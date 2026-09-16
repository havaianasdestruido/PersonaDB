🌌 Mega-Schema de Personas Fictícias
====================================

Esqueleto relacional colossal para geração de dados sintéticos de indivíduos fictícios. **~256 tabelas** em **25 domínios**, todas amarradas por `pessoa_id` (chave central) e por chaves de domínio cruzado (`empresa_id`, `familia_id`, `imovel_id`, `processo_id`, `eleicao_id`, `evento_id`, etc).

Convenção: toda tabela satélite tem `id` (PK) + `pessoa_id` (FK → `pessoa.id`), salvo indicação contrária. Tabelas de junção têm PK composta.

* * *

00\. Hub central
----------------

*   **pessoa** (PK: `id`) — nome\_completo, data\_nascimento, local\_nascimento, sexo, nacionalidade, estado\_civil, data\_criacao\_registro

* * *

01\. Identidade & Biometria
---------------------------

*   **pessoa\_nome\_anterior** — nome\_antigo, motivo\_mudanca, data\_mudanca
*   **pessoa\_apelido** — apelido, origem, contexto\_uso
*   **pessoa\_documento** — tipo (RG/CPF/passaporte/CNH/título de eleitor fictícios), numero\_ficticio, orgao\_emissor, validade
*   **pessoa\_biometria** — impressao\_digital\_ficticia, padrao\_iris\_ficticio, hash\_facial\_ficticio
*   **pessoa\_foto** — url\_ficticia, data, contexto
*   **pessoa\_assinatura** — modelo\_assinatura, data\_registro
*   **pessoa\_caracteristica\_fisica** — altura, peso, cor\_olhos, cor\_cabelo, mao\_dominante, tipo\_sanguineo, fator\_rh
*   **pessoa\_marca\_distintiva** — tipo (tatuagem/cicatriz/sinal), localizacao\_corporal, descricao, data\_aquisicao
*   **pessoa\_idioma** — idioma, nivel\_fluencia, forma\_aprendizado

* * *

02\. Genealogia & Herança
-------------------------

*   **familia** (PK: `id`) — sobrenome\_familiar, origem\_ficticia
*   **membro\_familia** — pessoa\_id, familia\_id, papel\_familiar
*   **parentesco** — pessoa\_id\_a, pessoa\_id\_b, tipo\_parentesco, grau
*   **arvore\_genealogica** — pessoa\_id, geracao, ramo (paterno/materno)
*   **heranca** — pessoa\_id\_herdeiro, pessoa\_id\_falecido, data, origem
*   **heranca\_item** — heranca\_id, tipo\_bem, valor\_estimado, descricao
*   **doacao\_familiar** — pessoa\_id\_doador, pessoa\_id\_receptor, item, data, motivo
*   **condicao\_genetica** — nome\_condicao\_ficticia, linha\_familiar (paterna/materna), percentual\_manifestacao
*   **predisposicao\_genetica** — pessoa\_id, condicao\_id, grau\_predisposicao
*   **ancestralidade\_ficticia** — pessoa\_id, origem\_percentual, regiao\_ficticia

* * *

03\. Saúde
----------

