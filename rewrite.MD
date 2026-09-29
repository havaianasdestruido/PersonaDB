> **⚠️ NOTE / WARNING:** This document is a hypothetical architectural and performance analysis only. **It is NOT currently in the plan to implement these changes YET.** Do not refactor or rewrite the codebase based on this document unless explicitly scheduled.

---

For **this specific codebase (`PersonaDB`)** and the constraint **"without changing pretty much every line of code"**, here is how those four options actually play out against your architecture:

---

### TL;DR Verdict for `PersonaDB`

1. **Best near-zero-code-change runtime swap:** **GraalPy** (or **PyPy**) — *provided you make a ~40-line change in a single file (`persona_db/engines/rng.py`) to stop calling NumPy per scalar draw.*
2. **Best practical speedup without even switching runtimes (staying on CPython):** **Surgical fix in `rng.py` + `gen_02_genealogia.py` (~60 lines total across 2 files)** — gives a massive speedup (5x–20x+ at scale) because **NumPy is currently making this codebase *slower*, not faster.**
3. **Worst fit for "without changing every line of code":** **NumPy (Vectorization)** and **Cython**. Both would require rewriting almost every engine and generator from top to bottom.

---

### Why Each Option Behaves This Way in `PersonaDB`

#### 1. The Plot Twist: You Are Already Using `NumPy`, and It Is Currently Slowing You Down
Look at `persona_db/engines/rng.py` (`SeededRNG`):
* Every persona in `gen_00_pessoa.py`, `gen_01_identidade.py`, `gen_02_genealogia.py`, and `gen_03_saude.py` calls `master.fork(...)`, which instantiates a brand-new `np.random.default_rng()` object **multiple times per person**.
* Every call to `rng.choice(options, weights)` (used dozens of times per persona for names, cities, social classes, blood types, eye/hair color, diseases, etc.) executes:
  ```python
  w = np.asarray(weights, dtype=np.float64)
  w = w / s
  return self._rng.choice(options, p=w)
  ```
* When `options` is a Python `list` of strings or `dict`s (for example, `GeographyEngine.city_for_class` in `persona_db/engines/geography.py` passes `CITY_SET`, a list of **50 dictionaries**, into `self._rng.choice(CITY_SET, weights=weights)`), NumPy has to convert/box the Python sequence and weights into C arrays **just to pick 1 single element**, then unbox it back to Python.
* Similarly, `SocioeconomicEngine.education_level` (`persona_db/engines/socio.py`) allocates a 4-element `np.array` on every single person just to compute a 4-item softmax.

**Why full NumPy vectorization violates your constraint:**
* To get NumPy's real **10x–100x vectorized speed**, you would have to abandon `build_persona(idx, rng, ...)` returning a `dict` per person and rewrite every engine and generator to operate on **columnar arrays of $N$ people at once** (Struct-of-Arrays instead of Array-of-Structs).
* That would mean rewriting virtually every line of `gen_00` through `gen_03` and all 6 engines, and it would break your per-persona `master.fork(persona_id, domain)` determinism contract.

---

#### 2. `GraalPy` — The Winner for "Zero/Minimal Code Changes", With One Catch
Your workload in `PersonaDB` is almost entirely:
* Pure Python `for` loops over `personas` (`list[dict[str, Any]]`)
* Dictionary creation, string formatting, `uuid5`, `hashlib`, and `datetime.date` math
* Branch-heavy probabilistic rules (`CriminalEngine`, `GeneticEngine`, `HealthEngine`, `FamilyEngine`)

This is textbook **JIT compiler territory** (GraalPy / PyPy), **except for one catch**:
* As noted in your comparison, **GraalPy pays a heavy penalty when crossing the boundary into C extensions (like `numpy`) inside tight loops.**
* Because `SeededRNG` (`persona_db/engines/rng.py`) is the **single gateway** for all randomness across the entire project (*"Every engine MUST use SeededRNG"*), you only have to touch **`persona_db/engines/rng.py`** (and 4 lines in `socio.py`) to replace `np.random.default_rng` with Python's standard `random.Random` + `math`.
* Once `rng.py` is pure Python, **the entire generation pipeline is 100% pure Python**, and GraalPy's JIT can inline and compile the loops across `gen_00`–`gen_03` and all engines without changing a single line of generator or engine logic.

