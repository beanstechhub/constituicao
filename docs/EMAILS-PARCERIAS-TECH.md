# E-mails para Parceiros de Tecnologia — constituicao.tech

---

## E-MAIL PARA ANTHROPIC — Glasswing / Ecossistema de defesa construído com Claude

**Assunto:** Two AI-defense tools built entirely with Claude — Glasswing-aligned work from Brazil

**Destinatário sugerido:**
- Via Claude for Open Source (pathway indicado na página do Glasswing para maintainers)
- partnerships@anthropic.com
- glasswing@anthropic.com (se existir)

---

Hi,

You know who I am from usage patterns. Hundreds of sessions with Claude Opus 4.5 and 4.6 across multiple projects. I'm writing not to ask for something specific, but to show you what your model has been building — because the narrative is worth knowing.

**I built 4 defensive modules entirely with Claude — a full AI integrity platform:**

**constituicao.tech** (publishing on GitHub, Apache 2.0)

Each module maps to a constitutional article — the "constitution of the digital world":

1. **Prompt Injection Detection** (Art. 5º LIV CF — due process)
   13 regex patterns, Unicode normalization, leetspeak detection, steganography. Aligned to OWASP LLM01:2025, NIST AI 100-2e2025, MITRE ATLAS. Latency ~5ms.

2. **Academic Integrity / Stylometric Analysis** (Art. 205-214 CF — education rights)
   10 statistical features (Zipf deviation, burstiness, TTR/hapax, sentence rhythm, hedging density, etc.) — pure local analysis, no external API. 85-92% accuracy on internal PT-BR corpus. Deterministic.

3. **Digital Signature Verification** (Art. 19 CF — public faith)
   Multi-layer PDF signature validation: pyhanko + pypdf + raw heuristics. Detects ByteRange manipulation, hash mismatch, cosmetic signatures, SHA-1 deprecation. 8 attack vectors covered.

4. **Fraud Shield** (Art. 170 CF — economic order)
   Go engine, in-process, ~100μs latency. 12 rules (6 global + 6 betting/anti-money-laundering). Sliding windows, hybrid scoring, extensible via interfaces. Pure Go stdlib — no dependencies.

**The architecture:**
- Gateway (Go): rate limiting, CORS, structured logging, request ID
- Detector (Python/FastAPI): modules 1-3
- Fraud Shield (Go, in-process): module 4
- 61+ automated tests, GitHub Actions CI, benchmarks

**This is Glasswing's thesis applied to the input layer.** Instead of finding zero-days in the software AI runs on, it finds adversarial payloads in the documents AI reads, validates academic integrity, verifies signature authenticity, and blocks financial fraud — all in a single coherent platform grounded in constitutional law.

**Why I'm writing:**

**I'm a natural propagator of what you build.** I use Claude extensively, I build real defensive infrastructure with it, I'm publishing it with full attribution. The README says "Built with Claude." The methodology documentation shows what frontier AI produces when pointed at defense rather than attack.

If there's value in showcasing that Claude builds security platforms — not just apps, not just code, but actual defensive infrastructure across 4 domains (NLP, statistics, cryptography, fraud detection) — I'm already doing it. Google for Startups alumni. Constitutional law foundation (horizontal effect of fundamental rights, due process between private parties). No commercial interest — it's public good.

If you see alignment with Glasswing's mission, let me know how to formalize it. If not, the work ships regardless. Claude built it. That fact alone is the message.

constituicao.tech (going live)
github.com/constituicaotech/constituicao-tech (publishing shortly)

[Seu nome]
BeansTech · Brazil
[Seu e-mail]

---

## E-MAIL PARA GOOGLE — Startup alumni + parceria

**Assunto:** constituicao.tech — AI integrity tool from Google for Startups alumni · partnership exploration

**Destinatário sugerido:**
- Google for Startups regional contact (LATAM)
- Google Cloud Partnerships (se aplicável)
- startups-latam@google.com (ou contato direto que você tenha do programa)

---

Dear Google for Startups team,

I'm a Google for Startups alumni (BeansTech), reaching out about a new open-source initiative that we believe aligns with Google's mission on AI safety and responsible deployment.

**What we built:**

constituicao.tech — a free, open-source platform with 4 defensive modules for document integrity in the AI era:

1. **Prompt Injection Detection** — 13 patterns, Unicode/leetspeak normalization, OWASP LLM01 aligned
2. **Academic Integrity** — stylometric analysis with 10 statistical features, zero external APIs
3. **Digital Signature Verification** — multi-layer PDF validation, 8 attack vectors detected
4. **Fraud Shield** — Go engine, 12 rules, ~100μs latency, anti-money-laundering (COAF)

The platform is:
- Aligned to OWASP LLM Top 10 (2025), NIST AI 100-2e2025, and MITRE ATLAS
- Deterministic and explainable — no black-box decisions
- Privacy-first: no document storage, no tracking, LGPD-compliant
- 61+ automated tests, CI/CD, benchmarked latencies
- Built for deployment on Google Cloud (Cloud Run + Cloud Armor)
- Under Apache 2.0 license

**Why it matters:**

As AI assistants become embedded in institutional workflows (judicial systems, compliance, due diligence), document integrity becomes a critical attack surface across multiple dimensions: manipulation of AI systems, fabrication of authorship, forged signatures, and financial fraud. We address these four attack surfaces in a single coherent platform grounded in constitutional law.