*   **doenca** (PK: `id`) — nome, categoria, gravidade\_padrao
*   **doenca\_pessoa** — pessoa\_id, doenca\_id, data\_diagnostico, estagio, status (ativa/remissão/curada)
*   **sintoma** (PK: `id`) — nome, categoria
*   **sintoma\_ocorrencia** — pessoa\_id, sintoma\_id, data\_inicio, intensidade
*   **exame** — pessoa\_id, tipo\_exame, data, local
*   **exame\_resultado** — exame\_id, parametro, valor, referencia
*   **tratamento** — pessoa\_id, doenca\_pessoa\_id, tipo, data\_inicio, data\_fim
*   **medicamento** (PK: `id`) — nome\_ficticio, principio\_ativo\_ficticio
*   **prescricao** — pessoa\_id, medicamento\_id, medico\_id, data
*   **dosagem** — prescricao\_id, quantidade, unidade, frequencia
*   **cirurgia** — pessoa\_id, tipo, data, cirurgiao\_id, hospital\_id
*   **cirurgiao** (PK: `id`) — nome, especialidade
*   **hospital** (PK: `id`) — nome, endereco\_id, tipo
*   **internacao** — pessoa\_id, hospital\_id, leito\_id, data\_entrada, data\_saida, motivo
*   **leito** (PK: `id`) — hospital\_id, numero, ala
*   **alta\_hospitalar** — internacao\_id, data, condicao\_saida
*   **vacina** (PK: `id`) — nome, tipo
*   **vacina\_dose** — pessoa\_id, vacina\_id, data, dose\_numero, local\_aplicacao
*   **alergia** — pessoa\_id, substancia, gravidade
*   **alergia\_reacao** — alergia\_id, sintoma\_id, tratamento\_aplicado
*   **condicao\_cronica** — pessoa\_id, nome, data\_diagnostico, controle\_atual
*   **saude\_mental\_registro** — pessoa\_id, condicao\_ficticia, data\_inicio, status
*   **terapia** — pessoa\_id, tipo, terapeuta\_id, data\_inicio
*   **sessao\_terapia** — terapia\_id, data, duracao, notas\_ficticias
*   **seguro\_saude** — pessoa\_id, plano\_id, data\_contratacao
*   **plano\_saude** (PK: `id`) — operadora, cobertura, mensalidade
*   **convenio** (PK: `id`) — nome, hospitais\_conveniados

* * *

04\. Educação
-------------

*   **instituicao\_ensino** (PK: `id`) — nome, tipo, endereco\_id
*   **matricula** — pessoa\_id, instituicao\_id, curso\_id, data\_inicio, data\_fim, status
*   **curso** (PK: `id`) — nome, nivel, duracao
*   **disciplina** (PK: `id`) — nome, curso\_id, carga\_horaria
*   **turma** — disciplina\_id, professor\_id, periodo
*   **professor** (PK: `id`) — nome, instituicao\_id, especialidade
*   **nota** — pessoa\_id, disciplina\_id, periodo, valor
*   **frequencia\_escolar** — pessoa\_id, disciplina\_id, periodo, percentual\_presenca
*   **bolsa\_estudo** — pessoa\_id, instituicao\_id, tipo, percentual, periodo
*   **certificado** — pessoa\_id, curso\_id, data\_emissao
*   **diploma** — pessoa\_id, curso\_id, data\_conclusao, instituicao\_id
*   **reprovacao** — pessoa\_id, disciplina\_id, periodo, motivo
*   **estagio** — pessoa\_id, empresa\_id, curso\_id, data\_inicio, data\_fim
*   **biblioteca\_emprestimo** — pessoa\_id, instituicao\_id, titulo\_obra, data\_emprestimo, data\_devolucao

* * *

05\. Carreira & Trabalho
------------------------

*   **empresa** (PK: `id`) — nome, cnpj\_ficticio, ramo\_atividade, endereco\_id
*   **cargo** (PK: `id`) — nome, nivel\_hierarquico
*   **contrato\_trabalho** — pessoa\_id, empresa\_id, cargo\_id, tipo\_contrato, data\_inicio, data\_fim
*   **historico\_emprego** — pessoa\_id, empresa\_id, cargo\_id, inicio, fim, motivo\_saida
*   **salario** — contrato\_id, valor, data\_vigencia
*   **holerite** — contrato\_id, mes\_referencia, valor\_liquido, descontos
*   **beneficio** — contrato\_id, tipo, valor
*   **avaliacao\_desempenho** — pessoa\_id, empresa\_id, periodo, nota, feedback\_ficticio
*   **promocao** — pessoa\_id, empresa\_id, cargo\_anterior\_id, cargo\_novo\_id, data
*   **demissao** — contrato\_id, data, motivo, tipo (justa causa/sem justa causa/pedido)
*   **ferias** — contrato\_id, data\_inicio, data\_fim, dias
*   **licenca\_trabalho** — pessoa\_id, empresa\_id, tipo, data\_inicio, data\_fim
*   **habilidade\_profissional** — pessoa\_id, nome\_habilidade, nivel
*   **certificacao\_profissional** — pessoa\_id, nome, orgao\_emissor, validade
*   **sindicato\_ficticio** — pessoa\_id, nome\_sindicato, categoria
*   **colega\_trabalho** — pessoa\_id\_a, pessoa\_id\_b, empresa\_id, periodo

