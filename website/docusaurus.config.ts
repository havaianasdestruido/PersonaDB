import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const ORG = 'havaianasdestruido';
const REPO = 'PersonaDB';

const config: Config = {
  title: 'PersonaDB',
  tagline:
    'Motor determinístico de geração de dados sintéticos relacionais para personas fictícias brasileiras',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  url: `https://${ORG}.github.io`,
  baseUrl: `/${REPO}/`,

  organizationName: ORG,
  projectName: REPO,
  deploymentBranch: 'gh-pages',
  trailingSlash: false,

  onBrokenLinks: 'throw',

  i18n: {
    defaultLocale: 'pt-BR',
    locales: ['pt-BR'],
    localeConfigs: {
      'pt-BR': {label: 'Português (Brasil)', htmlLang: 'pt-BR'},
    },
  },

  markdown: {
    // `detect` mantém os arquivos .md em CommonMark (seguro para páginas
    // geradas a partir de docstrings) e habilita MDX apenas em .mdx.
    format: 'detect',
    mermaid: true,
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  themes: [
    '@docusaurus/theme-mermaid',
    [
      require.resolve('@easyops-cn/docusaurus-search-local'),
      {
        hashed: true,
        language: ['pt', 'en'],
        indexBlog: false,
        docsRouteBasePath: '/docs',
        highlightSearchTermsOnTargetPage: true,
        searchResultLimits: 10,
      },
    ],
  ],

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl: `https://github.com/${ORG}/${REPO}/tree/main/website/`,
          remarkPlugins: [remarkMath],
          rehypePlugins: [rehypeKatex],
          showLastUpdateTime: true,
          breadcrumbs: true,
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
        sitemap: {
          lastmod: 'date',
          changefreq: 'weekly',
        },
      } satisfies Preset.Options,
    ],
  ],

  stylesheets: [
    {
      href: 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css',
      type: 'text/css',
      integrity:
        'sha384-n8MVd4RsNIU0tAv4ct0nTaAbDJwPJzDEaqSD1odI+WdtXRGWt2kTvGFasHpSy3SV',
      crossorigin: 'anonymous',
    },
  ],

  themeConfig: {
    image: 'img/personadb-social-card.png',
    colorMode: {
      respectPrefersColorScheme: true,
    },
    mermaid: {
      theme: {light: 'neutral', dark: 'dark'},
    },
    docs: {
      sidebar: {hideable: true, autoCollapseCategories: false},
    },
    navbar: {
      title: 'PersonaDB',
      logo: {
        alt: 'PersonaDB',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docsSidebar',
          position: 'left',
          label: 'Documentação',
        },
        {
          type: 'docSidebar',
          sidebarId: 'apiSidebar',
          position: 'left',
          label: 'Referência de API',
        },
        {
          type: 'docSidebar',
          sidebarId: 'schemaSidebar',
          position: 'left',
          label: 'Schema SQL',
        },
        {
          href: `https://github.com/${ORG}/${REPO}`,
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Documentação',
          items: [
            {label: 'Introdução', to: '/docs/intro'},
            {label: 'Instalação', to: '/docs/comecando/instalacao'},
            {label: 'Primeiro dataset', to: '/docs/comecando/primeiro-dataset'},
            {label: 'Arquitetura', to: '/docs/arquitetura/visao-geral'},
          ],
        },
        {
          title: 'Referência',
          items: [
            {label: 'Motores matemáticos', to: '/docs/motores/'},
            {label: 'Geradores de domínio', to: '/docs/geradores/'},
            {label: 'Referência de API', to: '/docs/referencia-api/'},
            {label: 'Schema relacional', to: '/docs/schema/'},
          ],
        },
        {
          title: 'Projeto',
          items: [
            {label: 'GitHub', href: `https://github.com/${ORG}/${REPO}`},
            {
              label: 'Issues',
              href: `https://github.com/${ORG}/${REPO}/issues`,
            },
            {label: 'Ética e limitações', to: '/docs/projeto/etica-e-limitacoes'},
            {label: 'Licença MIT', href: `https://github.com/${ORG}/${REPO}/blob/main/LICENSE`},
          ],
        },
      ],
      copyright: `PersonaDB — dados 100% fictícios. Documentação construída com Docusaurus. © ${new Date().getFullYear()}.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'python', 'sql', 'json', 'ini', 'docker', 'diff'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
