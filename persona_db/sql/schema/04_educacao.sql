-- ============================================================================
-- PersonaDB - 04_educacao.sql (Domínio 04 - Educação)
-- ----------------------------------------------------------------------------
-- Hubs: instituicao_ensino, curso, disciplina, professor.
-- Satélites: matricula, nota, frequencia, bolsa, certificado, diploma,
-- reprovacao, estagio, biblioteca_emprestimo, turma.
-- FK cruzada: estagio.empresa_id -> empresa(id) é resolvida em 05_carreira.sql.
-- ============================================================================

CREATE TABLE IF NOT EXISTS instituicao_ensino (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome         TEXT NOT NULL,
    tipo         TEXT CHECK (tipo IN ('escola','colegio','faculdade','universidade','tecnico')),
    endereco_id  UUID
);
COMMENT ON TABLE instituicao_ensino IS 'Instituições de ensino fictícias.';

CREATE TABLE IF NOT EXISTS curso (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome          TEXT NOT NULL,
    nivel         TEXT CHECK (nivel IN ('infantil','fundamental','medio','tecnico','superior','pos')),
    duracao_anos  INTEGER
);
COMMENT ON TABLE curso IS 'Cursos oferecidos (nível igual ao usado pelos engines).';
COMMENT ON COLUMN curso.duracao_anos IS 'Duração do curso em anos.';

CREATE TABLE IF NOT EXISTS disciplina (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome          TEXT NOT NULL,
    curso_id      UUID NOT NULL REFERENCES curso(id) ON DELETE CASCADE,
    carga_horaria INTEGER
);
COMMENT ON TABLE disciplina IS 'Disciplinas vinculadas a cursos.';

CREATE TABLE IF NOT EXISTS professor (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome             TEXT NOT NULL,
    instituicao_id   UUID NOT NULL REFERENCES instituicao_ensino(id) ON DELETE CASCADE,
    especialidade    TEXT
);
COMMENT ON TABLE professor IS 'Professores fictícios.';

CREATE TABLE IF NOT EXISTS turma (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    disciplina_id UUID NOT NULL REFERENCES disciplina(id) ON DELETE CASCADE,
    professor_id  UUID NOT NULL REFERENCES professor(id) ON DELETE CASCADE,
    periodo       TEXT
);
COMMENT ON TABLE turma IS 'Turmas de uma disciplina com professor.';

CREATE TABLE IF NOT EXISTS matricula (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id       UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    instituicao_id  UUID NOT NULL REFERENCES instituicao_ensino(id) ON DELETE CASCADE,
    curso_id        UUID NOT NULL REFERENCES curso(id) ON DELETE CASCADE,
    data_inicio     DATE,
    data_fim        DATE,
    status          TEXT CHECK (status IN ('ativa','concluida','trancada','abandonada'))
);
COMMENT ON TABLE matricula IS 'Matrículas da persona em instituições.';

CREATE TABLE IF NOT EXISTS nota (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    disciplina_id  UUID NOT NULL REFERENCES disciplina(id) ON DELETE CASCADE,
    periodo        TEXT,
    valor          NUMERIC(4,2) CHECK (valor BETWEEN 0 AND 10)
);
COMMENT ON TABLE nota IS 'Notas escolares por disciplina/periodo.';

CREATE TABLE IF NOT EXISTS frequencia_escolar (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id           UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    disciplina_id       UUID NOT NULL REFERENCES disciplina(id) ON DELETE CASCADE,
    periodo             TEXT,
    percentual_presenca NUMERIC(5,2) CHECK (percentual_presenca BETWEEN 0 AND 100)
);
COMMENT ON TABLE frequencia_escolar IS 'Frequência escolar da persona.';

CREATE TABLE IF NOT EXISTS bolsa_estudo (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    instituicao_id UUID NOT NULL REFERENCES instituicao_ensino(id) ON DELETE CASCADE,
    tipo           TEXT,
    percentual     NUMERIC(5,2) CHECK (percentual BETWEEN 0 AND 100),
    periodo        TEXT
);
COMMENT ON TABLE bolsa_estudo IS 'Bolsas de estudo concedidas.';

CREATE TABLE IF NOT EXISTS certificado (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id    UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    curso_id     UUID NOT NULL REFERENCES curso(id) ON DELETE CASCADE,
    data_emissao DATE
);
COMMENT ON TABLE certificado IS 'Certificados de conclusão de curso.';

CREATE TABLE IF NOT EXISTS diploma (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id       UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    curso_id        UUID NOT NULL REFERENCES curso(id) ON DELETE CASCADE,
    data_conclusao  DATE,
    instituicao_id  UUID NOT NULL REFERENCES instituicao_ensino(id) ON DELETE CASCADE
);
COMMENT ON TABLE diploma IS 'Diplomas de graduação/pós-graduação.';

CREATE TABLE IF NOT EXISTS reprovacao (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    disciplina_id  UUID NOT NULL REFERENCES disciplina(id) ON DELETE CASCADE,
    periodo        TEXT,
    motivo         TEXT
);
COMMENT ON TABLE reprovacao IS 'Reprovações escolares.';

CREATE TABLE IF NOT EXISTS estagio (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    empresa_id     UUID,
    curso_id       UUID NOT NULL REFERENCES curso(id) ON DELETE CASCADE,
    data_inicio    DATE,
    data_fim       DATE
);
COMMENT ON TABLE estagio IS 'Estágios cursados (FK empresa resolvida em 05).';

CREATE TABLE IF NOT EXISTS biblioteca_emprestimo (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id        UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    instituicao_id   UUID NOT NULL REFERENCES instituicao_ensino(id) ON DELETE CASCADE,
    titulo_obra      TEXT,
    data_emprestimo  DATE,
    data_devolucao   DATE
);
COMMENT ON TABLE biblioteca_emprestimo IS 'Empréstimos de obras na biblioteca da instituição.';