* * *

06\. Patrimônio & Finanças
--------------------------

*   **conta\_bancaria** — pessoa\_id, banco\_id, tipo\_conta, agencia, numero\_ficticio
*   **banco** (PK: `id`) — nome, codigo\_ficticio
*   **cartao\_credito** — pessoa\_id, conta\_id, bandeira, limite
*   **transacao** — conta\_id, tipo (débito/crédito/pix), valor, data, descricao
*   **fatura** — cartao\_id, mes\_referencia, valor\_total, status\_pagamento
*   **investimento** — pessoa\_id, tipo, valor\_aplicado, data, corretora\_id
*   **carteira\_investimento** — pessoa\_id, valor\_total, data\_snapshot
*   **corretora** (PK: `id`) — nome, tipo
*   **imovel** (PK: `id`) — endereco\_id, tipo, valor\_estimado, proprietario\_pessoa\_id
*   **imovel\_historico** — imovel\_id, evento (compra/venda/reforma), data, valor
*   **veiculo** (PK: `id`) — modelo, ano, placa\_ficticia, proprietario\_pessoa\_id
*   **veiculo\_historico** — veiculo\_id, evento (compra/venda/acidente/manutenção), data, valor
*   **divida** — pessoa\_id, credor, valor, data\_vencimento, status
*   **financiamento** — pessoa\_id, tipo (imóvel/veículo/pessoal), valor\_total, parcelas, taxa\_juros
*   **seguro** — pessoa\_id, tipo (vida/residencial/veicular), seguradora, valor\_cobertura
*   **patrimonio\_snapshot** — pessoa\_id, data, valor\_total\_estimado
*   **imposto** — pessoa\_id, tipo, ano\_referencia, valor
*   **declaracao\_imposto** — pessoa\_id, ano, status, valor\_restituicao\_ou\_debito

* * *

07\. Residência
---------------

*   **endereco** (PK: `id`) — logradouro\_ficticio, numero, bairro, cidade\_ficticia, cep\_ficticio
*   **residencia** — pessoa\_id, endereco\_id, tipo\_posse (próprio/alugado), data\_entrada
*   **historico\_residencia** — pessoa\_id, endereco\_id, data\_entrada, data\_saida, motivo\_mudanca
*   **condominio** (PK: `id`) — nome, endereco\_id, numero\_unidades
*   **taxa\_condominio** — residencia\_id, mes\_referencia, valor
*   **vizinho** — pessoa\_id\_a, pessoa\_id\_b, endereco\_id, periodo\_convivencia
*   **contrato\_aluguel** — pessoa\_id, imovel\_id, valor\_mensal, data\_inicio, data\_fim
*   **financiamento\_imobiliario** — pessoa\_id, imovel\_id, financiamento\_id

* * *

08\. Relacionamentos & Família nuclear
--------------------------------------

*   **relacionamento** — pessoa\_id\_a, pessoa\_id\_b, tipo, data\_inicio, data\_fim, status
*   **namoro** — relacionamento\_id, motivo\_termino
*   **casamento** — pessoa\_id\_a, pessoa\_id\_b, data, regime\_bens
*   **divorcio** — casamento\_id, data, motivo\_ficticio
*   **uniao\_estavel** — pessoa\_id\_a, pessoa\_id\_b, data\_inicio, data\_reconhecimento
*   **filho** — pessoa\_id\_pai, pessoa\_id\_mae, pessoa\_id\_filho, data\_nascimento
*   **guarda\_compartilhada** — filho\_id, responsavel\_pessoa\_id, percentual\_tempo
*   **pensao\_alimenticia** — pessoa\_id\_pagador, pessoa\_id\_beneficiario, valor\_mensal, data\_inicio
*   **adocao\_ficticia** — pessoa\_id\_adotante, pessoa\_id\_adotado, data
*   **padrinho\_madrinha** — pessoa\_id\_afilhado, pessoa\_id\_padrinho, tipo (batismo/casamento)

