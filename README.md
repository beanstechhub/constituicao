# constituicao.tech

> Integridade de documentos profissionais na era da IA generativa. Fundamentada na eficácia horizontal dos direitos fundamentais.

[![Licença](https://img.shields.io/badge/licen%C3%A7a-Apache--2.0-blue)](LICENSE)
[![Versão](https://img.shields.io/badge/vers%C3%A3o-0.2.1-orange)](#)
[![Live](https://img.shields.io/badge/live-constituicao.tech-brightgreen)](https://constituicao.tech)
[![Built with Claude](https://img.shields.io/badge/built%20with-Claude%20Opus-blueviolet)](https://anthropic.com)
[![Frameworks](https://img.shields.io/badge/alinhado-OWASP%20%7C%20NIST%20%7C%20MITRE-green)](#)

## Fundamento constitucional

Os direitos fundamentais não incidem apenas na relação vertical Estado–cidadão. A **eficácia horizontal** (*Drittwirkung*) impõe que princípios como o **devido processo legal**, a **boa-fé objetiva** e o **dever de cooperação** vinculem também as relações entre particulares.

Quando um sistema de IA processa documentos em fluxos institucionais — triagem de processos, análise de petições, due diligence — e uma parte embutiu texto desenhado para manipular a máquina, isso viola:

- O **princípio da cooperação** (art. 6º do CPC) — o dever de que todos os sujeitos do processo contribuam para decisão justa, célere e efetiva.
- O **devido processo legal substancial** (art. 5º, LIV da CF) — não apenas como garantia contra o Estado, mas como exigência de lealdade processual entre as partes.
- A **boa-fé objetiva** (art. 5º do CPC) — ninguém deve se comportar de forma incompatível com um padrão ético mínimo.
- A **paridade de armas** (art. 7º do CPC) — o juiz deve assegurar às partes igualdade de tratamento. A parte que manipula IA obtém vantagem indevida sobre a parte que joga limpo.

O nome desta iniciativa não é metáfora. A Constituição fundamenta o direito a um processo leal — inclusive quando máquinas participam dele.

## O problema

Sistemas de IA estão sendo introduzidos em fluxos que dependem de documentos: análise de petições por assistentes jurídicos, triagem automatizada de processos, resumos de laudos periciais, due diligence financeira assistida por LLM.

Quando a entrada desses sistemas é um documento produzido por parte interessada, abre-se um vetor de ataque: **indirect prompt injection**. A parte embutiu texto desenhado para manipular o sistema automatizado que processará o documento.

Esse vetor está documentado em:
- **OWASP LLM Top 10 (2025)** — categoria LLM01: Prompt Injection
- **NIST AI 100-2e2025** — Adversarial Machine Learning Taxonomy
- **MITRE ATLAS** — Adversarial Threat Landscape for AI Systems

Mas faltava uma ferramenta que traduzisse esses frameworks para o profissional brasileiro. A integridade do artefato — o documento — ficava desprotegida.

## O que esta iniciativa faz

- Disponibiliza ferramenta gratuita em [constituicao.tech](https://constituicao.tech) para verificar documentos antes que sejam processados por IA.
- Mantém **taxonomia pública** dos vetores de comprometimento, mapeada a OWASP/NIST/MITRE.
- Publica os **padrões de detecção** sob licença aberta, sujeitos a revisão e contribuição.
- Documenta a **calibração de severidade** e os critérios de classificação de risco.
- Comunica transparentemente a **taxa estimada de falso positivo (3-7%)**.

## Os 4 Módulos

| # | Módulo | Protege | Latência |
|---|--------|---------|----------|
| 1 | **Prompt Injection** | Documentos processados por LLMs (11 categorias OWASP) | <1s |
| 2 | **Integridade Acadêmica** | Autenticidade autoral via estilometria (10 features) | <200ms |
| 3 | **Assinatura Digital** | Autenticidade criptográfica de PDFs (3 camadas) | <500ms |
| 4 | **Fraud Shield** | Fraude financeira em tempo real (12 regras Go) | <100μs |

**Live:** https://constituicao.tech
**Validação (Colab):** [Notebook com 34 testes + benchmarks](https://colab.research.google.com/github/beanstechhub/constituicao/blob/main/colab_validation.ipynb)

## O que esta iniciativa NÃO faz

- Não dá veredito binário ("fraudulento" vs "limpo"). Entrega nível de risco e justificativa.
- Não armazena documentos submetidos. Não treina modelos com eles.
- Não substitui revisão humana. É ferramenta de apoio.
- Não detecta alucinação de IA (citação inventada, jurisprudência fictícia). Planejado para v0.4.
- Não pretende ser à prova de adversário motivado — padrões podem ser contornados.

## Aviso sobre falsos positivos

Falsos positivos são esperados e tratados como parte do design. O estado da arte em detecção de prompt injection atinge ~89% de mitigação preservando ~94% da funcionalidade legítima — portanto **~5-6% de falso positivo é o piso tecnológico atual**.

Documentos que discutem IA, citam exemplos de ataques, ou usam linguagem imperativa típica do domínio podem gerar alertas. Cada achado inclui justificativa e confiança para que o humano avalie.

Ver: [docs/FALSOS-POSITIVOS.md](docs/FALSOS-POSITIVOS.md)

## Arquitetura

```
┌──────────┐    HTTPS    ┌──────────────┐         ┌─────────────────┐
│  Browser │────────────▶│  Cloud Armor │────────▶│  API (Go)       │
│  (web)   │             │  + LB        │         │  rate limiting  │
└──────────┘             └──────────────┘         │  validação      │
                                                  └────────┬────────┘
                                                           │ interno
                                                           ▼
                                                  ┌─────────────────┐
                                                  │ Detector (Py)   │
                                                  │ FastAPI          │
                                                  │ + extração       │
                                                  │ + padrões OWASP  │
                                                  │ + scoring        │
                                                  └─────────────────┘
```

- **`api-go/`** — gateway HTTP em Go: rate limiting, CORS, segurança de borda. Stateless. Cloud Run.
- **`detector-py/`** — núcleo de detecção em Python: normalização Unicode, padrões regex calibrados por OWASP/NIST/MITRE, scoring saturante. Cloud Run ingress privado.
- **`web/`** — landing + analisador estático. Cloud Storage + CDN.
- **`infra/`** — scripts de deploy GCP, Cloud Armor.
- **`docs/`** — privacidade, falsos positivos, API, taxonomia detalhada.

## Como rodar localmente

```bash
docker compose up --build
# Web em http://localhost:3000
# API em http://localhost:8080
# Detector em http://localhost:8000
```

## Como rodar os testes

```bash
cd detector-py
pip install -r requirements.txt pytest
PYTHONPATH=. pytest tests/ -v
```

A suite inclui:
- **True positives** para cada categoria de vetor (OWASP LLM01, NIST, MITRE).
- **True negatives críticos:** petição jurídica legítima, parecer técnico, pedido de procedência padrão, artigo acadêmico sobre IA.
- **Casos limite:** texto vazio, repetições saturantes, serialização, determinismo.

## Como contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes. Em resumo:

1. **Contraexemplos** — submeta documentos (anonimizados) que produzem falso positivo/negativo.
2. **Novos vetores** — padrões não cobertos, com referência bibliográfica.
3. **Código** — PRs com testes, true negatives obrigatórios, explicabilidade mantida.

## Roadmap público

| Versão | Escopo | Status |
|--------|--------|--------|
| **v0.2** (atual) | Detecção alinhada a OWASP/NIST/MITRE. PT-BR + EN. 11 categorias. | Em revisão pública |
| v0.3 | Detecção semântica (LLM como segundo opinião sobre intencionalidade) | Planejado |
| v0.4 | Verificação de citações jurídicas (STJ, STF, TJs) | Planejado |
| v0.5 | Adaptação setorial: financeiro, pericial, regulatório | Planejado |
| v1.0 | Dataset público rotulado, métricas F1 por categoria, benchmark | Planejado |

## Princípios

1. **Transparência sobre opacidade.** Código aberto, metodologia pública, calibração documentada.
2. **Humano sobre máquina.** Toda decisão final é humana. A ferramenta informa, não decide.
3. **Explicabilidade sobre acurácia.** Preferimos um detector que erra explicando do que um que acerta sem justificar.
4. **Privacidade sobre conveniência.** Não armazenamos nada. Sem cadastro. Sem analytics invasivo.
5. **Comum sobre privado.** Iniciativa de bem comum, não produto comercial.

## Licença

[Apache License 2.0](LICENSE). Use, modifique, redistribua — desde que mantenha aviso de licença.

## Por que isso existe

Porque a manipulação de sistemas automatizados por meio de documentos comprometidos é uma violação do devido processo legal substancial. Em um mundo onde produzir um documento plausível ficou trivial com IA generativa, a paridade de armas exige que a verificação seja igualmente trivial — e gratuita, e aberta, e auditável.

Não é a única defesa necessária. Mas é uma que faltava, e que a Constituição demanda.

---

**constituicao.tech** · Beans Tech · Apache 2.0 · Built with Claude (Anthropic)
