# Mathematical models

PersonaDB uses deterministic pseudo-random streams: every domain forks a stream
from the master seed and persona identifier. This permits a domain to be rerun
without changing unrelated records.

The engines implement simplified, explicitly synthetic versions of: categorical
social mobility, Mendelian ABO/Rh inheritance, logistic handedness and criminal
risk models, age-dependent health hazards, household/fertility distributions,
and gravity-inspired geographic mobility. Parameters are calibration defaults,
not claims about real people or populations. Recalibrate constants in
`engines/constants.py` and `seeds/probability_tables.py`, then run the test suite
and distribution checks before publishing a dataset.