---

#### 3. `Cython` — Why It Doesn't Fit Your Constraint
* **Without rewriting code:** Cython can compile unmodified `.py` files ("pure Python mode"), but because `PersonaDB` passes dynamic `dict[str, Any]` objects (`persona["classe_social"]`, `rows["doenca_pessoa"].append({...})`) and Python strings everywhere, compiling `.py` files with Cython without `cdef` structs/types only yields ~15%–30% speedup (it just removes Python bytecode dispatch while keeping all CPython `PyObject*` dictionary lookups and boxing).
* **To get Cython's 50x–3,000x speedup:** You would have to replace all persona `dict`s with `cdef struct` / `cdef class` types, replace string enums with C `enum` ints, and add static C types to every variable in every engine and generator — which means rewriting the entire codebase in `.pyx`.

---

#### 4. `CPython` — The Hidden Gem (Fixing the 2 Real Bottlenecks in <60 Lines)
Even if you stay on standard **CPython** and don't switch to GraalPy, you can get an order-of-magnitude speedup by fixing just **two localized bottlenecks** without touching the rest of the codebase:

1. **Replace NumPy scalar draws in `persona_db/engines/rng.py` (~40 lines):**
   * Use Python's `random.Random(seed_int)` (which is implemented in C in CPython and has zero array-allocation overhead for scalar draws) and `random.choices(options, weights=weights, k=1)[0]` (or `itertools.accumulate` + `bisect`).
   * For single-item weighted draws over small lists of strings/dicts, `random.Random` is **10x–30x faster** than `np.random.Generator.choice` because it doesn't construct a NumPy array out of `options` and `weights` on every call.
2. **Fix the $O(N^2)$ scans in `persona_db/generators/gen_02_genealogia.py` (~20 lines):**
   * In `_parents()` / `_pick_parent()` (`gen_02_genealogia.py:157-182`), for **every** person, it scans the entire `pool` of $N$ personas *and* calls `date.fromisoformat(p["data_nascimento"])` inside the inner loop ($O(N^2)$ date parses).
   * In `_heranca()` and `_doacoes()` (`gen_02_genealogia.py:258, 294`), for every deceased/donor persona, it scans all personas again to find matching `familia_id` ($O(N^2)$).
   * Pre-parsing birth dates once and grouping `personas` by `familia_id` in a `dict` turns those from $O(N^2)$ into $O(N)$ while keeping the exact same output.

---

### Summary Comparison for `PersonaDB`

| Path | Code Changes in `PersonaDB` | Expected Real-World Impact on `PersonaDB` | Verdict |
| :--- | :--- | :--- | :--- |
| **GraalPy** *(as-is, keeping NumPy in `rng.py`)* | **0 lines** | Modest or even slower due to C-extension boundary calls into `numpy.random` thousands of times per persona | Held back by `rng.py` |
| **GraalPy** *(after swapping `rng.py` to pure-Python `random.Random`)* | **~45 lines** (only in `rng.py` & `socio.py`) | **Very High (5x–25x+)** — JIT compiles all pure-Python dict/loop logic across engines & generators | **Best runtime choice** |
| **CPython** *(swapping `rng.py` to `random.Random` + indexing `gen_02`)* | **~60 lines** (in `rng.py` & `gen_02_genealogia.py`) | **High (5x–20x+ at $N \ge 10\text{k}$)** — eliminates per-call NumPy array creation and $O(N^2)$ family scans | **Best pragmatic fix on standard Python** |
| **NumPy** *(full vectorization)* | **~90% of codebase** | **10x–100x**, but requires rewriting all engines/generators from per-person dicts to columnar arrays | Violates constraint |
| **Cython** | **~80% of codebase** (to get real speed) | **1.2x** without `cdef` types; **50x+** only if you rewrite all dicts/strings into C structs | Violates constraint |
