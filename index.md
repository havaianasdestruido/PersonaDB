---
title: PersonaDB
description: Motor determinístico de geração de dados sintéticos e relacionais para personas fictícias brasileiras.
---

# PersonaDB

O **PersonaDB** é um motor determinístico de geração de dados sintéticos e relacionais para **personas fictícias brasileiras**, cobrindo **25 domínios** da vida humana (**257 tabelas** no PostgreSQL 16). Todos os registros são 100% fictícios e reproduzíveis a partir de uma única semente mestre (`SeededRNG` / PCG64 com derivação criptográfica `BLAKE2b`).

* * *

## Links rápidos

- 📚 **[Documentação completa](docs/)** — guias de instalação, arquitetura, motores matemáticos, catálogo dos geradores, referência de API de todos os módulos Python e dicionário das 257 tabelas.
- 💻 **[Código-fonte no GitHub](https://github.com/havaianasdestruido/PersonaDB)**
- 📄 **[README](https://github.com/havaianasdestruido/PersonaDB/blob/main/README.MD)** — visão geral, quick start e exemplos de consultas SQL.
- 🗺️ **[TODO / roteiro do projeto](TODO.html)**
- 🧬 **[PERSONA.MD — esquema conceitual](PERSONA.html)**
- 🚀 **[Análise hipotética de performance](rewrite.html)**

* * *

## Visão geral

- **257 tabelas relacionais** distribuídas em 25 domínios funcionais + metadados e junções N:N (`00_hub.sql` a `26_metadata.sql`).
- **7 motores matemáticos e probabilísticos** (`persona_db/engines/`): RNG determinístico, mobilidade social, genética, saúde, família, geografia e criminalidade.
- **24 geradores de domínio** (`persona_db/generators/`) orquestrados em ordem topológica estrita.
- **6 validadores de consistência** (`persona_db/validators/`): genealogia, temporal, finanças, saúde, jurídico-eleitoral e social.

## Quick start

```bash
# 1. Instalar pacote e dependências de desenvolvimento/Parquet
python3 -m pip install -e "persona_db[dev,parquet]"

# 2. Gerar um dataset sintético completo (257 tabelas) com validação automática
python3 -m persona_db.scripts.generate --personas 200 --seed 42 --output dataset.json --html-report report.html

# 3. Executar a suíte de validadores de consistência diretamente
python3 -m persona_db.validators.run_validators --personas 200 --seed 42

# 4. Rodar todos os testes (unitários, integração e estatísticos)
pytest persona_db/tests -v
```

Para o passo a passo completo, incluindo o fluxo com PostgreSQL via Docker Compose, consulte a **[documentação](docs/)**.