* * *

09\. Rede Social
----------------

*   **amizade** — pessoa\_id\_a, pessoa\_id\_b, data\_inicio, contexto\_conhecimento
*   **grupo\_social** (PK: `id`) — nome, tipo, data\_criacao
*   **membro\_grupo\_social** — pessoa\_id, grupo\_id, data\_entrada, papel
*   **evento\_social** (PK: `id`) — nome, data, local\_endereco\_id
*   **participacao\_evento\_social** — pessoa\_id, evento\_id, papel (convidado/organizador)
*   **contato\_pessoal** — pessoa\_id, pessoa\_id\_contato, frequencia\_contato, tipo\_vinculo
*   **inimizade\_ficticia** — pessoa\_id\_a, pessoa\_id\_b, motivo, data\_inicio
*   **clube** (PK: `id`) — nome, categoria

* * *

10\. Vida Digital
-----------------

*   **dispositivo** (PK: `id`) — pessoa\_id, tipo, modelo, sistema\_operacional, data\_aquisicao
*   **conta\_digital** — pessoa\_id, plataforma, username\_ficticio, data\_criacao
*   **perfil\_rede\_social** — conta\_digital\_id, seguidores\_ficticios, bio\_ficticia
*   **publicacao\_rede\_social** — perfil\_id, data, tipo\_conteudo, engajamento\_ficticio
*   **historico\_navegacao\_ficticio** — dispositivo\_id, dominio\_visitado, data, duracao
*   **jogo** (PK: `id`) — nome, plataforma, genero
*   **progresso\_jogo** — pessoa\_id, jogo\_id, horas\_jogadas, nivel\_atual, data\_ultima\_sessao
*   **assinatura\_streaming** — pessoa\_id, servico, plano, data\_inicio, valor\_mensal
*   **senha\_registro\_ficticio** — conta\_digital\_id, data\_ultima\_troca, forca\_senha
*   **dispositivo\_troca\_historico** — pessoa\_id, dispositivo\_antigo\_id, dispositivo\_novo\_id, data, motivo
*   **app\_instalado** — dispositivo\_id, nome\_app, data\_instalacao, categoria
*   **provedor\_internet** — residencia\_id, operadora, velocidade\_contratada

* * *

11\. Jurídico
-------------

*   **processo** (PK: `id`) — numero\_ficticio, tipo, tribunal\_id, status
*   **pessoa\_processo** — pessoa\_id, processo\_id, papel (réu/autor/testemunha)
*   **ocorrencia\_policial** — pessoa\_id, tipo, data, local\_endereco\_id
*   **boletim\_ocorrencia** — ocorrencia\_id, numero\_ficticio, delegacia
*   **julgamento** — processo\_id, data, resultado
*   **sentenca** — julgamento\_id, tipo, descricao
*   **pena** — sentenca\_id, tipo (multa/prisão/prestação de serviço), duracao\_ou\_valor
*   **antecedente\_criminal** — pessoa\_id, processo\_id, status (ativo/arquivado)
*   **advogado** (PK: `id`) — nome, oab\_ficticia
*   **processo\_advogado** — processo\_id, advogado\_id, parte\_representada
*   **tribunal** (PK: `id`) — nome\_ficticio, jurisdicao
*   **multa** — pessoa\_id, tipo, valor, data, status\_pagamento
*   **contrato\_juridico** — pessoa\_id\_a, pessoa\_id\_b, tipo, data, objeto

* * *

12\. Eleitoral & Política
-------------------------

