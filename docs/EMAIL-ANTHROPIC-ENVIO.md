# Email para Anthropic — versão para envio

**Para:** partnerships@anthropic.com
**Assunto:** AI-defense platform built with Claude — live, open source, 4 security modules

---

Hi,

I'm Matheus Beans (BeansTech, Google for Startups alumni, Brazil). I built an AI integrity platform — **entirely with Claude Opus** — that's now live at **https://constituicao.tech**.

**What it does:** Protects documents processed by AI systems. Four modules, each mapped to a Brazilian constitutional article:

1. **Prompt Injection Detection** — 11 categories, OWASP LLM01:2025 aligned, <1s latency
2. **Stylometric Integrity** — detects AI-generated text via 10 statistical features (local, no API)
3. **Digital Signature Verification** — multi-layer PDF validation (pyhanko + pypdf + heuristics)
4. **Fraud Shield** — Go engine, 12 rules, ~100μs, zero dependencies

**What Claude built:** Every line — Python detector, Go gateway, Go fraud engine, 2 ebooks (100 real-world examples of judicial prompt injection), CI/CD, infrastructure. 300+ sessions with Opus 4.5/4.6. This isn't generated code — it's co-architected defensive infrastructure across 4 security domains.

**Why it matters for you:**
- Glasswing thesis applied to the input layer (adversarial payloads in documents AI reads)
- Proof of Claude's capability spectrum beyond chatbots — one model, four security domains
- Open source (Apache 2.0) with full attribution to Claude in README, docs, and commits

**Links:**
- Live: https://constituicao.tech
- Repo: https://github.com/beanstechhub/constituicao
- Validation (Colab): https://colab.research.google.com/github/beanstechhub/constituicao/blob/main/colab_validation.ipynb

**What I'm exploring:**
- Is there a showcase program for defensive AI projects built with Claude?
- Would you be interested in co-publishing the prompt injection research? (100-example ebook, OWASP/NIST/MITRE aligned)
- Does Glasswing see alignment with pre-LLM adversarial input detection?

The platform ships regardless — fully attributed. But if there's mutual value, I'd like to know.

Best,
Matheus Beans
BeansTech · Google for Startups Alumni · Brazil
https://github.com/beanstechhub

---

## Notas para antes de enviar:

1. **Verificar que o site funciona** — abrir https://constituicao.tech, testar analisador
2. **Verificar que o Colab funciona** — abrir link, Run All, ver 34 tests + 6 end-to-end passing
3. **Verificar o repo** — README está apresentável? (sim, tem tudo)
4. **Onde enviar:**
   - partnerships@anthropic.com (principal)
   - Ou via https://www.anthropic.com/partners (formulário)
   - Ou via https://claude.ai feedback com link para o projeto
5. **Horário ideal:** Terça/Quarta, 9-11am PST (horário SF)
   - Agora (3 Jun 2026) é terça — bom dia para enviar
   - 9am PST = 13h BRT
