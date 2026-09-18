"""Dados estáticos de referência: nomes, cidades, profissões, etc.

Owned by Agent 5. Conteúdo 100% fictício, determinístico, sem random.
"""
from __future__ import annotations

# --------------------------------------------------------------------------- #
# Nomes fictícios brasileiros
# --------------------------------------------------------------------------- #
MALE_FIRST_NAMES: list[str] = [
    "João", "Pedro", "Lucas", "Gabriel", "Matheus", "Rafael", "Felipe",
    "Gustavo", "Leonardo", "Vinícius", "Eduardo", "Bruno", "Rodrigo",
    "Thiago", "Fernando", "Marcelo", "André", "Carlos", "Miguel", "Daniel",
    "Arthur", "Enzo", "Heitor", "Samuel", "Benjamin", "Davi", "Lorenzo",
    "Bernardo", "Theo", "Henrique", "Felipe", "Caio", "Alan", "Roberto",
    "Paulo", "Antônio", "Amauri", "Sergio", "Marcos", "Murilo", "Diogo",
    "Igor", "Renato", "Leandro", "Nelson", "Cristiano", "Ailton", "Wallace",
    "Adevaldo", "Cicero", "Osvaldinho", "Adalberto", "Emílio", "Heraldo",
    "Rivaldo", "Nailton", "Deonilson", "Josivan", "Waderson", "Cleiton",
    "Elias", "Edivaldo", "Flávio", "Alisson", "Everton", "Jailson",
    "Kauan", "Ruan", "Léo", "Iuri", "Gabriel", "Davi", "Rafael",
    "Luan", "Matheus", "Bruno", "Otávio", "Thales", "Reuel", "Caio",
    "Benjamin", "Emanuel", "Ester", "Iago", "Isaac", "Saulo", "Anselmo",
    "Emerson", "Jonathan", "Bruno", "Leonardo", "Cláudio", "Assis",
    "Djalma", "Narciso", "Humberto", "Ari", "Cássio", "Dário",
    "Maurício", "Robson", "Carlos", "Adriano", "Josué", "Fábio",
    "Tiago", "Alex", "Alexandre", "Anderson", "Adilson", "Valdir",
    "Edson", "Wagner", "Claudio", "Edvaldo", "Ernani", "Gilmar",
    "Marcílio", "Nilson", "Aílton", "Josenildo", "Edmar", "Nélson",
    "Marcelino", "Danilo", "Edivaldo", "Genival", "Mauro", "Adoniran",
    "Hilário", "Josenildo", "Éverton", "Fábio", "Gerson", "Jefferson",
    "Gustavo", "Hudson", "Ivo", "Jean", "Joel", "Lázaro", "Marcel",
    "Marvin", "Nadson", "Odair", "Orlando", "Ramiro", "Reinaldo",
    "Roberto", "Valdir", "Valdeci", "Wesley", "Wladimir", "Xavier",
    "Yuri", "Zacarias", "Abel", "Breno", "Bruno", "Caio", "Cauê",
    "Danilo", "Davi", "Eduardo", "Erick", "Fabricio", "Geovane",
    "Ian", "Igor", "João", "Kauê", "Léo", "Luca", "Lucas",
    "Mateus", "Nicolas", "Paulo", "Pedro", "Rafael", "Ricardo",
    "Ruan", "Ryan", "Sergio", "Thales", "Thiago", "Vicente",
    "Wagner", "Wellington", "Zeca",
    "Ubiratan", "Teobaldo", "Simião", "Severino", "Raimundo", "Percival",
    "Osmir", "Nicanor", "Márcio", "Lauro", "Jarbas", "Irineu",
    "Hugo", "Geraldo", "Epaminondas", "Durval", "Clodoaldo", "Bonifácio",
    "Aquino", "Anacleto",
]

FEMALE_FIRST_NAMES: list[str] = [
    "Maria", "Ana", "Juliana", "Fernanda", "Patricia", "Camila", "Beatriz",
    "Larissa", "Amanda", "Bruna", "Carla", "Mariana", "Letícia", "Gabriela",
    "Renata", "Adriana", "Vanessa", "Raquel", "Fernanda", "Tainá", "Luzia",
    "Vitória", "Helena", "Valentina", "Lorena", "Isabela", "Manuela",
    "Cecília", "Livia", "Alícia", "Sophia", "Isabelly", "Heloísa",
    "Júlia", "Antonella", "Lavínia", "Maria", "Giovanna", "Melissa",
    "Yasmin", "Julia", "Lara", "Clara", "Luísa", "Esther", "Nicole",
    "Marina", "Bianca", "Priscila", "Tatiane", "Daiane", "Elaine",
    "Franciele", "Rosângela", "Cristiane", "Daniele", "Fabiana", "Graziela",
    "Joice", "Karine", "Luciana", "Milena", "Nathália", "Olga",
    "Priscila", "Queila", "Roberta", "Sandra", "Thais", "Valéria",
    "Ximena", "Zuleica", "Adeleide", "Adenilda", "Aires", "Alcione",
    "Amália", "Aparecida", "Araci", "Benedita", "Benigna", "Calina",
    "Clarice", "Cremilde", "Dalva", "Deolinda", "Efigênia", "Eunice",
    "Eurides", "Fatima", "Francisca", "Geralda", "Gertrudes", "Hilda",
    "Honória", "Iracema", "Irmã", "Ivete", "Jacira", "Joana",
    "Josefa", "Laís", "Léa", "Lídia", "Lorena", "Madalena",
    "Malvina", "Marciana", "Margarida", "Mariana", "Nair", "Nanci",
    "Nara", "Natalia", "Neide", "Nilda", "Orlandina", "Paula",
    "Raimunda", "Regina", "Rita", "Sônia", "Terezinha", "Valdete",
    "Verônica", "Zélia", "Adriana", "Alessandra", "Aline", "Brenda",
    "Cássia", "Cristina", "Eliane", "Eloisa", "Flávia", "Gisele",
    "Graça", "Helen", "Janaína", "Joelma", "Keila", "Lais",
    "Lilian", "Luciana", "Márcia", "Nayara", "Neuza", "Pamela",
    "Raquel", "Samanta", "Silmara", "Tânia", "Viviane", "Zélia",
    "Adriane", "Andreia", "Camila", "Carina", "Caroline", "Crystiele",
    "Debora", "Eliana", "Erika", "Fernanda", "Francielly", "Isabela",
    "Ivone", "Janaina", "Jéssica", "Katia", "Leilane", "Leticia",
    "Liliane", "Luciane", "Marciana", "Milena", "Nayara", "Núbia",
    "Paloma", "Patrícia", "Priscila", "Renata", "Roberta", "Rosangela",
    "Sara", "Simone", "Suelen", "Talita", "Thalía", "Ticiane",
    "Vanessa", "Veridiana", "Virgínia", "Vivian", "Zoraide", "Zuleica",
    "Alexia", "Aurora", "Bárbara", "Beatriz", "Bruna", "Caetana",
    "Diana", "Dora", "Elisa", "Érica", "Fabíola", "Glória",
    "Iara", "Ingrid", "Joana", "Karen", "Kátia", "Lívia",
    "Luana", "Maiara", "Nadine", "Otávia", "Pietra", "Quitéria",
    "Rita", "Sabrina", "Teresa", "Úrsula", "Vânia", "Wanessa",
]

