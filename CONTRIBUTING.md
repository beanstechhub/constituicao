# Contribuindo para constituicao.tech

Obrigado por considerar contribuir. Este documento explica como participar.

---

## Formas de contribuição (por ordem de impacto)

### 1. Contraexemplos (maior impacto)

Se você é profissional do direito, perícia, auditoria, medicina ou finanças:

- Submeta amostras **anonimizadas** de documentos reais que produzem falso positivo ou falso negativo
- Abra issue com a tag `contraexemplo`
- Inclua: texto que disparou, categoria do achado, por que é legítimo/malicioso

**Isso é o que mais melhora o sistema.** Cada contraexemplo validado pode virar um teste automatizado.

### 2. Novos vetores

Identificou um padrão de manipulação não coberto pela taxonomia atual?

- Abra issue com a tag `novo-vetor`
- Descreva: padrão linguístico, exemplo concreto, referência bibliográfica (se houver)
- Se possível, mapeie para OWASP LLM01, NIST AI 100-2e2025, ou MITRE ATLAS

### 3. Código

Pull requests são bem-vindos com as seguintes condições:

1. **Testes obrigatórios.** Toda PR precisa passar na suite existente E adicionar testes para o que introduz.
2. **True negatives obrigatórios.** Se adicionar padrão de detecção, incluir pelo menos um caso de texto legítimo que NÃO deve disparar.
3. **Explicabilidade mantida.** Sem caixa-preta, sem modelo ML sem justificativa.
4. **Confiança calibrada.** Todo padrão novo precisa de `confianca_base` fundamentada.

---

## Setup de desenvolvimento

```bash
# Clone
git clone https://github.com/constituicao-tech/framework.git
cd framework

# Detector (Python)
cd detector-py
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate no Windows
pip install -r requirements.txt
pip install pytest
PYTHONPATH=. pytest tests/ -v

# Stack completa (Docker)
docker compose up --build
```

## Estrutura do repositório

```
├── detector-py/         # Núcleo de detecção (Python)
│   ├── detector/
│   │   ├── core.py      # Padrões, scoring, análise
│   │   └── extracao.py  # Extração de texto de PDF/DOCX/TXT
│   ├── tests/
│   │   └── test_core.py # Suite de testes com true positives e negatives
│   ├── server.py        # Microserviço FastAPI
│   └── requirements.txt
├── api-go/              # Gateway HTTP (Go)
│   └── main.go          # Rate limiting, CORS, proxy
├── web/                 # Frontend estático
│   └── index.html
├── infra/               # Scripts de deploy GCP
├── docs/                # Documentação complementar
└── metodologia.md       # Documento técnico principal
```

## Convenções

- **Commits:** mensagens em português, descritivas, prefixo por área (`detector:`, `api:`, `web:`, `docs:`, `infra:`)
- **Branches:** `feature/xxx`, `fix/xxx`, `docs/xxx`
- **Testes:** `pytest` com assertions claras. Nomes de teste descrevem o cenário.
- **Padrões:** cada regex tem ID único (`INJ-001`, `IND-002`...), severidade, confiança e descrição.

## Código de conduta

- Contribuições de boa-fé são esperadas
- Não submeta vetores de ataque que não estejam publicamente documentados sem coordenação prévia
- Não inclua dados pessoais reais em testes ou issues
- Crítica técnica é bem-vinda; ataques pessoais não

---

*Dúvidas: abra issue ou escreva para contribuir@constituicao.tech*
