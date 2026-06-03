# Emails para envio — 3 Jun 2026

> **Melhores práticas aplicadas:** Subject < 45 chars, body em 1 tela mobile, personalizado, single ask, dados concretos, follow-up em 3-5 dias.

---

## 1. ANTHROPIC

**Canal:** https://claude.com/contact-sales (formulário) + partnerships@anthropic.com
**Assunto:** Claude built a 4-module defense platform (live)

---

Hi,

I used Claude Opus (300+ sessions) to co-architect a live AI defense platform:

**https://constituicao.tech** — detects prompt injection, AI-generated text, signature fraud, and financial fraud in documents before they reach LLMs.

Numbers: 4 modules, 34 tests, <1s latency, OWASP LLM01 aligned, Apache 2.0.

This isn't wrapper code — it's defensive infrastructure across Python, Go, NLP, cryptography, and real-time fraud detection. One model, four security domains. Every commit attributes Claude.

Repo: https://github.com/beanstechhub/constituicao (org beanstechhub)

Is there a "Powered by Claude" showcase for defensive AI projects? I have a 100-example ebook on judicial prompt injection ready for co-publishing if there's interest.

— Matheus Beans, BeansTech (Google for Startups alumni, Brazil)

---

**Follow-up (dia 4):**

Subject: Re: Claude built a 4-module defense platform (live)

Quick follow-up — the platform is being presented to Brazil's National Council of Justice (CNJ) as a tool against adversarial manipulation of judicial AI systems. Attribution to Claude is front and center.

If there's someone specific I should connect with on the Glasswing or partnerships team, I'd appreciate a pointer.

---

## 2. GOOGLE

**Canal:** Contato Google for Startups LATAM / Cloud partnerships
**Assunto:** GFS alumni: AI integrity tool live on Cloud Run

---

Hi,

Google for Startups alumni here (BeansTech, Brazil). Quick share:

I deployed **constituicao.tech** entirely on GCP — an open-source AI integrity platform protecting judicial documents from adversarial manipulation.

Stack: Cloud Run (us-central1), Cloud Build, Artifact Registry, Google-managed SSL. 4 modules, 34 tests, zero external APIs.

Live: https://constituicao.tech
Repo: https://github.com/beanstechhub/constituicao (org beanstechhub)

If there's a customer story, case study, or startup highlight for alumni building public-safety tools on GCP, I'd be glad to participate.

— Matheus Beans, BeansTech

---

## 3. MICROSOFT / GITHUB

**Canal:** GitHub Security (via issue/discussion no github/advisory-database) ou opensource@github.com
**Assunto:** GitHub Action for LLM prompt injection scanning

---

Hi,

I built a GitHub Action that scans PR documents for prompt injection before they reach AI systems:

- Addresses OWASP LLM01:2025
- Configurable threshold + scan modes
- Apache 2.0, zero dependencies
- Repo: https://github.com/beanstechhub/constituicao (org beanstechhub)

The broader platform (constituicao.tech) also detects AI-generated text, forged signatures, and financial fraud — all runnable as a GitHub Action in CI/CD.

Relevant for Copilot/AI-integrated workflow security. Is there a pathway for GitHub Marketplace security tools or Supply Chain Security partnerships?

— Matheus Beans, BeansTech (Brazil)

---

## 4. CNJ — CONSELHO NACIONAL DE JUSTIÇA

**Canal:** Ouvidoria CNJ (https://www.cnj.jus.br/ouvidoria/) → Manifestação tipo "Sugestão"
**Ou:** Laboratório de Inovação do CNJ (liods@cnj.jus.br)
**Assunto:** Ferramenta open-source contra prompt injection em petições — proposta de demonstração

---

Prezados,

Sou Matheus Beans, fundador da BeansTech (alumni Google for Startups). Desenvolvi ferramenta open-source que detecta instruções adversariais embutidas em petições processadas por sistemas de IA do Judiciário.

**Problema que resolve:** Advogados podem inserir instruções invisíveis em PDFs (texto branco, caracteres zero-width, metadados) que manipulam sistemas de triagem automática como o Sinapses. A ferramenta identifica 11 categorias de ataque antes que o documento chegue à IA.

**Fatos:**
- 34 testes automatizados, alinhada a OWASP LLM01:2025
- Zero armazenamento de dados (LGPD by design)
- Código aberto, Apache 2.0, auditável
- Inclui ebook com 100 exemplos documentados de vetores em petições
- Complementa Resolução CNJ 332/2020 com camada técnica

**Demonstração funcional:** https://constituicao.tech
**Repositório:** https://github.com/beanstechhub/constituicao (org beanstechhub)

**Proposta:** Apresentação técnica para equipe do Sinapses/PJe (15 min, remota). Disponibilização gratuita como middleware de pré-processamento.

Atenciosamente,
Matheus Beans
BeansTech · Google for Startups Alumni
matheus@beanstech.com.br

---

## ESTRATÉGIA DE ENVIO

| Destinatário | Quando | Canal | Follow-up |
|---|---|---|---|
| Anthropic | Hoje 13h BRT (9am PST) | Formulário + email | Dia 4 (sexta) |
| Google | Hoje 14h BRT | Email direto LATAM | Dia 5 |
| Microsoft/GitHub | Hoje 14h BRT | Email opensource@ | Dia 7 |
| CNJ | Hoje 10h BRT | Ouvidoria + liods@ | 15 dias |

**Horário ideal para US:** 9-11am PST = 13-15h BRT (terça é bom dia)
**Horário ideal para BR:** 9-11h BRT (governo funciona de manhã)
