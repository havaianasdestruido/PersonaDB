import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import CodeBlock from '@theme/CodeBlock';
import Heading from '@theme/Heading';

import stats from '@site/src/data/stats.json';
import styles from './index.module.css';

const metrics: {value: string; label: string}[] = [
  {value: String(stats.tables), label: 'tabelas PostgreSQL'},
  {value: String(stats.domains), label: 'domínios de vida'},
  {value: String(stats.generators), label: 'geradores'},
  {value: String(stats.engines), label: 'motores matemáticos'},
  {value: String(stats.rules), label: 'regras de validação'},
  {value: stats.pythonLines.toLocaleString('pt-BR'), label: 'linhas de Python'},
];

const features: {title: string; body: ReactNode; to: string}[] = [
  {
    title: 'Determinístico de ponta a ponta',
    body: (
      <>
        Uma semente mestre e um <code>fork</code> BLAKE2b por persona e domínio: a mesma execução
        produz o mesmo dataset, em qualquer máquina, hoje ou daqui a um ano.
      </>
    ),
    to: '/docs/arquitetura/determinismo',
  },
  {
    title: 'Coerente entre domínios',
    body: (
      <>
        Tipo sanguíneo que respeita Punnett, salário acima do piso do ano, antecedente criminal que
        bloqueia setores, óbito que encerra a linha do tempo.
      </>
    ),
    to: '/docs/validadores/',
  },
  {
    title: 'Modelos explícitos',
    body: (
      <>
        Markov para mobilidade social, Mincer para salários, Gompertz–Makeham para mortalidade,
        Poisson para fecundidade, gravidade para migração — todos documentados.
      </>
    ),
    to: '/docs/motores/',
  },
  {
    title: 'Documentação viva',
    body: (
      <>
        Referência de API e catálogo do schema são gerados do código a cada build: as docstrings e
        os DDL do repositório são a fonte da verdade.
      </>
    ),
    to: '/docs/referencia-api/',
  },
];

function Hero() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={styles.hero}>
      <div className="container">
        <Heading as="h1" className={styles.heroTitle}>
          {siteConfig.title}
        </Heading>
        <p className={styles.heroTagline}>{siteConfig.tagline}</p>
        <p className={styles.heroNote}>
          {stats.tables} tabelas · {stats.domains} domínios · {stats.columns} colunas ·{' '}
          {stats.foreignKeys} chaves estrangeiras — 100% fictícias e reproduzíveis.
        </p>
        <div className={styles.heroButtons}>
          <Link className="button button--primary button--lg" to="/docs/intro">
            Começar
          </Link>
          <Link
            className="button button--secondary button--lg"
            to="/docs/comecando/primeiro-dataset">
            Gerar um dataset
          </Link>
          <Link
            className="button button--outline button--secondary button--lg"
            href="https://github.com/havaianasdestruido/PersonaDB">
            GitHub
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home(): ReactNode {
  return (
    <Layout
      title="Dados sintéticos brasileiros, determinísticos e coerentes"
      description="PersonaDB — motor determinístico de geração de dados sintéticos relacionais para personas fictícias brasileiras em 257 tabelas PostgreSQL.">
      <Hero />
      <main>
        <section className={styles.metrics}>
          <div className="container">
            <div className="row">
              {metrics.map((m) => (
                <div key={m.label} className={clsx('col col--2', styles.metric)}>
                  <div className={styles.metricValue}>{m.value}</div>
                  <div className={styles.metricLabel}>{m.label}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className={styles.section}>
          <div className="container">
            <div className="row">
              <div className="col col--6">
                <Heading as="h2">Do zero ao dataset em dois comandos</Heading>
                <p>
                  O pipeline roda inteiramente em memória: o PostgreSQL só entra quando você quiser
                  consultar os dados em SQL.
                </p>
                <CodeBlock language="bash">
                  {`python3 -m pip install -e "persona_db[dev,parquet]"

python3 -m persona_db.scripts.generate \\
  --personas 200 --seed 42 \\
  --output dataset.json --html-report report.html`}
                </CodeBlock>
              </div>
              <div className="col col--6">
                <Heading as="h2">Validação embutida</Heading>
                <p>
                  Dez verificações percorrem o dataset gerado. Qualquer invariante quebrada reprova a
                  execução com <code>exit 1</code> — e o JSON não é gravado.
                </p>
                <CodeBlock language="json">
                  {`{"personas": 200, "seed": 42, "total_rows": 68342,
 "validation": {"passed": true,
   "violation_count": 0,
   "overall_consistency_pct": 100.0}}`}
                </CodeBlock>
              </div>
            </div>
          </div>
        </section>

        <section className={styles.section}>
          <div className="container">
            <div className="row">
              {features.map((f) => (
                <div key={f.title} className="col col--6">
                  <div className={styles.card}>
                    <Heading as="h3">{f.title}</Heading>
                    <p>{f.body}</p>
                    <Link to={f.to}>Ler mais →</Link>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className={clsx(styles.section, styles.disclaimer)}>
          <div className="container">
            <Heading as="h2">Nada aqui é real</Heading>
            <p>
              Nomes, documentos, endereços, empresas, hospitais e processos são inventados. O
              PersonaDB não ingere, anonimiza nem deriva dados de pessoas reais, e seus modelos não
              devem ser usados para decisões sobre indivíduos.
            </p>
            <Link to="/docs/projeto/etica-e-limitacoes">Ética e limitações →</Link>
          </div>
        </section>
      </main>
    </Layout>
  );
}
