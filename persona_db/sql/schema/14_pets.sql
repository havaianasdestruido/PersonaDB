-- ============================================================================
-- PersonaDB - 14_pets.sql (Domínio 14 - Pets & Animais)
-- ----------------------------------------------------------------------------
-- Hubs: pet, raca, veterinario, clinica_veterinaria.
-- Satélites: consulta_veterinaria, vacina_pet, adocao_pet,
-- pet_historico_dono.
-- ============================================================================

CREATE TABLE IF NOT EXISTS raca (
    id      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome    TEXT NOT NULL,
    especie TEXT CHECK (especie IN ('canina','felina','aves','roedores','peixes','repteis'))
);
COMMENT ON TABLE raca IS 'Raças de animais fictícias.';

CREATE TABLE IF NOT EXISTS pet (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id_dono    UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    nome              TEXT NOT NULL,
    raca_id           UUID NOT NULL REFERENCES raca(id) ON DELETE CASCADE,
    data_nascimento   DATE
);
COMMENT ON TABLE pet IS 'Animais de estimação da persona.';

CREATE TABLE IF NOT EXISTS veterinario (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome          TEXT NOT NULL,
    especialidade TEXT
);
COMMENT ON TABLE veterinario IS 'Veterinários fictícios.';

CREATE TABLE IF NOT EXISTS clinica_veterinaria (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome        TEXT NOT NULL,
    endereco_id UUID
);
COMMENT ON TABLE clinica_veterinaria IS 'Clínicas veterinárias fictícias.';

CREATE TABLE IF NOT EXISTS consulta_veterinaria (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pet_id        UUID NOT NULL REFERENCES pet(id) ON DELETE CASCADE,
    veterinario_id UUID NOT NULL REFERENCES veterinario(id) ON DELETE CASCADE,
    clinica_id    UUID NOT NULL REFERENCES clinica_veterinaria(id) ON DELETE CASCADE,
    data          DATE,
    motivo        TEXT
);
COMMENT ON TABLE consulta_veterinaria IS 'Consultas veterinárias do pet.';

CREATE TABLE IF NOT EXISTS vacina_pet (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pet_id        UUID NOT NULL REFERENCES pet(id) ON DELETE CASCADE,
    tipo_vacina   TEXT NOT NULL,
    data          DATE
);
COMMENT ON TABLE vacina_pet IS 'Vacinas aplicadas nos pets.';

CREATE TABLE IF NOT EXISTS adocao_pet (
    id                   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pet_id               UUID NOT NULL REFERENCES pet(id) ON DELETE CASCADE,
    pessoa_id_adotante   UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    data                 DATE,
    origem               TEXT CHECK (origem IN ('canil','resgate','loja','reatividade'))
);
COMMENT ON TABLE adocao_pet IS 'Adoções de animais.';

CREATE TABLE IF NOT EXISTS pet_historico_dono (
    id                    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pet_id                UUID NOT NULL REFERENCES pet(id) ON DELETE CASCADE,
    pessoa_id             UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    data_inicio           DATE,
    data_fim              DATE,
    motivo_transferencia  TEXT
);
COMMENT ON TABLE pet_historico_dono IS 'Tutores anteriores do pet.';