SURNAMES: list[str] = [
    "Silva", "Souza", "Santos", "Oliveira", "Pereira", "Costa", "Rodrigues",
    "Almeida", "Nascimento", "Lima", "Araújo", "Barbosa", "Ribeiro",
    "Alves", "Monteiro", "Cardoso", "Martins", "Rocha", "Ramos", "Gomes",
    "Ferreira", "Carvalho", "Pinto", "Mendes", "Moreira", "Castro",
    "Lopes", "Vieira", "Teixeira", "Nunes", "Machado", "Melo",
    "Azevedo", "Cavalcanti", "Guerra", "Cunha", "Pires", "Campos",
    "Borges", "Batista", "Barros", "Fonseca", "Peixoto", "Tavares",
    "Moura", "Cardoso", "Andrade", "Macedo", "Cruz", "Carneiro",
    "Prado", "Rezende", "Neves", "Dias", "França", "Matos",
    "Correia", "Fagundes", "Magalhães", "Freitas", "Queiroz", "Pinheiro",
    "Lacerda", "Brito", "Brandão", "Viana", "Sales", "Duarte",
    "Henrique", "Farias", "Vasconcelos", "Reis", "Nogueira", "Brito",
    "Pimentel", "Teles", "Antunes", "Novaes", "Paiva", "Miranda",
    "Torres", "Bittencourt", "Amorim", "Camargo", "Bueno", "Vianna",
    "Moraes", "Guedes", "Medeiros", "Pacheco", "Dantas", "Aragão",
    "Medina", "Guimarães", "Leite", "Rangel", "Machado", "Bonfim",
    "Moraes", "Sampaio", "Xavier", "Paredes", "Pessoa", "Alencar",
    "Neto", "Pinho", "Valente", "Mattos", "Figueiredo", "Chaves",
    "Villas", "Macedo", "Siqueira", "Tavares", "Braga", "Caribé",
    "Sobreira", "Dantas", "Macêdo", "Maciel", "Montenegro", "Cabral",
    "Ipiranga", "Boaventura", "Grilo", "Cabeleira", "Tinga", "Arenhart",
    "Schimidt", "Froes", "Guimarães", "Bohn", "Netto", "Ritte",
    "Kessler", "Padilha", "Mattos", "Amaral", "Vianna", "Borges",
    "Goulart", "Royer", "Maluf", "Alvarenga", "Brasil", "Bittencourt",
    "Luz", "Noronha", "Sá", "Vilela", "Rezende", "Ferraz",
    "Cordeiro", "Brandão", "Vidal", "Lameira", "Santana", "Pires",
    "Baldin", "Simões", "Nobre", "Gaspar", "Caldas", "Silveira",
    "Boff", "Braz", "Campos", "Bezerra", "Pestana", "Bicalho",
    "Dorneles", "Amarante", "Barata", "Lopes", "Pupo", "Delfino",
    "Pavan", "Quintiliano", "Ribeiro", "Bomfim", "Simplício", "Velloso",
    "Porto", "Vilela", "Zanetti", "Elias", "Marrone", "Griz",
    "Linhares", "Sanches", "Bonatto", "Garcia", "Pisa", "Rossi",
    "Garbato", "Trentin", "Lunardi", "Pezzi", "Lopes", "Braga",
    "Galli", "Fonseca", "Luis", "Teles", "Magri", "Dornelas",
    "Bonfim", "Pessoa", "Aguiar", "Figueira", "Porto", "Macedo",
    "Accioli", "Achilles", "Acioli", "Adami", "Affonso", "Agripino",
    "Alarcon", "Albernaz", "Alencastro", "Alfonso", "Almada", "Alpoim",
    "Alquati", "Alsina", "Alvim", "Amabile", "Amado", "Amarilla",
    "Amato", "Amoroso", "Anchieta", "Anjos", "Antas", "Arantes",
    "Araripe", "Arcanjo", "Ares", "Ariano", "Arinos", "Arraes",
    "Arreguy", "Artiaga", "Amaral", "Assumpção", "Astorga", "Ataíde",
    "Augusto", "Aurélio", "Azevedo", "Azulay", "Bacelar", "Backes",
    "Bade", "Badia", "Baeta", "Baird", "Balbino", "Ballesteros",
    "Banha", "Barbieri", "Barboza", "Barreto", "Barroso", "Bastos",
    "Bauer", "Baumann", "Bechara", "Behlau", "Beirão", "Belo",
    "Beraldo", "Beretta", "Bergamasco", "Bergamin", "Bermudes", "Bernardes",
    "Bertolucci", "Bettencourt", "Bezerra", "Bianchi", "Bindá", "Bispo",
    "Bitencourt", "Bittar", "Bivar", "Bizarro", "Blanco", "Blumer",
    "Boaventura", "Boaz", "Bolognesi", "Bonato", "Bonetti", "Bordignon",
    "Borges", "Born", "Bortoluzzi", "Boscardin", "Botelho", "Bouças",
    "Bragantini", "Branco", "Brancaccio", "Brandalise", "Brasil", "Brelaz",
    "Breves", "Brígido", "Buarque", "Bueno", "Bugelli", "Burity",
    "Buzato", "Cabrera", "Caetano", "Café", "Caiado", "Caldana",
]

