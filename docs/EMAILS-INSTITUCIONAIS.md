# E-mails Institucionais — constituicao.tech

Modelos de e-mail para envio a tribunais, CNJ, MPs e órgãos de controle.

**Objetivo:** comunicar a existência da iniciativa com clareza de que NÃO é autopromoção, mas alerta institucional sobre um risco real à paridade de armas e ao devido processo legal substancial.

---

## E-MAIL 1 — Para Tribunais (TJ, TRF, TRT, TST, STJ)

**Assunto:** Alerta técnico — vetor de manipulação de sistemas de IA em documentos processuais

**Destinatários sugeridos:**
- Secretaria de Tecnologia da Informação de cada tribunal
- Corregedoria (quando relevante)
- Comissão de Inteligência Artificial (onde existir)

---

Prezada Secretaria / Presidência,

Escrevo para comunicar a existência de um risco técnico documentado que afeta diretamente a integridade de fluxos em que sistemas de inteligência artificial processam documentos de partes.

**O risco**: quando um sistema de IA (assistente jurídico, ferramenta de triagem, resumo automatizado) lê um documento produzido por parte interessada, essa parte pode embutir texto desenhado para manipular a análise da máquina — vetor conhecido tecnicamente como *indirect prompt injection*. Esse ataque está classificado como o risco nº 1 no OWASP LLM Top 10 (2025), documentado pelo NIST em AI 100-2e2025 e catalogado pelo MITRE ATLAS.

**A implicação processual**: a parte que manipula o sistema obtém vantagem indevida sobre a que não o faz. Isso viola a paridade de armas (art. 7º do CPC), o princípio da cooperação (art. 6º do CPC), a boa-fé objetiva (art. 5º do CPC) e o devido processo legal substancial (art. 5º, LIV da CF), cuja eficácia horizontal incide entre particulares.