*   **eleicao** (PK: `id`) — ano, tipo, municipio\_ficticio
*   **candidato** — pessoa\_id, eleicao\_id, partido\_id, cargo\_pretendido
*   **voto** — pessoa\_id, eleicao\_id, candidato\_id\_escolhido (ou branco/nulo)
*   **partido** (PK: `id`) — nome\_ficticio, sigla\_ficticia
*   **filiacao\_partidaria** — pessoa\_id, partido\_id, data\_filiacao, data\_desfiliacao
*   **cargo\_publico** — pessoa\_id, nome\_cargo, orgao, data\_inicio, data\_fim
*   **doacao\_campanha\_ficticia** — pessoa\_id\_doador, candidato\_id, valor, data
*   **comparecimento\_eleitoral** — pessoa\_id, eleicao\_id, compareceu, justificativa\_ausencia

* * *

13\. Viagens
------------

*   **viagem** (PK: `id`) — pessoa\_id, destino\_id, data\_ida, data\_volta, motivo
*   **destino** (PK: `id`) — cidade\_ficticia, pais\_ficticio
*   **hospedagem** — viagem\_id, tipo, nome\_estabelecimento, custo
*   **transporte\_viagem** — viagem\_id, tipo (aéreo/rodoviário/marítimo), companhia
*   **passagem** — transporte\_id, numero\_ficticio, classe, valor
*   **documento\_viagem** — pessoa\_id, tipo (visto/passaporte), validade
*   **bagagem** — viagem\_id, tipo, peso, extraviada (sim/não)
*   **seguro\_viagem** — viagem\_id, seguradora, cobertura
*   **roteiro\_viagem** — viagem\_id, dia, atividade\_planejada
*   **companhia\_viagem** — viagem\_id, pessoa\_id\_acompanhante

* * *

14\. Pets & Animais
-------------------

*   **pet** (PK: `id`) — pessoa\_id\_dono, nome, raca\_id, data\_nascimento
*   **raca** (PK: `id`) — nome, especie
*   **veterinario** (PK: `id`) — nome, especialidade
*   **clinica\_veterinaria** (PK: `id`) — nome, endereco\_id
*   **consulta\_veterinaria** — pet\_id, veterinario\_id, clinica\_id, data, motivo
*   **vacina\_pet** — pet\_id, tipo\_vacina, data
*   **adocao\_pet** — pet\_id, pessoa\_id\_adotante, data, origem (canil/resgate/loja)
*   **pet\_historico\_dono** — pet\_id, pessoa\_id, data\_inicio, data\_fim, motivo\_transferencia

* * *

15\. Consumo
------------

*   **compra** — pessoa\_id, loja\_id, data, valor\_total
*   **item\_compra** — compra\_id, produto\_id, quantidade, valor\_unitario
*   **produto** (PK: `id`) — nome, categoria, marca\_ficticia
*   **loja** (PK: `id`) — nome, tipo (física/online), endereco\_id
*   **avaliacao\_produto** — pessoa\_id, produto\_id, nota, comentario\_ficticio
*   **assinatura\_servico** — pessoa\_id, servico, valor\_mensal, data\_inicio
*   **devolucao** — compra\_id, produto\_id, motivo, data
*   **programa\_fidelidade** — pessoa\_id, loja\_id, pontos\_acumulados
*   **carrinho\_abandonado** — pessoa\_id, loja\_id, itens\_ficticios, data
*   **historico\_preco** — produto\_id, data, valor

* * *

16\. Timeline & Eventos de Vida
-------------------------------

*   **evento\_vida** — pessoa\_id, data, tipo\_evento, descricao
*   **marco\_historico\_pessoal** — pessoa\_id, evento\_vida\_id, importancia (1-10)
*   **linha\_do\_tempo** — pessoa\_id, evento\_vida\_id, ordem\_cronologica
*   **aniversario** — pessoa\_id, tipo (nascimento/casamento/emprego), data
*   **comemoracao** — pessoa\_id, evento\_vida\_id, local\_endereco\_id, convidados\_ficticios
*   **luto\_ficticio** — pessoa\_id, pessoa\_id\_falecido, data, relacao

* * *

17\. Comportamento & Personalidade
----------------------------------