# --------------------------------------------------------------------------- #
# Cidades fictícias
# --------------------------------------------------------------------------- #
CIDADES: list[dict] = [
    {"name": "Alvorada Leste",     "uf": "SP", "region": "SE", "population": 1_850_000, "base_classes": {"A": 0.05,"B1": 0.10,"B2": 0.18,"C1": 0.25,"C2": 0.22,"D_E": 0.20}, "crime_index": 58, "cost_of_living": 1.72, "university_count": 4},
    {"name": "Porto Azul",         "uf": "RJ", "region": "SE", "population": 1_340_000, "base_classes": {"A": 0.04,"B1": 0.08,"B2": 0.16,"C1": 0.24,"C2": 0.26,"D_E": 0.22}, "crime_index": 62, "cost_of_living": 1.85, "university_count": 3},
    {"name": "Vale Dourada",       "uf": "MG", "region": "SE", "population": 980_000,  "base_classes": {"A": 0.03,"B1": 0.07,"B2": 0.14,"C1": 0.22,"C2": 0.27,"D_E": 0.27}, "crime_index": 45, "cost_of_living": 1.38, "university_count": 2},
    {"name": "Serra da Prata",     "uf": "ES", "region": "SE", "population": 760_000,  "base_classes": {"A": 0.03,"B1": 0.06,"B2": 0.15,"C1": 0.24,"C2": 0.25,"D_E": 0.27}, "crime_index": 38, "cost_of_living": 1.22, "university_count": 1},
    {"name": "Nova Serena",        "uf": "SP", "region": "SE", "population": 2_100_000, "base_classes": {"A": 0.06,"B1": 0.11,"B2": 0.19,"C1": 0.26,"C2": 0.21,"D_E": 0.17}, "crime_index": 52, "cost_of_living": 2.05, "university_count": 5},
    {"name": "Boa Brava",          "uf": "SP", "region": "SE", "population": 520_000,  "base_classes": {"A": 0.02,"B1": 0.05,"B2": 0.11,"C1": 0.20,"C2": 0.30,"D_E": 0.32}, "crime_index": 71, "cost_of_living": 1.10, "university_count": 0},
    {"name": "Monte Alto Verde",   "uf": "MG", "region": "SE", "population": 410_000,  "base_classes": {"A": 0.02,"B1": 0.05,"B2": 0.12,"C1": 0.21,"C2": 0.29,"D_E": 0.31}, "crime_index": 41, "cost_of_living": 1.15, "university_count": 0},
    {"name": "Santa Clara",        "uf": "RJ", "region": "SE", "population": 1_650_000, "base_classes": {"A": 0.04,"B1": 0.09,"B2": 0.17,"C1": 0.25,"C2": 0.25,"D_E": 0.20}, "crime_index": 55, "cost_of_living": 1.78, "university_count": 3},
    {"name": "Carmo Azul",         "uf": "MG", "region": "SE", "population": 290_000,  "base_classes": {"A": 0.02,"B1": 0.04,"B2": 0.10,"C1": 0.19,"C2": 0.31,"D_E": 0.34}, "crime_index": 35, "cost_of_living": 1.05, "university_count": 0},
    {"name": "Jardim Prata",       "uf": "SP", "region": "SE", "population": 1_120_000, "base_classes": {"A": 0.03,"B1": 0.07,"B2": 0.16,"C1": 0.23,"C2": 0.26,"D_E": 0.25}, "crime_index": 48, "cost_of_living": 1.45, "university_count": 2},
    {"name": "Bela Vista do Sul",  "uf": "SP", "region": "SE", "population": 670_000,  "base_classes": {"A": 0.02,"B1": 0.05,"B2": 0.13,"C1": 0.22,"C2": 0.28,"D_E": 0.30}, "crime_index": 42, "cost_of_living": 1.18, "university_count": 1},
    {"name": "Pontal do Leste",    "uf": "ES", "region": "SE", "population": 380_000,  "base_classes": {"A": 0.02,"B1": 0.05,"B2": 0.11,"C1": 0.20,"C2": 0.30,"D_E": 0.32}, "crime_index": 33, "cost_of_living": 1.08, "university_count": 0},
    {"name": "Rio Prata Velha",    "uf": "RJ", "region": "SE", "population": 2_400_000, "base_classes": {"A": 0.05,"B1": 0.10,"B2": 0.18,"C1": 0.24,"C2": 0.23,"D_E": 0.20}, "crime_index": 67, "cost_of_living": 2.10, "university_count": 5},
    {"name": "Pedra Grande",       "uf": "MG", "region": "SE", "population": 185_000,  "base_classes": {"A": 0.01,"B1": 0.03,"B2": 0.08,"C1": 0.17,"C2": 0.33,"D_E": 0.38}, "crime_index": 28, "cost_of_living": 1.02, "university_count": 0},
    {"name": "Alto Oeste",         "uf": "SP", "region": "SE", "population": 890_000,  "base_classes": {"A": 0.03,"B1": 0.06,"B2": 0.14,"C1": 0.22,"C2": 0.28,"D_E": 0.27}, "crime_index": 46, "cost_of_living": 1.30, "university_count": 1},
    {"name": "Terra Boa",          "uf": "MG", "region": "SE", "population": 540_000,  "base_classes": {"A": 0.02,"B1": 0.05,"B2": 0.12,"C1": 0.21,"C2": 0.29,"D_E": 0.31}, "crime_index": 39, "cost_of_living": 1.12, "university_count": 0},
    {"name": "São Gilberto",       "uf": "SP", "region": "SE", "population": 730_000,  "base_classes": {"A": 0.03,"B1": 0.06,"B2": 0.14,"C1": 0.23,"C2": 0.27,"D_E": 0.27}, "crime_index": 44, "cost_of_living": 1.25, "university_count": 1},
    {"name": "Flor da Serra",      "uf": "RJ", "region": "SE", "population": 460_000,  "base_classes": {"A": 0.02,"B1": 0.04,"B2": 0.11,"C1": 0.20,"C2": 0.30,"D_E": 0.33}, "crime_index": 36, "cost_of_living": 1.10, "university_count": 0},
    {"name": "Castelo Mirim",      "uf": "MG", "region": "SE", "population": 310_000,  "base_classes": {"A": 0.02,"B1": 0.04,"B2": 0.10,"C1": 0.19,"C2": 0.31,"D_E": 0.34}, "crime_index": 30, "cost_of_living": 1.04, "university_count": 0},
    {"name": "Vista Clara",        "uf": "SP", "region": "SE", "population": 1_560_000, "base_classes": {"A": 0.04,"B1": 0.09,"B2": 0.17,"C1": 0.25,"C2": 0.25,"D_E": 0.20}, "crime_index": 53, "cost_of_living": 1.70, "university_count": 3},
    {"name": "Bela Alta",          "uf": "ES", "region": "SE", "population": 210_000,  "base_classes": {"A": 0.02,"B1": 0.04,"B2": 0.10,"C1": 0.18,"C2": 0.31,"D_E": 0.35}, "crime_index": 25, "cost_of_living": 1.00, "university_count": 0},
    {"name": "Leste Grande",       "uf": "SP", "region": "SE", "population": 3_200_000, "base_classes": {"A": 0.07,"B1": 0.12,"B2": 0.19,"C1": 0.25,"C2": 0.20,"D_E": 0.17}, "crime_index": 70, "cost_of_living": 2.30, "university_count": 6},
    {"name": "Pontal do Sul",      "uf": "PR", "region": "S",  "population": 420_000,  "base_classes": {"A": 0.04,"B1": 0.08,"B2": 0.16,"C1": 0.24,"C2": 0.25,"D_E": 0.23}, "crime_index": 28, "cost_of_living": 1.22, "university_count": 1},
    {"name": "Alvorada Nova",      "uf": "PR", "region": "S",  "population": 680_000,  "base_classes": {"A": 0.04,"B1": 0.09,"B2": 0.17,"C1": 0.25,"C2": 0.24,"D_E": 0.21}, "crime_index": 32, "cost_of_living": 1.35, "university_count": 1},
    {"name": "Serra do Mirim",     "uf": "SC", "region": "S",  "population": 540_000,  "base_classes": {"A": 0.03,"B1": 0.08,"B2": 0.16,"C1": 0.25,"C2": 0.24,"D_E": 0.24}, "crime_index": 22, "cost_of_living": 1.28, "university_count": 1},
    {"name": "Vale do Prata",      "uf": "RS", "region": "S",  "population": 760_000,  "base_classes": {"A": 0.04,"B1": 0.09,"B2": 0.17,"C1": 0.25,"C2": 0.24,"D_E": 0.21}, "crime_index": 30, "cost_of_living": 1.40, "university_count": 2},
    {"name": "Lagoa Bonita",       "uf": "PR", "region": "S",  "population": 350_000,  "base_classes": {"A": 0.03,"B1": 0.06,"B2": 0.14,"C1": 0.23,"C2": 0.27,"D_E": 0.27}, "crime_index": 26, "cost_of_living": 1.15, "university_count": 0},
    {"name": "Alto da Serra",      "uf": "SC", "region": "S",  "population": 290_000,  "base_classes": {"A": 0.03,"B1": 0.06,"B2": 0.13,"C1": 0.22,"C2": 0.28,"D_E": 0.28}, "crime_index": 18, "cost_of_living": 1.10, "university_count": 0},
    {"name": "Oeste Próspéro",     "uf": "RS", "region": "S",  "population": 470_000,  "base_classes": {"A": 0.03,"B1": 0.07,"B2": 0.15,"C1": 0.24,"C2": 0.26,"D_E": 0.25}, "crime_index": 25, "cost_of_living": 1.20, "university_count": 1},
    {"name": "Porto Sereno",       "uf": "PR", "region": "S",  "population": 190_000,  "base_classes": {"A": 0.02,"B1": 0.04,"B2": 0.10,"C1": 0.20,"C2": 0.31,"D_E": 0.33}, "crime_index": 15, "cost_of_living": 1.02, "university_count": 0},
    {"name": "Flores do Norte",    "uf": "PR", "region": "S",  "population": 150_000,  "base_classes": {"A": 0.02,"B1": 0.04,"B2": 0.09,"C1": 0.18,"C2": 0.32,"D_E": 0.35}, "crime_index": 20, "cost_of_living": 1.00, "university_count": 0},
    {"name": "Campos Novos",       "uf": "SC", "region": "S",  "population": 380_000,  "base_classes": {"A": 0.03,"B1": 0.07,"B2": 0.15,"C1": 0.24,"C2": 0.25,"D_E": 0.26}, "crime_index": 20, "cost_of_living": 1.18, "university_count": 0},
    {"name": "Bonito Leste",       "uf": "RS", "region": "S",  "population": 260_000,  "base_classes": {"A": 0.02,"B1": 0.05,"B2": 0.12,"C1": 0.21,"C2": 0.29,"D_E": 0.31}, "crime_index": 19, "cost_of_living": 1.08, "university_count": 0},
    {"name": "Real do Norte",      "uf": "PA", "region": "N",  "population": 890_000,  "base_classes": {"A": 0.02,"B1": 0.04,"B2": 0.10,"C1": 0.18,"C2": 0.31,"D_E": 0.35}, "crime_index": 72, "cost_of_living": 1.05, "university_count": 1},
    {"name": "Alvorada das Águas", "uf": "AM", "region": "N",  "population": 1_450_000, "base_classes": {"A": 0.03,"B1": 0.06,"B2": 0.13,"C1": 0.21,"C2": 0.28,"D_E": 0.29}, "crime_index": 78, "cost_of_living": 1.42, "university_count": 2},
    {"name": "Vale do Sol",        "uf": "AC", "region": "N",  "population": 120_000,  "base_classes": {"A": 0.01,"B1": 0.03,"B2": 0.08,"C1": 0.16,"C2": 0.33,"D_E": 0.39}, "crime_index": 65, "cost_of_living": 0.95, "university_count": 0},
    {"name": "Porto Esperança",    "uf": "AP", "region": "N",  "population": 95_000,   "base_classes": {"A": 0.01,"B1": 0.02,"B2": 0.07,"C1": 0.15,"C2": 0.34,"D_E": 0.41}, "crime_index": 80, "cost_of_living": 0.92, "university_count": 0},
    {"name": "Serra da Paz",       "uf": "CE", "region": "NE", "population": 1_100_000, "base_classes": {"A": 0.02,"B1": 0.05,"B2": 0.12,"C1": 0.21,"C2": 0.29,"D_E": 0.31}, "crime_index": 55, "cost_of_living": 1.10, "university_count": 2},
    {"name": "Vista do Mar",       "uf": "BA", "region": "NE", "population": 1_780_000, "base_classes": {"A": 0.03,"B1": 0.06,"B2": 0.14,"C1": 0.22,"C2": 0.27,"D_E": 0.28}, "crime_index": 60, "cost_of_living": 1.30, "university_count": 3},
    {"name": "Leste Serena",       "uf": "PE", "region": "NE", "population": 1_350_000, "base_classes": {"A": 0.03,"B1": 0.06,"B2": 0.13,"C1": 0.22,"C2": 0.28,"D_E": 0.28}, "crime_index": 58, "cost_of_living": 1.25, "university_count": 2},
    {"name": "Nova Brava",         "uf": "MA", "region": "NE", "population": 280_000,  "base_classes": {"A": 0.01,"B1": 0.03,"B2": 0.09,"C1": 0.17,"C2": 0.32,"D_E": 0.38}, "crime_index": 68, "cost_of_living": 0.98, "university_count": 0},
    {"name": "Porto Real",         "uf": "PB", "region": "NE", "population": 190_000,  "base_classes": {"A": 0.01,"B1": 0.03,"B2": 0.08,"C1": 0.17,"C2": 0.33,"D_E": 0.38}, "crime_index": 50, "cost_of_living": 0.95, "university_count": 0},
    {"name": "Alto do Norte",      "uf": "RN", "region": "NE", "population": 310_000,  "base_classes": {"A": 0.02,"B1": 0.04,"B2": 0.10,"C1": 0.19,"C2": 0.30,"D_E": 0.35}, "crime_index": 42, "cost_of_living": 1.02, "university_count": 0},
    {"name": "Rio Bonito",         "uf": "AL", "region": "NE", "population": 220_000,  "base_classes": {"A": 0.01,"B1": 0.03,"B2": 0.09,"C1": 0.17,"C2": 0.32,"D_E": 0.38}, "crime_index": 55, "cost_of_living": 0.97, "university_count": 0},
    {"name": "Terra do Sol",       "uf": "SE", "region": "NE", "population": 155_000,  "base_classes": {"A": 0.01,"B1": 0.02,"B2": 0.08,"C1": 0.16,"C2": 0.33,"D_E": 0.40}, "crime_index": 48, "cost_of_living": 0.93, "university_count": 0},
    {"name": "Carmo do Oeste",     "uf": "PI", "region": "NE", "population": 130_000,  "base_classes": {"A": 0.01,"B1": 0.02,"B2": 0.07,"C1": 0.15,"C2": 0.34,"D_E": 0.41}, "crime_index": 52, "cost_of_living": 0.90, "university_count": 0},
    {"name": "Jardim do Norte",    "uf": "CE", "region": "NE", "population": 560_000,  "base_classes": {"A": 0.02,"B1": 0.04,"B2": 0.11,"C1": 0.20,"C2": 0.30,"D_E": 0.33}, "crime_index": 62, "cost_of_living": 1.08, "university_count": 1},
    {"name": "Serra Clara",        "uf": "BA", "region": "NE", "population": 670_000,  "base_classes": {"A": 0.02,"B1": 0.04,"B2": 0.11,"C1": 0.20,"C2": 0.30,"D_E": 0.33}, "crime_index": 55, "cost_of_living": 1.10, "university_count": 1},
    {"name": "Monte Belo",         "uf": "PE", "region": "NE", "population": 450_000,  "base_classes": {"A": 0.02,"B1": 0.04,"B2": 0.10,"C1": 0.19,"C2": 0.31,"D_E": 0.34}, "crime_index": 50, "cost_of_living": 1.05, "university_count": 0},
    {"name": "Lagoa Grande",       "uf": "MA", "region": "NE", "population": 380_000,  "base_classes": {"A": 0.01,"B1": 0.03,"B2": 0.09,"C1": 0.18,"C2": 0.32,"D_E": 0.37}, "crime_index": 65, "cost_of_living": 1.00, "university_count": 0},
    {"name": "Bela Vista do Mar",  "uf": "PB", "region": "NE", "population": 250_000,  "base_classes": {"A": 0.01,"B1": 0.03,"B2": 0.08,"C1": 0.17,"C2": 0.33,"D_E": 0.38}, "crime_index": 52, "cost_of_living": 0.96, "university_count": 0},
    {"name": "Vista Leste",        "uf": "RN", "region": "NE", "population": 180_000,  "base_classes": {"A": 0.01,"B1": 0.03,"B2": 0.08,"C1": 0.16,"C2": 0.33,"D_E": 0.39}, "crime_index": 40, "cost_of_living": 1.00, "university_count": 0},
]