**O que estamos fazendo**: desenvolvemos o [constituicao.tech](https://constituicao.tech) — plataforma gratuita e de código aberto com 4 módulos defensivos:

1. **Detecção de Prompt Injection** — 13 padrões, normalização Unicode/leetspeak, alinhado a OWASP/NIST/MITRE
2. **Integridade Acadêmica** — análise estilométrica com 10 features estatísticas, sem API externa
3. **Verificação de Assinatura Digital** — validação multicamada de PDFs, detecta 8 vetores de ataque (ByteRange manipulation, hash mismatch, assinaturas cosméticas, SHA-1 depreciado)
4. **Fraud Shield** — engine Go com 12 regras antifraude, incluindo detecção de structuring (COAF) e lavagem via apostas

O módulo 3 é particularmente relevante para tribunais: detecta PDFs com assinaturas digitais forjadas, copiadas ou cosméticas antes que produzam efeitos processuais.

**O que NÃO estamos fazendo**: não se trata de produto comercial, nem de autopromoção. Não há cobrança, não há captação de dados, não há interesse comercial. A plataforma é de bem comum e está em revisão pública sob licença Apache 2.0. 61+ testes automatizados, CI/CD, benchmarks publicados.

**O que pedimos**: que este tribunal avalie se os sistemas de IA eventualmente utilizados em seus fluxos internos estão protegidos contra esse vetor. A ferramenta está disponível para teste imediato e a metodologia está documentada para auditoria.

Repositório público: github.com/constituicaotech/constituicao-tech
Metodologia: constituicao.tech/metodologia
Contato técnico: oi@constituicao.tech

Respeitosamente,
[Seu nome]
[Sua qualificação]

---

## E-MAIL 2 — Para o CNJ (Conselho Nacional de Justiça)

**Assunto:** Contribuição técnica — proteção da integridade processual contra manipulação de IA via documentos

**Destinatários sugeridos:**
- Departamento de Pesquisas Judiciárias (DPJ)
- Comitê de Inteligência Artificial do Poder Judiciário
- Secretaria de Gestão Tecnológica

---

Ao Conselho Nacional de Justiça,

Dirijo-me a este Conselho para apresentar contribuição técnica relativa a um risco emergente que afeta a integridade de sistemas de inteligência artificial utilizados no Poder Judiciário.

**Contexto**: a Resolução CNJ nº 525/2023 disciplinou o uso de IA no Judiciário e sinalizou a importância de governança sobre essas ferramentas. No entanto, um vetor específico de comprometimento permanece pouco discutido: a possibilidade de que documentos produzidos por partes contenham instruções ocultas desenhadas para manipular sistemas de IA que os processem — o chamado *indirect prompt injection*, classificado como risco nº 1 pelo OWASP LLM Top 10 (2025).

**O problema em termos constitucionais**: quando uma parte embutiu manipulação que altera o comportamento de um sistema automatizado utilizado na jurisdição, a eficácia horizontal dos direitos fundamentais impõe reconhecer violação ao devido processo legal substancial. Não se trata de hipótese acadêmica — os vetores de ataque estão documentados, catalogados e são reprodutíveis.

**A contribuição**: desenvolvemos o constituicao.tech, plataforma gratuita e de código aberto com 4 módulos defensivos: (1) detecção de prompt injection, (2) integridade acadêmica via estilometria, (3) verificação de assinatura digital em PDFs — detectando assinaturas forjadas, cosméticas e manipulações de ByteRange, e (4) fraud shield com detecção de structuring e lavagem.

Para o Judiciário, destacamos especialmente os módulos 1 e 3: documentos com injection manipulam assistentes de IA; PDFs com assinaturas falsificadas produzem efeitos processuais indevidos. Ambos são verificáveis pela ferramenta.

A metodologia é pública, alinhada a frameworks internacionais (OWASP, NIST AI 100-2e2025, MITRE ATLAS), 61+ testes automatizados. Não armazenamos documentos, não cobramos, não temos interesse comercial.

**Sugestão**: que o CNJ avalie a inclusão de verificação de integridade contra prompt injection e de autenticidade de assinaturas digitais como requisito ou recomendação nas diretrizes de governança de IA do Judiciário. Estamos à disposição para contribuir tecnicamente com qualquer grupo de trabalho nesse sentido.

Não se trata de autopromoção. Trata-se de paridade de armas — princípio que o CNJ tem o papel institucional de proteger em escala nacional.

Repositório: github.com/constituicaotech/constituicao-tech
Ferramenta: constituicao.tech
Contato: oi@constituicao.tech

Respeitosamente,
[Seu nome]
[Sua qualificação]

---

## E-MAIL 3 — Para o MPF (Ministério Público Federal) e PGR

**Assunto:** Alerta técnico — vulnerabilidade de sistemas de IA a manipulação documental e implicações para a atuação ministerial

**Destinatários sugeridos:**
- Secretaria de Cooperação Internacional e Atuação Institucional
- Câmaras de Coordenação e Revisão (especialmente 3ª CCR — Consumidor e Ordem Econômica; 1ª CCR — Constitucional)
- Grupo de Trabalho sobre Inteligência Artificial (se existir)
- Gabinete do Procurador-Geral da República (para ciência)

---

Ao Ministério Público Federal,

Comunico a existência de risco técnico relevante para a atuação ministerial em contextos que envolvam sistemas de inteligência artificial processando documentos de partes.

**O risco**: indirect prompt injection — possibilidade de que documentos submetidos a sistemas de IA contenham instruções ocultas para manipular a análise automatizada. Catalogado como risco nº 1 pelo OWASP LLM Top 10 (2025), documentado pelo NIST (AI 100-2e2025) e MITRE ATLAS.

**Relevância para o MP**:
1. Se o próprio Parquet utiliza ferramentas de IA para triagem ou análise de documentos recebidos, está vulnerável a prompt injection.
2. Se partes adversas em ações de improbidade, ações civis públicas ou ações penais utilizam esse vetor, a integridade da instrução probatória pode ser comprometida.
3. Se o Judiciário utiliza IA para assessorar decisões, o MP tem interesse institucional em que esses sistemas não sejam manipuláveis.
4. **Módulo de Fraud Shield**: detecta structuring (fracionamento para evadir COAF), lavagem via apostas esportivas (round-trip, smurfing, syndicate betting), e velocidade anômala de transações — diretamente relevante para a 3ª CCR e para investigações de lavagem de dinheiro.

**Implicação constitucional**: a eficácia horizontal dos direitos fundamentais, combinada com o dever de lealdade processual (art. 5º do CPC) e o respeito ao devido processo legal substancial, impõe que medidas de proteção existam. A parte que manipula um sistema automatizado obtém vantagem processual indevida — violação que o Ministério Público tem legitimidade para combater como fiscal da ordem jurídica (art. 176 do CPC).

**O que oferecemos**: o constituicao.tech é plataforma gratuita e de código aberto com 4 módulos: (1) prompt injection, (2) integridade acadêmica, (3) verificação de assinatura digital, e (4) fraud shield com regras anti-lavagem. Não é produto comercial. Não há interesse econômico. A metodologia é pública e auditável. 61+ testes. Estamos à disposição para apresentar tecnicamente a qualquer grupo de trabalho ou procurador interessado.

Repositório: github.com/constituicaotech/constituicao-tech
Ferramenta: constituicao.tech
Contato: oi@constituicao.tech

Respeitosamente,
[Seu nome]
[Sua qualificação]

---

## E-MAIL 4 — Para Chefes de Ministério Público Estadual (PGJ)

**Assunto:** Contribuição técnica — risco de manipulação de IA em fluxos documentais e paridade de armas

**Destinatários sugeridos:**
- Gabinete do Procurador-Geral de Justiça de cada estado
- Centro de Apoio Operacional (CAO) de Defesa do Patrimônio Público (onde existir)
- Núcleo de Inovação / Tecnologia (onde existir)

---

Ao Procurador-Geral de Justiça,

Permito-me apresentar contribuição técnica sobre risco emergente que pode afetar a atuação do Ministério Público em qualquer feito que envolva processamento automatizado de documentos.

**Resumo**: documentos produzidos por partes podem conter texto invisível ou disfarçado que manipula sistemas de inteligência artificial. Esse vetor (indirect prompt injection) é o risco nº 1 classificado pela OWASP para sistemas baseados em modelos de linguagem. Está documentado pelo NIST e catalogado pelo MITRE.

**Cenário concreto para o MP estadual**: um réu em ação de improbidade embute instrução oculta em petição processada por assistente jurídico automatizado do gabinete. O sistema, influenciado pela manipulação, produz resumo favorável ao réu. O assessor que lê o resumo pode ser induzido a erro sem perceber.

**O que existe para proteger**: desenvolvemos o constituicao.tech — ferramenta gratuita, código aberto, sem armazenamento de dados, que detecta esses vetores. Alinhada a OWASP, NIST e MITRE. Não é produto comercial. O objetivo é paridade de armas e respeito ao devido processo legal substancial, cuja eficácia horizontal incide entre particulares.

**O que pedimos**: ciência institucional do risco e, se pertinente, avaliação pela área técnica sobre medidas preventivas nos fluxos internos que envolvam IA.

Ferramenta: constituicao.tech
Repositório aberto: github.com/constituicaotech/constituicao-tech
Contato: oi@constituicao.tech

Respeitosamente,
[Seu nome]
[Sua qualificação]

---

## E-MAIL 5 — Para CNMP (Conselho Nacional do Ministério Público)

**Assunto:** Contribuição técnica — proteção de integridade em sistemas de IA do Ministério Público contra manipulação documental

**Destinatários sugeridos:**
- Comissão de Planejamento Estratégico
- Unidade Nacional de Capacitação do MP
- Corregedoria Nacional (para ciência)

---

Ao Conselho Nacional do Ministério Público,

Apresento contribuição técnica relativa a risco que afeta a integridade de sistemas de IA utilizados por membros e servidores do Ministério Público.

O vetor: indirect prompt injection — quando documentos recebidos de partes contêm instruções ocultas para manipular ferramentas de IA que os processem. Risco nº 1 do OWASP LLM Top 10 (2025), documentado pelo NIST AI 100-2e2025.

O MP, como fiscal da ordem jurídica (art. 176 CPC) e como parte em milhares de feitos que envolvem documentação de réus e investigados, é simultaneamente potencial vítima (quando seus sistemas são manipulados) e guardião institucional (quando sistemas do Judiciário são comprometidos).

Desenvolvemos ferramenta gratuita e de código aberto para detecção: constituicao.tech. Sem interesse comercial. Sem armazenamento. Metodologia pública alinhada a frameworks internacionais. Disponível para teste e auditoria imediatos.

Não se trata de autopromoção. Trata-se de uma lacuna de proteção que, se não for endereçada preventivamente, será explorada por quem tem incentivo para manipular resultados automatizados. O CNMP tem posição privilegiada para recomendar medidas preventivas em escala nacional.

Ferramenta: constituicao.tech
Repositório: github.com/constituicaotech/constituicao-tech
Contato: oi@constituicao.tech

Respeitosamente,
[Seu nome]
[Sua qualificação]

---

## Notas sobre envio

### Tom geral
- **Nunca** tom de venda
- **Sempre** tom de alerta técnico + contribuição institucional
- **Enfatizar**: paridade de armas, devido processo legal substancial, eficácia horizontal
- **Deixar claro**: não é produto, não cobra, não capta dados, é código aberto

### Onde encontrar e-mails institucionais
- **CNJ**: cnj.jus.br → Fale Conosco / Ouvidoria / Comitê de IA
- **STJ**: stj.jus.br → Secretaria de TI
- **TJs**: [sigla-estado].tjXX.jus.br → Secretaria de TI ou Ouvidoria
- **TRFs**: cada TRF tem página com contatos institucionais
- **MPF**: mpf.mp.br → Fale Conosco / Procuradoria da República
- **PGR**: pgr.mpf.mp.br
- **MPs Estaduais**: mp[sigla-estado].mp.br → Gabinete PGJ
- **CNMP**: cnmp.mp.br → Fale Conosco

### Lista de TJs para envio
| Tribunal | Sigla | Observação |
|----------|-------|------------|
| TJSP | São Paulo | Maior do país, já usa IA em triagem |
| TJRJ | Rio de Janeiro | — |
| TJMG | Minas Gerais | — |
| TJRS | Rio Grande do Sul | — |
| TJPR | Paraná | — |
| TJSC | Santa Catarina | — |
| TJDFT | Distrito Federal | Proximidade com CNJ |
| TJBA | Bahia | — |
| TJPE | Pernambuco | — |
| TJCE | Ceará | — |
| Demais TJs | — | Enviar conforme capacidade |

### Lista de TRFs
| Tribunal | Jurisdição |
|----------|-----------|
| TRF-1 | AC, AM, AP, BA, DF, GO, MA, MG, MT, PA, PI, RO, RR, TO |
| TRF-2 | ES, RJ |
| TRF-3 | MS, SP |
| TRF-4 | PR, RS, SC |
| TRF-5 | AL, CE, PB, PE, RN, SE |
| TRF-6 | MG |

### Lista de MPs para envio prioritário
| Órgão | Observação |
|-------|-----------|
| MPF/PGR | Nível federal, ações de grande porte |
| MPSP | Maior MP estadual |
| MPRJ | — |
| MPMG | — |
| MPRS | — |
| MPPR | — |
| MPDFT | Proximidade institucional |
| CNMP | Recomendação em escala nacional |