**Constitutional foundation:**

The project is grounded in the horizontal effect of fundamental rights — the principle that due process and fairness obligations apply between private parties, not just against the state. When one party manipulates an AI system via a crafted document, the other party loses without knowing why. This violates constitutional principles of procedural fairness and equality of arms.

**The connection to Google:**

1. We came from Google for Startups — your ecosystem shaped how we build.
2. The infrastructure runs on GCP (Cloud Run, Cloud Armor, Cloud Storage).
3. The tool protects AI-assisted workflows — directly relevant to Google's Responsible AI commitments.

**What we're exploring:**

- Whether Google Cloud or Google for Startups has programs for open-source AI safety tools
- Potential visibility through Google's AI safety or responsible AI channels
- Any guidance on scaling a public-good infrastructure project on GCP cost-effectively

We have no commercial model — this is a public good initiative. The goal is parity of arms in the AI era.

Repository: github.com/constituicaotech/constituicao-tech
Live: constituicao.tech

Best regards,
[Seu nome]
BeansTech · Google for Startups alumni
[Seu e-mail]

---

## E-MAIL PARA PERPLEXITY — Parceria

**Assunto:** Partnership proposal — constituicao.tech protects AI-processed documents from prompt injection

**Destinatário sugerido:**
- partnerships@perplexity.ai
- business@perplexity.ai

---

Dear Perplexity team,

I'm reaching out about a potential partnership between Perplexity and constituicao.tech — an open-source initiative that addresses a problem directly relevant to any AI system that processes user-submitted or third-party documents.

**The problem we solve:**

When AI systems (including search-augmented generation) process documents or web content produced by adversarial parties, those documents can contain hidden instructions designed to manipulate the AI's output. This is indirect prompt injection — OWASP's #1 risk for LLM applications (2025).

Perplexity's model — ingesting and synthesizing content from across the web — makes it a potential target for exactly this vector. Websites, PDFs, and documents indexed by Perplexity could theoretically contain prompt injection payloads designed to bias the system's answers.

**What constituicao.tech does:**

A platform with 4 defensive modules:
- **Prompt Injection**: 13 patterns + Unicode/leetspeak normalization, aligned to OWASP/NIST/MITRE
- **Academic Integrity**: 10 stylometric features, pure local analysis, 85-92% accuracy
- **Digital Signature**: Multi-layer PDF verification, 8 attack vectors
- **Fraud Shield**: Go engine, 12 rules, ~100μs, anti-structuring (COAF)

Open-source (Apache 2.0), free, no data storage, 61+ tests, deterministic.

**Why partnership makes sense:**

1. **Perplexity processes untrusted content at scale.** A pre-processing integrity check could reduce the surface area for indirect prompt injection via indexed documents.
2. **Shared interest in trustworthy AI.** Perplexity's value proposition depends on answer accuracy. Prompt injection in source documents degrades that accuracy silently.
3. **Document verification.** Our signature and integrity modules could validate source documents before Perplexity ingests them — ensuring citations come from authentic, unmanipulated sources.

**What we'd like to explore:**

- Technical discussion about how Perplexity handles integrity of ingested content
- Whether our detection patterns or methodology could be useful as a pre-processing filter
- Potential co-development of semantic prompt injection detection
- Visibility for the project through Perplexity's AI safety communications

We have no commercial interest — this is a public good initiative under Apache 2.0. The goal is making the AI ecosystem more robust against adversarial manipulation of the input layer.

Repository: github.com/constituicaotech/constituicao-tech
Live tool: constituicao.tech
Methodology: constituicao.tech/metodologia

Looking forward to exploring this.

Best regards,
[Seu nome]
BeansTech · constituicao.tech
[Seu e-mail]

---

## Notas sobre publicação no GitHub

### Opção 1: Organização `constituicao-tech` (recomendada)
- Crie a org no GitHub: github.com/constituicao-tech
- Repositório: `constituicao-tech/framework`
- Vantagem: marca institucional dedicada, permite colaboradores futuros
- Os e-mails acima já referenciam essa URL

### Opção 2: Conta pessoal `beanstechbr`
- Repositório: `beanstechbr/constituicao-tech`
- Vantagem: mostra autoria direta, conecta ao Google for Startups alumni
- Desvantagem: parece mais "pessoal" para e-mails institucionais

### Recomendação
Criar a organização `constituicao-tech` no GitHub e fazer fork/mirror na `beanstechbr` para manter a conexão com a identidade da startup. Nos e-mails referenciar sempre a org.

### Comandos para publicação

```bash
# Na máquina local, dentro de e:\constituicao.tech
git init
git add .
git commit -m "v0.2.0 — detector alinhado a OWASP/NIST/MITRE, documentação completa

Fundamentado na eficácia horizontal dos direitos fundamentais.
Paridade de armas e devido processo legal substancial na era da IA generativa."

# Opção 1: org constituicao-tech
git remote add origin git@github.com:constituicao-tech/framework.git
git branch -M main
git push -u origin main

# Opção 2: conta pessoal
git remote add origin git@github.com:beanstechbr/constituicao-tech.git
git branch -M main
git push -u origin main
```