*   **traco\_personalidade** — pessoa\_id, nome\_traco, intensidade
*   **habito** — pessoa\_id, descricao, frequencia
*   **rotina\_diaria** — pessoa\_id, horario, atividade
*   **preferencia** — pessoa\_id, categoria, item\_preferido
*   **aversao** — pessoa\_id, categoria, item\_evitado
*   **habilidade** — pessoa\_id, nome, nivel
*   **talento** — pessoa\_id, area, nivel\_ficticio
*   **medo\_ficticio** — pessoa\_id, descricao, origem
*   **sonho\_ficticio** — pessoa\_id, descricao, status (realizado/em curso/abandonado)
*   **estilo\_aprendizagem** — pessoa\_id, tipo (visual/auditivo/cinestésico)

* * *

18\. Religião & Crenças
-----------------------

*   **crenca** — pessoa\_id, nome\_ficticio, intensidade
*   **instituicao\_religiosa** (PK: `id`) — nome, endereco\_id
*   **participacao\_religiosa** — pessoa\_id, instituicao\_id, frequencia, papel
*   **ritual\_ficticio** — pessoa\_id, nome, data
*   **conversao\_religiosa** — pessoa\_id, crenca\_anterior\_id, crenca\_nova\_id, data
*   **dizimo\_ficticio** — pessoa\_id, instituicao\_id, valor, periodicidade

* * *

19\. Esporte & Lazer
--------------------

*   **esporte\_praticado** — pessoa\_id, nome\_esporte, nivel, frequencia
*   **clube\_esportivo** (PK: `id`) — nome, modalidade
*   **membro\_clube\_esportivo** — pessoa\_id, clube\_id, data\_entrada
*   **competicao** (PK: `id`) — nome, modalidade, data
*   **resultado\_competicao** — pessoa\_id, competicao\_id, colocacao
*   **equipamento\_esportivo** — pessoa\_id, tipo, marca\_ficticia, data\_aquisicao
*   **hobby** — pessoa\_id, nome, frequencia
*   **colecao\_ficticia** — pessoa\_id, tema, quantidade\_itens

* * *

20\. Militar & Serviço
----------------------

*   **servico\_militar** — pessoa\_id, data\_inicio, data\_fim, ramo
*   **patente** — servico\_militar\_id, nome\_patente, data\_promocao
*   **unidade\_militar** (PK: `id`) — nome, localizacao\_ficticia
*   **convocacao** — pessoa\_id, data, motivo, resultado (dispensado/incorporado)
*   **baixa\_militar** — servico\_militar\_id, data, motivo
*   **condecoracao\_ficticia** — pessoa\_id, nome, data

* * *

21\. Imigração & Documentos (fictícios)
---------------------------------------

*   **documento\_identidade** — pessoa\_id, tipo, pais\_emissor\_ficticio, validade
*   **visto\_ficticio** — pessoa\_id, pais\_destino\_ficticio, tipo, validade
*   **naturalizacao\_ficticia** — pessoa\_id, pais\_origem, pais\_destino, data
*   **residencia\_permanente\_ficticia** — pessoa\_id, pais, data\_concessao
*   **deportacao\_ficticia** — pessoa\_id, pais, data, motivo
*   **fronteira\_travessia\_ficticia** — pessoa\_id, ponto\_fronteira, data, direcao

* * *

22\. Comunicação
----------------

*   **telefone** — pessoa\_id, numero\_ficticio, tipo (fixo/celular)
*   **email** — pessoa\_id, endereco\_ficticio, provedor
*   **correspondencia** — pessoa\_id\_remetente, pessoa\_id\_destinatario, tipo, data
*   **ligacao\_registro** — pessoa\_id\_a, pessoa\_id\_b, data, duracao
*   **mensagem\_registro** — pessoa\_id\_a, pessoa\_id\_b, plataforma, data

* * *

23\. Mídia & Reputação
----------------------

*   **noticia\_ficticia** — pessoa\_id, titulo, veiculo\_ficticio, data
*   **mencao\_midia** — pessoa\_id, noticia\_id, contexto (positivo/negativo/neutro)
*   **reputacao\_score** — pessoa\_id, data, valor\_score
*   **premio\_ficticio** — pessoa\_id, nome, categoria, data
*   **entrevista\_ficticia** — pessoa\_id, veiculo\_ficticio, data, tema

* * *