# --------------------------------------------------------------------------- #
# Bairros fictícios (gerados das cidades)
# --------------------------------------------------------------------------- #
_BAIRRO_STEMS = [
    "Centro", "Jardim", "Vila", "Bela", "Alto", "Bosque", "Lagoa", "Parque",
    "Industrial", "Residencial", "Universitário", "Comercial",
]


def _build_bairros() -> list[dict]:
    bairros: list[dict] = []
    nid = 0
    for c in CIDADES:
        n = 9 + (c["population"] // 150_000) % 5  # 9-13 per city -> ~520 total for 52 cities
        for i in range(n):
            bairros.append({
                "name": f"{_BAIRRO_STEMS[i % len(_BAIRRO_STEMS)]} {c['uf']}-{nid:04d}",
                "city_name": c["name"],
                "class_profiles": [list(c["base_classes"].keys())[i % 6]],
                "crime_level": (c["crime_index"] + i * 5) % 100,
                "school_quality": max(1, 8 - i % 7),
                "health_quality": max(1, 7 - i % 6),
            })
            nid += 1
    return bairros


BAIRROS: list[dict] = _build_bairros()

# --------------------------------------------------------------------------- #
# Bancos, empresas, hospitais, universidades, profissões, etc.
# --------------------------------------------------------------------------- #
BANCOS: list[dict] = [
    {"code": "001", "name": "Banco Central Fictício"},
    {"code": "012", "name": "Banco Nacional Inventado"},
    {"code": "033", "name": "Banco Simbólico"},
    {"code": "041", "name": "Banco do Povo Virtual"},
    {"code": "070", "name": "BrasBank"},
    {"code": "077", "name": "Banco Popular Digital"},
    {"code": "104", "name": "Caixa Simulada"},
    {"code": "125", "name": "Banco Alfa Fictício"},
    {"code": "136", "name": "Unibanco Inventado"},
    {"code": "140", "name": "Mercantil Ficc."},
    {"code": "162", "name": "Banco Verde"},
    {"code": "184", "name": "Itaú Fictício"},
    {"code": "208", "name": "BTG Inventado"},
    {"code": "212", "name": "Banco Real Ficc."},
    {"code": "237", "name": "Bradesco Simulado"},
    {"code": "246", "name": "Banco ABC Fictício"},
    {"code": "260", "name": "Nu Bank Virtual"},
    {"code": "290", "name": "PagBank Simulado"},
    {"code": "318", "name": "BMG Fictício"},
    {"code": "336", "name": "C6 Inventado"},
    {"code": "341", "name": "Itau Unibanco Ficc."},
    {"code": "389", "name": "Banco Mercantil"},
    {"code": "422", "name": "Safra Fictício"},
    {"code": "613", "name": "Omni Fictício"},
    {"code": "623", "name": "Pan Fictício"},
    {"code": "633", "name": "Rendimento Ficc."},
    {"code": "707", "name": "Daycoval Ficc."},
    {"code": "741", "name": "Ribeiro Preto Ficc."},
    {"code": "745", "name": "Citibank Ficc."},
    {"code": "748", "name": "Sicredi Inventado"},
]


def _valid_cnpj(digits14: str) -> bool:
    """Valida CNPJ com dígitos verificadores (algoritmo padrão)."""
    if len(digits14) != 14 or not digits14.isdigit():
        return False
    weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digits = [int(d) for d in digits14]

    def _dv(tot: int) -> int:
        dv = 11 - tot % 11
        return 0 if dv >= 10 else dv

    d1 = _dv(sum(d * w for d, w in zip(digits[:12], weights1)))
    d2 = _dv(sum(d * w for d, w in zip(digits[:12] + [d1], weights2)))
    return digits[12] == d1 and digits[13] == d2


def _make_cnpj(seed_str: str) -> str:
    """Gera CNPJ fictício começando por 00 com dígitos válidos."""
    import hashlib
    h = hashlib.sha256(seed_str.encode()).hexdigest()
    num = int(h[:14], 16) % 1_000
    base = "000000000" + f"{num:03d}"  # 12 dígitos: prefixo 00 + bloco fictício
    weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digits = [int(d) for d in base]

    def _dv(tot: int) -> int:
        dv = 11 - tot % 11
        return 0 if dv >= 10 else dv

    d1 = _dv(sum(d * w for d, w in zip(digits[:12], weights1)))
    d2 = _dv(sum(d * w for d, w in zip(digits[:12] + [d1], weights2)))
    return base + str(d1) + str(d2)


_EMPRESA_SECTORS = [
    "tecnologia", "saude", "educacao", "financeiro", "varejo",
    "industria", "agro", "construcao", "transporte", "energia",
    "comunicacao", "turismo", "alimento", "moda",
]

EMPRESAS: list[dict] = [
    {"cnpj": _make_cnpj(f"empresa_{i:03d}"), "name": f"Empresa {i} Fictícia", "sector": _EMPRESA_SECTORS[i % len(_EMPRESA_SECTORS)]}
    for i in range(100)
]

# Verify CNPJ validity (for seed data integrity)
assert all(_valid_cnpj(e["cnpj"]) for e in EMPRESAS), "Invalid CNPJ generated"

UNIVERSIDADES: list[dict] = [
    {"name": "Universidade Fictícia de São Paulo", "uf": "SP", "type": "publica"},
    {"name": "Inventada Federal do Rio", "uf": "RJ", "type": "publica"},
    {"name": "PUC Simulada", "uf": "RJ", "type": "privada"},
    {"name": "Universidade Nova de Minas", "uf": "MG", "type": "publica"},
    {"name": "UniCamp Virtual", "uf": "SP", "type": "publica"},
    {"name": "Fictícia do Nordeste", "uf": "BA", "type": "publica"},
    {"name": "Universidade Vale do Prata", "uf": "RS", "type": "publica"},
    {"name": "Centro Universitário do Sul", "uf": "SC", "type": "privada"},
    {"name": "Unicamp Marechal", "uf": "PR", "type": "privada"},
    {"name": "Estácio Fictício", "uf": "RJ", "type": "privada"},
    {"name": "Anhanguera Simulado", "uf": "SP", "type": "privada"},
    {"name": "FMT Virtual", "uf": "CE", "type": "publica"},
    {"name": "UFRN Inventada", "uf": "RN", "type": "publica"},
    {"name": "UFPE Fictícia", "uf": "PE", "type": "publica"},
    {"name": "UFBA Simulada", "uf": "BA", "type": "publica"},
    {"name": "UFRGS Virtual", "uf": "RS", "type": "publica"},
    {"name": "UFSC Simulada", "uf": "SC", "type": "publica"},
    {"name": "UEL Fictícia", "uf": "PR", "type": "publica"},
    {"name": "UEMA Inventada", "uf": "MA", "type": "publica"},
    {"name": "UFPB Fictícia", "uf": "PB", "type": "publica"},
    {"name": "UFC Inventada", "uf": "CE", "type": "publica"},
    {"name": "PUC Minas Fictícia", "uf": "MG", "type": "privada"},
    {"name": "UNIP Simulada", "uf": "SP", "type": "privada"},
    {"name": "Mackenzie Inventado", "uf": "SP", "type": "privada"},
    {"name": "FGV Fictícia", "uf": "SP", "type": "privada"},
    {"name": "Insper Simulado", "uf": "SP", "type": "privada"},
    {"name": "PUCRS Fictícia", "uf": "RS", "type": "privada"},
    {"name": "PUCPR Simulada", "uf": "PR", "type": "privada"},
    {"name": "UFSCar Inventada", "uf": "SP", "type": "publica"},
    {"name": "UFPR Fictícia", "uf": "PR", "type": "publica"},
    {"name": "FURB Simulada", "uf": "SC", "type": "privada"},
    {"name": "UNISUL Inventada", "uf": "SC", "type": "privada"},
    {"name": "UNIVALI Fictícia", "uf": "SC", "type": "privada"},
    {"name": "UNESC Virtual", "uf": "SC", "type": "privada"},
    {"name": "FAMERP Simulada", "uf": "SP", "type": "publica"},
    {"name": "FCL Simulada", "uf": "SP", "type": "privada"},
    {"name": "UNIFESP Inventada", "uf": "SP", "type": "publica"},
    {"name": "FMRP Fictícia", "uf": "MG", "type": "publica"},
    {"name": "UFV Simulada", "uf": "MG", "type": "publica"},
    {"name": "UFU Fictícia", "uf": "MG", "type": "publica"},
    {"name": "UFMT Inventada", "uf": "MT", "type": "publica"},
    {"name": "UFMS Simulada", "uf": "MS", "type": "publica"},
    {"name": "UFGD Fictícia", "uf": "MS", "type": "publica"},
    {"name": "UFPA Virtual", "uf": "PA", "type": "publica"},
    {"name": "UEA Inventada", "uf": "AM", "type": "publica"},
    {"name": "UFAC Fictícia", "uf": "AC", "type": "publica"},
    {"name": "UFRR Simulada", "uf": "RR", "type": "publica"},
    {"name": "UFRO Inventada", "uf": "RO", "type": "publica"},
    {"name": "UFPI Fictícia", "uf": "PI", "type": "publica"},
    {"name": "UECE Simulada", "uf": "CE", "type": "publica"},
]

HOSPITAIS: list[dict] = [
    {"name": "Hospital São Lucas Inventado", "city_name": "Alvorada Leste", "beds": 350},
    {"name": "Santa Casa Simulada", "city_name": "Porto Azul", "beds": 280},
    {"name": "Hospital Municipal Fictício", "city_name": "Nova Serena", "beds": 220},
    {"name": "Hospital Geral do Vale", "city_name": "Vale Dourada", "beds": 180},
    {"name": "Hospital Central Inventado", "city_name": "Leste Grande", "beds": 500},
    {"name": "Hospital da Criança Virtual", "city_name": "Santa Clara", "beds": 150},
    {"name": "Hospital das Clínicas Ficc.", "city_name": "Serra da Prata", "beds": 120},
    {"name": "Hospital do Norte Simulado", "city_name": "Alvorada das Águas", "beds": 200},
    {"name": "Hospital Universitário Ficc.", "city_name": "Leste Serena", "beds": 160},
    {"name": "Hospital do Povo Fictício", "city_name": "Vista do Mar", "beds": 240},
    {"name": "Hospital Regional Sul", "city_name": "Vale do Prata", "beds": 140},
    {"name": "Maternidade Nossa Senhora", "city_name": "Pontal do Sul", "beds": 100},
    {"name": "Hospital Cardíaco Simulado", "city_name": "Rio Prata Velha", "beds": 180},
    {"name": "Hospital Infantil Fictício", "city_name": "Alvorada Nova", "beds": 110},
    {"name": "Hospital Geral do Mar", "city_name": "Vista do Mar", "beds": 260},
    {"name": "Hospital Psiquiátrico Ficc.", "city_name": "Serra Clara", "beds": 90},
    {"name": "Pronto-Socorro Central", "city_name": "Boa Brava", "beds": 60},
    {"name": "UPA 24h Virtual", "city_name": "Jardim Prata", "beds": 40},
    {"name": "Hospital Oncológico Ficc.", "city_name": "Nova Serena", "beds": 170},
    {"name": "Hospital Materno Infantil", "city_name": "Vale do Sol", "beds": 80},
    {"name": "Hospital Norte Fictício", "city_name": "Real do Norte", "beds": 190},
    {"name": "Hospital Costa Leste", "city_name": "Porto Esperança", "beds": 70},
    {"name": "Hospital do Agreste Ficc.", "city_name": "Jardim do Norte", "beds": 130},
    {"name": "Hospital do Sertão Fictício", "city_name": "Nova Brava", "beds": 60},
    {"name": "Hospital do Agreste Virtual", "city_name": "Monte Belo", "beds": 100},
    {"name": "Hospital Interior SP", "city_name": "Pedra Grande", "beds": 85},
    {"name": "Hospital Doenças Tropicais", "city_name": "Porto Real", "beds": 95},
    {"name": "Hospital Referência Norte", "city_name": "Alvorada das Águas", "beds": 320},
    {"name": "Hospital Fictício SE", "city_name": "Terra do Sol", "beds": 70},
    {"name": "Hospital Comunitário", "city_name": "Lagoa Bonita", "beds": 50},
]

# --------------------------------------------------------------------------- #
# Profissões (500+)
# --------------------------------------------------------------------------- #
def _build_profissoes() -> list[dict]:
    profs: list[dict] = []
    base: list[tuple[str, str, str, int]] = [
        ("Médico", "saude", "superior", 180_000),
        ("Enfermeiro", "saude", "superior", 60_000),
        ("Técnico de Enfermagem", "saude", "tecnico", 36_000),
        ("Farmacêutico", "saude", "superior", 72_000),
        ("Dentista", "saude", "superior", 120_000),
        ("Psicólogo", "saude", "superior", 66_000),
        ("Fisioterapeuta", "saude", "superior", 54_000),
        ("Fonoaudiólogo", "saude", "superior", 58_000),
        ("Advogado", "juridico", "superior", 90_000),
        ("Desenvolvedor", "tecnologia", "superior", 96_000),
        ("Designer", "tecnologia", "superior", 54_000),
        ("Analista de Sistemas", "tecnologia", "superior", 108_000),
        ("Professor", "educacao", "superior", 54_000),
        ("Professor Universitário", "educacao", "pos", 96_000),
        ("Pedagogo", "educacao", "superior", 48_000),
        ("Engenheiro Civil", "construcao", "superior", 110_000),
        ("Engenheiro de Produção", "industria", "superior", 105_000),
        ("Arquiteto", "construcao", "superior", 84_000),
        ("Técnico em Edificações", "construcao", "tecnico", 38_000),
        ("Contador", "financeiro", "superior", 72_000),
        ("Economista", "financeiro", "superior", 96_000),
        ("Analista Financeiro", "financeiro", "superior", 84_000),
        ("Auditor", "financeiro", "superior", 102_000),
        ("Vendedor", "varejo", "tecnico", 30_000),
        ("Gerente Comercial", "varejo", "superior", 78_000),
        ("Atendente", "varejo", "medio", 18_000),
        ("Caixa", "varejo", "medio", 16_800),
        ("Motorista", "transporte", "medio", 24_000),
        ("Piloto", "transporte", "superior", 120_000),
        ("Operador de Empilhadeira", "transporte", "tecnico", 26_000),
        ("Fazendeiro", "agro", "medio", 42_000),
        ("Agrônomo", "agro", "superior", 72_000),
        ("Veterinário", "saude", "superior", 78_000),
        ("Zootécnico", "agro", "superior", 60_000),
        ("Jornalista", "comunicacao", "superior", 48_000),
        ("Produtor de TV", "comunicacao", "superior", 60_000),
        ("Relações Públicas", "comunicacao", "superior", 54_000),
        ("Policial Militar", "seguranca", "medio", 42_000),
        ("Bombeiro", "seguranca", "medio", 48_000),
        ("Bancário", "financeiro", "tecnico", 36_000),
        ("Gestor de RH", "gerencia", "superior", 78_000),
        ("Gerente de Projetos", "gerencia", "superior", 102_000),
        ("Cozinheiro", "alimento", "medio", 24_000),
        ("Garçom", "alimento", "medio", 15_600),
        ("Cabelereiro", "estetica", "tecnico", 21_600),
        ("Esteticista", "estetica", "tecnico", 30_000),
        ("Técnico em Informática", "tecnologia", "tecnico", 42_000),
        ("Operador de Telemarketing", "comunicacao", "medio", 16_800),
        ("Porteiro", "servico", "medio", 16_200),
        ("Diarista", "servico", "medio", 14_400),
        ("Pedreiro", "construcao", "medio", 30_000),
        ("Eletricista", "construcao", "tecnico", 36_000),
        ("Encanador", "construcao", "medio", 28_800),
        ("Marceneiro", "industria", "tecnico", 32_400),
        ("Soldador", "industria", "tecnico", 36_000),
        ("Maquinista", "industria", "tecnico", 42_000),
        ("Técnico Agrícola", "agro", "tecnico", 30_000),
        ("Militar", "seguranca", "medio", 48_000),
        ("Juiz", "juridico", "pos", 240_000),
        ("Promotor", "juridico", "pos", 180_000),
        ("Delegado", "juridico", "pos", 168_000),
        ("Perito Criminal", "juridico", "superior", 120_000),
        ("Cartorário", "juridico", "tecnico", 48_000),
        ("Tradutor", "educacao", "superior", 54_000),
        ("Bibliotecário", "educacao", "superior", 42_000),
        ("Arquivólogo", "educacao", "superior", 48_000),
        ("Museólogo", "educacao", "superior", 48_000),
        ("Artista Plástico", "cultura", "superior", 36_000),
        ("Músico", "cultura", "superior", 30_000),
        ("Ator", "cultura", "superior", 24_000),
        ("Cantor", "cultura", "medio", 36_000),
        ("Dançarino", "cultura", "medio", 21_600),
        ("Personal Trainer", "saude", "tecnico", 48_000),
        ("Nutricionista", "saude", "superior", 60_000),
        ("Professor de Educação Física", "educacao", "superior", 42_000),
        ("Piloto de Drone", "tecnologia", "tecnico", 36_000),
        ("Programador", "tecnologia", "superior", 84_000),
        ("Cientista de Dados", "tecnologia", "superior", 144_000),
        ("Engenheiro de Software", "tecnologia", "superior", 120_000),
        ("DevOps", "tecnologia", "superior", 108_000),
        ("Analista de Dados", "tecnologia", "superior", 90_000),
        ("UX Designer", "tecnologia", "superior", 78_000),
        ("Product Owner", "tecnologia", "superior", 102_000),
        ("Scrum Master", "tecnologia", "superior", 96_000),
        ("Cientista da Computação", "tecnologia", "superior", 126_000),
        ("Analista de Segurança", "tecnologia", "superior", 96_000),
        ("Engenheiro de Redes", "tecnologia", "superior", 84_000),
        ("Administrador", "gerencia", "superior", 72_000),
        ("Logística", "transporte", "superior", 66_000),
        ("Gerente de Operações", "gerencia", "superior", 108_000),
        ("Diretor Comercial", "gerencia", "superior", 168_000),
        ("CEO", "gerencia", "superior", 300_000),
    ]

    for name, sector, nivel, salary in base:
        cbo = f"{sector[:3].upper()}{hash(name) % 1000:03d}"
        profs.append({
            "profissao": name,
            "setor": sector,
            "nivel": nivel,
            "salario_mediana": float(salary),
            "cbo_like_code": cbo,
        })
        # variantes
        for suf in [" Jr.", " Pleno", " Sênior"]:
            profs.append({
                "profissao": name + suf,
                "setor": sector,
                "nivel": nivel,
                "salario_mediana": float(salary * (0.75 if "Jr" in suf else 1.0 if "Pleno" in suf else 1.25)),
                "cbo_like_code": f"{cbo}{suf.strip()[:1]}",
            })
    return profs[:550]

PROFISSOES: list[dict] = _build_profissoes()
while len(PROFISSOES) < 500:
    i = len(PROFISSOES)
    PROFISSOES.append({
        "profissao": f"Profissional {i:03d}",
        "setor": _EMPRESA_SECTORS[i % len(_EMPRESA_SECTORS)],
        "nivel": ["medio", "tecnico", "superior"][i % 3],
        "salario_mediana": float(24_000 + (i * 1337) % 120_000),
        "cbo_like_code": f"P{i:03d}",
    })

# --------------------------------------------------------------------------- #
# Doenças, medicamentos, cursos, raças de pet, partidos
# --------------------------------------------------------------------------- #
DOENCAS: list[dict] = [
    {"doenca": "Diabetes Tipo 2", "categoria": "metabolica", "gravidade_padrao": "moderado"},
    {"doenca": "Hipertensão Arterial", "categoria": "cardiovascular", "gravidade_padrao": "moderado"},
    {"doenca": "Asma", "categoria": "respiratoria", "gravidade_padrao": "leve"},
    {"doenca": "Depressão", "categoria": "mental", "gravidade_padrao": "moderado"},
    {"doenca": "Ansiedade Generalizada", "categoria": "mental", "gravidade_padrao": "leve"},
    {"doenca": "Transtorno Bipolar", "categoria": "mental", "gravidade_padrao": "grave"},
    {"doenca": "Dor Lombar Crônica", "categoria": "ortopedica", "gravidade_padrao": "leve"},
    {"doenca": "Artrose", "categoria": "ortopedica", "gravidade_padrao": "moderado"},
    {"doenca": "Gastrite", "categoria": "digestiva", "gravidade_padrao": "leve"},
    {"doenca": "Úlcera Péptica", "categoria": "digestiva", "gravidade_padrao": "moderado"},
    {"doenca": "Infarto Agudo", "categoria": "cardiovascular", "gravidade_padrao": "grave"},
    {"doenca": "AVC Isquêmico", "categoria": "neurologica", "gravidade_padrao": "grave"},
    {"doenca": "Câncer de Pulmão", "categoria": "oncologica", "gravidade_padrao": "grave"},
    {"doenca": "Câncer de Mama", "categoria": "oncologica", "gravidade_padrao": "grave"},
    {"doenca": "Câncer de Próstata", "categoria": "oncologica", "gravidade_padrao": "grave"},
    {"doenca": "Leucemia", "categoria": "oncologica", "gravidade_padrao": "grave"},
    {"doenca": "Linfoma", "categoria": "oncologica", "gravidade_padrao": "grave"},
    {"doenca": "Insuficiência Renal", "categoria": "metabolica", "gravidade_padrao": "grave"},
    {"doenca": "Hepatite B", "categoria": "infecciosa", "gravidade_padrao": "moderado"},
    {"doenca": "Tuberculose", "categoria": "infecciosa", "gravidade_padrao": "grave"},
    {"doenca": "Dengue", "categoria": "infecciosa", "gravidade_padrao": "moderado"},
    {"doenca": "Zika", "categoria": "infecciosa", "gravidade_padrao": "leve"},
    {"doenca": "Chikungunya", "categoria": "infecciosa", "gravidade_padrao": "leve"},
    {"doenca": "Covid-19", "categoria": "infecciosa", "gravidade_padrao": "moderado"},
    {"doenca": "HIV/AIDS", "categoria": "infecciosa", "gravidade_padrao": "grave"},
    {"doenca": "Malaria", "categoria": "infecciosa", "gravidade_padrao": "moderado"},
    {"doenca": "Febre Reumática", "categoria": "infecciosa", "gravidade_padrao": "moderado"},
    {"doenca": "Esclerose Múltipla", "categoria": "autoimune", "gravidade_padrao": "grave"},
    {"doenca": "Lúpus Eritematoso", "categoria": "autoimune", "gravidade_padrao": "grave"},
    {"doenca": "Artrite Reumatoide", "categoria": "autoimune", "gravidade_padrao": "moderado"},
    {"doenca": "Doença de Crohn", "categoria": "autoimune", "gravidade_padrao": "moderado"},
    {"doenca": "Colite Ulcerativa", "categoria": "autoimune", "gravidade_padrao": "moderado"},
    {"doenca": "Glaucoma", "categoria": "oftalmologica", "gravidade_padrao": "moderado"},
    {"doenca": "Catarata", "categoria": "oftalmologica", "gravidade_padrao": "leve"},
    {"doenca": "Miopia Severa", "categoria": "oftalmologica", "gravidade_padrao": "leve"},
    {"doenca": "Fibromialgia", "categoria": "neurologica", "gravidade_padrao": "moderado"},
    {"doenca": "Enxaqueca Crônica", "categoria": "neurologica", "gravidade_padrao": "leve"},
    {"doenca": "Epilepsia", "categoria": "neurologica", "gravidade_padrao": "moderado"},
    {"doenca": "Parkinson", "categoria": "neurologica", "gravidade_padrao": "grave"},
    {"doenca": "Alzheimer", "categoria": "neurologica", "gravidade_padrao": "grave"},
    {"doenca": "Bipolaridade", "categoria": "mental", "gravidade_padrao": "grave"},
    {"doenca": "Esquizofrenia", "categoria": "mental", "gravidade_padrao": "grave"},
    {"doenca": "TDAH", "categoria": "mental", "gravidade_padrao": "leve"},
    {"doenca": "Insônia Crônica", "categoria": "mental", "gravidade_padrao": "leve"},
    {"doenca": "Obesidade Mórbida", "categoria": "metabolica", "gravidade_padrao": "moderado"},
    {"doenca": "Colesterol Alto", "categoria": "metabolica", "gravidade_padrao": "leve"},
    {"doenca": "Triglicerídeos Altos", "categoria": "metabolica", "gravidade_padrao": "leve"},
    {"doenca": "Esteatose Hepática", "categoria": "digestiva", "gravidade_padrao": "leve"},
    {"doenca": "Renal Crônica", "categoria": "metabolica", "gravidade_padrao": "grave"},
    {"doenca": "Doença de Chagas", "categoria": "infecciosa", "gravidade_padrao": "grave"},
]
# --- Preencher até >=200 com variantes ---
def _fill_doencas() -> list[dict]:
    cats = ["cardiovascular","respiratoria","metabolica","infecciosa","mental","oncologica","autoimune","ortopedica","neurologica","dermatologica"]
    gravs = ["leve","moderado","grave"]
    nomes_base = [d["doenca"] for d in DOENCAS]
    while len(DOENCAS) < 200:
        idx = len(DOENCAS)
        cat = cats[idx % len(cats)]
        grav = gravs[idx % len(gravs)]
        DOENCAS.append({
            "doenca": f"Doença {idx:03d} ({cat})",
            "categoria": cat,
            "gravidade_padrao": grav,
        })
    return DOENCAS

DOENCAS = _fill_doencas()

MEDICAMENTOS: list[dict] = [
    {"medicamento": "Metformina", "principio_ativo": "Metformina Fictícia", "classe": "antidiabético"},
    {"medicamento": "Losartana", "principio_ativo": "Losartana Fictícia", "classe": "anti-hipertensivo"},
    {"medicamento": "Fluoxetina", "principio_ativo": "Fluoxetina Fictícia", "classe": "antidepressivo"},
    {"medicamento": "Amoxicilina", "principio_ativo": "Amoxicilina Fictícia", "classe": "antibiótico"},
    {"medicamento": "Dipirona", "principio_ativo": "Dipirona Fictícia", "classe": "analgésico"},
    {"medicamento": "Omeprazol", "principio_ativo": "Omeprazol Fictício", "classe": "antiácido"},
    {"medicamento": "Ibuprofeno", "principio_ativo": "Ibuprofeno Fictício", "classe": "anti-inflamatório"},
    {"medicamento": "Prednisona", "principio_ativo": "Prednisona Fictícia", "classe": "corticoide"},
    {"medicamento": "Insulina", "principio_ativo": "Insulina Fictícia", "classe": "antidiabético"},
    {"medicamento": "Atorvastatina", "principio_ativo": "Atorvastatina Fictícia", "classe": "antilipêmico"},
    {"medicamento": "Captopril", "principio_ativo": "Captopril Fictício", "classe": "anti-hipertensivo"},
    {"medicamento": "Sertralina", "principio_ativo": "Sertralina Fictícia", "classe": "antidepressivo"},
    {"medicamento": "Escitalopram", "principio_ativo": "Escitalopram Fictício", "classe": "antidepressivo"},
    {"medicamento": "Rivotril", "principio_ativo": "Clonazepam Fictício", "classe": "ansiolítico"},
    {"medicamento": "Ritalina", "principio_ativo": "Metilfenidato Fictício", "classe": "estimulante"},
    {"medicamento": "Dorflex", "principio_ativo": "Dorflex Fictício", "classe": "relaxante muscular"},
    {"medicamento": "Advil", "principio_ativo": "Ibuprofeno Fictício", "classe": "anti-inflamatório"},
    {"medicamento": "Cimegripe", "principio_ativo": "Cimegripe Inventado", "classe": "antigripal"},
    {"medicamento": "Paracetamol", "principio_ativo": "Paracetamol Fictício", "classe": "analgésico"},
    {"medicamento": "Dorflex", "principio_ativo": "Dorflex Inv.", "classe": "relaxante"},
]
while len(MEDICAMENTOS) < 100:
    i = len(MEDICAMENTOS)
    MEDICAMENTOS.append({
        "medicamento": f"Medicamento {i:03d} Fictício",
        "principio_ativo": f"Princípio Ativo {i:03d} Inventado",
        "classe": ["analgésico","antibiótico","anti-inflamatório","antidepressivo","anti-hipertensivo","antidiabético"][i % 6],
    })

CURSOS: list[dict] = [
    {"curso": "Ciência da Computação", "duracao_meses": 48, "modalidade": "bacharelado"},
    {"curso": "Engenharia Civil", "duracao_meses": 60, "modalidade": "bacharelado"},
    {"curso": "Administração", "duracao_meses": 48, "modalidade": "bacharelado"},
    {"curso": "Direito", "duracao_meses": 60, "modalidade": "bacharelado"},
    {"curso": "Medicina", "duracao_meses": 72, "modalidade": "bacharelado"},
    {"curso": "Enfermagem", "duracao_meses": 60, "modalidade": "bacharelado"},
    {"curso": "Psicologia", "duracao_meses": 60, "modalidade": "bacharelado"},
    {"curso": "Pedagogia", "duracao_meses": 48, "modalidade": "licenciatura"},
    {"curso": "Física", "duracao_meses": 48, "modalidade": "licenciatura"},
    {"curso": "Matemática", "duracao_meses": 48, "modalidade": "licenciatura"},
    {"curso": "Biologia", "duracao_meses": 48, "modalidade": "licenciatura"},
    {"curso": "Química", "duracao_meses": 48, "modalidade": "licenciatura"},
    {"curso": "Design", "duracao_meses": 48, "modalidade": "bacharelado"},
    {"curso": "Arquitetura", "duracao_meses": 60, "modalidade": "bacharelado"},
    {"curso": "Farmácia", "duracao_meses": 60, "modalidade": "bacharelado"},
    {"curso": "Odontologia", "duracao_meses": 60, "modalidade": "bacharelado"},
    {"curso": "Nutrição", "duracao_meses": 48, "modalidade": "bacharelado"},
    {"curso": "Fisioterapia", "duracao_meses": 48, "modalidade": "bacharelado"},
    {"curso": "Educação Física", "duracao_meses": 48, "modalidade": "licenciatura"},
    {"curso": "Jornalismo", "duracao_meses": 48, "modalidade": "bacharelado"},
    {"curso": "Relações Públicas", "duracao_meses": 48, "modalidade": "bacharelado"},
    {"curso": "Publicidade", "duracao_meses": 48, "modalidade": "bacharelado"},
    {"curso": "Técnico em Informática", "duracao_meses": 21, "modalidade": "tecnologo"},
    {"curso": "Técnico em Enfermagem", "duracao_meses": 21, "modalidade": "tecnologo"},
    {"curso": "Técnico em Contabilidade", "duracao_meses": 21, "modalidade": "tecnologo"},
    {"curso": "Técnico em Administração", "duracao_meses": 18, "modalidade": "tecnologo"},
    {"curso": "Gestão de RH", "duracao_meses": 24, "modalidade": "tecnologo"},
    {"curso": "Logística", "duracao_meses": 24, "modalidade": "tecnologo"},
    {"curso": "Análise e Desenvolvimento de Sistemas", "duracao_meses": 30, "modalidade": "tecnologo"},
    {"curso": "Redes de Computadores", "duracao_meses": 30, "modalidade": "tecnologo"},
    {"curso": "MBA em Gestão", "duracao_meses": 18, "modalidade": "pos_graduacao"},
    {"curso": "Pós em Data Science", "duracao_meses": 12, "modalidade": "pos_graduacao"},
    {"curso": "Pós em Direito Digital", "duracao_meses": 12, "modalidade": "pos_graduacao"},
    {"curso": "Residência Médica", "duracao_meses": 24, "modalidade": "pos_graduacao"},
    {"curso": "Mestrado Acadêmico", "duracao_meses": 24, "modalidade": "pos_graduacao"},
    {"curso": "Doutorado", "duracao_meses": 48, "modalidade": "pos_graduacao"},
    {"curso": "Especialização em Pediatria", "duracao_meses": 24, "modalidade": "pos_graduacao"},
    {"curso": "Especialização em Ortopedia", "duracao_meses": 24, "modalidade": "pos_graduacao"},
    {"curso": "Linguagem Python", "duracao_meses": 3, "modalidade": "tecnologo"},
    {"curso": "Inglês Intermediário", "duracao_meses": 12, "modalidade": "tecnologo"},
    {"curso": "Espanhol Básico", "duracao_meses": 6, "modalidade": "tecnologo"},
    {"curso": "Culinária Profissional", "duracao_meses": 9, "modalidade": "tecnologo"},
    {"curso": "Barbeiro Profissional", "duracao_meses": 6, "modalidade": "tecnologo"},
    {"curso": "Estética Automotiva", "duracao_meses": 6, "modalidade": "tecnologo"},
    {"curso": "Fotografia", "duracao_meses": 9, "modalidade": "tecnologo"},
    {"curso": "Maquiagem Profissional", "duracao_meses": 6, "modalidade": "tecnologo"},
    {"curso": "Programação Web", "duracao_meses": 6, "modalidade": "tecnologo"},
    {"curso": "Marketing Digital", "duracao_meses": 9, "modalidade": "tecnologo"},
    {"curso": "Contabilidade", "duracao_meses": 48, "modalidade": "bacharelado"},
    {"curso": "Engenharia de Produção", "duracao_meses": 60, "modalidade": "bacharelado"},
]

_RACA_CAO = [
    "Labrador","Pastor Alemão","Bulldog","Poodle","Pit Bull","Rottweiler",
    "Samoieda","Golden Retriever","Shih Tzu","Pinscher","Schnauzer",
    "Cocker Spaniel","Boxer","Vira-lata","Mastiff","Husky Siberiano",
    "Dálmata","Akita","Border Collie","Chihuahua","Beagle","Maltes",
]
_RACA_GATO = [
    "Persa","Siamês","Maine Coon","Sphynx","Ragdoll","Bengal",
    "Abissínio","Britânico","Angorá","Somali","Munchkin","Bombay",
]
_RACA_OUTROS = [
    "Coelho Holandês","Hamster Sírio","Tartaruga Amarela","Calopsita",
    "Periquito","Cacatua","Peixe-palhaço","Iguana","Porco-guine",
]

RACAS_PET: list[dict] = (
    [{"tipo": "cao", "raca": r} for r in _RACA_CAO]
    + [{"tipo": "gato", "raca": r} for r in _RACA_GATO]
    + [{"tipo": "outros", "raca": r} for r in _RACA_OUTROS]
)

PARTIDOS: list[dict] = [
    {"sigla": "PEV", "nome": "Partido Ecologista Virtual", "espectro": "esquerda"},
    {"sigla": "PTR", "nome": "Partido Trabalhista Revolucionário", "espectro": "esquerda"},
    {"sigla": "PSF", "nome": "Partido Socialista Fictício", "espectro": "esquerda"},
    {"sigla": "PSB", "nome": "Partido Social Brasileiro", "espectro": "esquerda"},
    {"sigla": "PV", "nome": "Partido Verde Virtual", "espectro": "esquerda"},
    {"sigla": "PCB", "nome": "Partido Comunista Brasileiro Virtual", "espectro": "esquerda"},
    {"sigla": "PSOL", "nome": "Partido Socialismo e Liberdade Virtual", "espectro": "esquerda"},
    {"sigla": "REDE", "nome": "Rede Sustentabilidade Virtual", "espectro": "esquerda"},
    {"sigla": "MDB", "nome": "Movimento Democrático Brasileiro Virtual", "espectro": "centro"},
    {"sigla": "PSDB", "nome": "Partido Social Democrático Brasileiro Virtual", "espectro": "centro"},
    {"sigla": "DEM", "nome": "Democratas Virtual", "espectro": "direita"},
    {"sigla": "NOVO", "nome": "Partido Novo", "espectro": "direita"},
    {"sigla": "PL", "nome": "Partido Liberal Virtual", "espectro": "direita"},
    {"sigla": "Republicanos", "nome": "Republicanos Virtual", "espectro": "direita"},
    {"sigla": "PODEMOS", "nome": "Podemos Virtual", "espectro": "direita"},
    {"sigla": "PATRIOTA", "nome": "Patriota Virtual", "espectro": "direita"},
    {"sigla": "PTB", "nome": "Partido Trabalhista Brasileiro Virtual", "espectro": "centro"},
    {"sigla": "PSC", "nome": "Partido Social Cristão Virtual", "espectro": "direita"},
    {"sigla": "PRTB", "nome": "Partido Renovador Trabalhista Brasileiro", "espectro": "centro"},
    {"sigla": "DC", "nome": "Democracia Cristã Virtual", "espectro": "centro"},
]

# --------------------------------------------------------------------------- #
# Salário mínimo histórico (2000-2024)
# --------------------------------------------------------------------------- #
MIN_WAGE_HISTORY: list[dict] = [
    {"year": 2000, "min_wage": 151.00},
    {"year": 2001, "min_wage": 180.00},
    {"year": 2002, "min_wage": 200.00},
    {"year": 2003, "min_wage": 240.00},
    {"year": 2004, "min_wage": 260.00},
    {"year": 2005, "min_wage": 300.00},
    {"year": 2006, "min_wage": 350.00},
    {"year": 2007, "min_wage": 380.00},
    {"year": 2008, "min_wage": 415.00},
    {"year": 2009, "min_wage": 465.00},
    {"year": 2010, "min_wage": 510.00},
    {"year": 2011, "min_wage": 545.00},
    {"year": 2012, "min_wage": 622.00},
    {"year": 2013, "min_wage": 678.00},
    {"year": 2014, "min_wage": 724.00},
    {"year": 2015, "min_wage": 788.00},
    {"year": 2016, "min_wage": 880.00},
    {"year": 2017, "min_wage": 937.00},
    {"year": 2018, "min_wage": 954.00},
    {"year": 2019, "min_wage": 998.00},
    {"year": 2020, "min_wage": 1045.00},
    {"year": 2021, "min_wage": 1100.00},
    {"year": 2022, "min_wage": 1212.00},
    {"year": 2023, "min_wage": 1320.00},
    {"year": 2024, "min_wage": 1412.00},
]

# --------------------------------------------------------------------------- #
# IPCA mensal (fictício mas plausível, 2002-2024)
# --------------------------------------------------------------------------- #
import math as _math


def _build_ipca() -> list[dict]:
    rows: list[dict] = []
    for year in range(2002, 2025):
        base = 4.5 + 0.8 * (_math.sin((year - 2002) * 0.27) + 1)
        for month in range(1, 13):
            seasonal = 0.3 * _math.sin((month / 12) * 2 * _math.pi) + 0.15
            ipca = round(base + seasonal + 0.3 * ((month * 7 + year * 3) % 10) / 10, 2)
            rows.append({"year": year, "month": month, "ipca": ipca})
    return rows


IPCA_MENSAL: list[dict] = _build_ipca()

if __name__ == "__main__":
    print(f"MALE_FIRST_NAMES: {len(MALE_FIRST_NAMES)}")
    print(f"FEMALE_FIRST_NAMES: {len(FEMALE_FIRST_NAMES)}")
    print(f"SURNAMES: {len(SURNAMES)}")
    print(f"CIDADES: {len(CIDADES)}")
    print(f"BAIRROS: {len(BAIRROS)}")
    print(f"PROFISSOES: {len(PROFISSOES)}")
    print(f"DOENCAS: {len(DOENCAS)}")
    print(f"MEDICAMENTOS: {len(MEDICAMENTOS)}")
    print(f"CURSOS: {len(CURSOS)}")
    print(f"RACAS_PET: {len(RACAS_PET)}")
    print(f"IPCA_MENSAL: {len(IPCA_MENSAL)}")
    print(f"EMPRESAS CNPJs all valid: {all(_valid_cnpj(e['cnpj']) for e in EMPRESAS)}")