24\. Meta & Sistema (controle do próprio banco)
-----------------------------------------------

*   **fonte\_dado** — tabela\_origem, metodo\_geracao, data\_geracao
*   **versao\_registro** — tabela, registro\_id, numero\_versao, data
*   **log\_alteracao** — tabela, registro\_id, campo\_alterado, valor\_antigo, valor\_novo, data
*   **auditoria** — usuario\_sistema, acao, tabela\_afetada, data
*   **regra\_geracao** — dominio, parametro, valor\_padrao
*   **semente\_aleatoria** — pessoa\_id, seed\_valor
*   **validacao\_consistencia** — tabela, regra\_violada, registro\_id, data
*   **exportacao\_dataset** — data, formato, tabelas\_incluidas, destino

* * *

25\. Tabelas de junção N:N explícitas
-------------------------------------

*   **pessoa\_habilidade** — pessoa\_id, habilidade\_id, nivel
*   **pessoa\_idioma\_nivel** — pessoa\_id, idioma\_id, nivel\_leitura, nivel\_fala
*   **pessoa\_hobby** — pessoa\_id, hobby\_id, desde\_quando
*   **pessoa\_grupo\_social** — pessoa\_id, grupo\_id, papel
*   **pessoa\_evento** — pessoa\_id, evento\_id, papel
*   **pessoa\_doenca\_familiar** — pessoa\_id, condicao\_genetica\_id, grau\_risco
*   **pessoa\_pet** — pessoa\_id, pet\_id, tipo\_vinculo (dono/cuidador)
*   **pessoa\_veiculo** — pessoa\_id, veiculo\_id, tipo\_posse (proprietário/condutor autorizado)
*   **pessoa\_imovel** — pessoa\_id, imovel\_id, tipo\_posse
*   **pessoa\_processo** — pessoa\_id, processo\_id, papel
*   **pessoa\_eleicao** — pessoa\_id, eleicao\_id, participou
*   **pessoa\_viagem\_companheiro** — pessoa\_id, viagem\_id, papel
*   **pessoa\_empresa\_socio** — pessoa\_id, empresa\_id, percentual\_participacao
*   **pessoa\_religiao\_historico** — pessoa\_id, crenca\_id, data\_inicio, data\_fim
*   **pessoa\_documento\_historico** — pessoa\_id, documento\_id, data\_emissao, data\_expiracao

* * *

🕸️ Mapa de relacionamento (hubs principais)
--------------------------------------------

                             ┌── familia ── heranca ── heranca_item
                             │
                             ├── empresa ── contrato_trabalho ── salario/holerite/beneficio
                             │
                             ├── imovel ── imovel_historico
                             │
                             ├── veiculo ── veiculo_historico
                             │
                  pessoa ────┼── processo ── julgamento ── sentenca ── pena
                    (hub)     │
                             ├── eleicao ── voto/candidato
                             │
                             ├── pet ── consulta_veterinaria/vacina_pet
                             │
                             ├── evento_vida ── linha_do_tempo
                             │
                             ├── conta_bancaria ── transacao/investimento
                             │
                             └── residencia ── endereco ── condominio
    

Todo domínio satélite referencia `pessoa.id`; os hubs de segundo nível (`empresa`, `imovel`, `processo`, `eleicao`, `familia`, `pet`, `endereco`) permitem consultas cruzadas do tipo:

> "Liste pessoas canhotas que herdaram dinheiro (`heranca`), tiveram mais de 2 empregos (`historico_emprego`), têm uma condição crônica específica (`condicao_cronica`) e votaram em determinado candidato (`voto`) numa eleição fictícia."

* * *

📊 Contagem
-----------

**25 domínios · ~256 tabelas fictícias**, todas conectáveis via `pessoa_id` ou via as chaves de hub de segundo nível. Para uma implementação real (SQLite/PostgreSQL), cada tabela vira um `CREATE TABLE` com `FOREIGN KEY (pessoa_id) REFERENCES pessoa(id)` — dá pra gerar o DDL inteiro programaticamente a partir desta lista, já que os nomes de tabela e campo aqui seguem convenção `snake_case` consistente.