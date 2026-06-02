# constituicao.tech — Documentação Técnica Completa

## 1. Arquitetura do Sistema

### 1.1 Visão Geral

```
┌─────────────────────────────────────────────────────────┐
│                    VPC Interna                            │
│                                                          │
│  ┌──────────────┐     ┌──────────────────────────────┐  │
│  │  Gateway Go  │────▶│  Detector Python (FastAPI)    │  │
│  │   :8080      │     │   :8081                       │  │
│  │              │     │                               │  │
│  │  • Rate Limit│     │  • Prompt Injection (core.py) │  │
│  │  • CORS      │     │  • Integridade (integridade.py)│ │
│  │  • Logging   │     │  • Assinatura (assinatura.py) │  │
│  │  • IP Hash   │     │  • Extração (extracao.py)     │  │
│  │              │     └──────────────────────────────┘  │
│  │  Fraud Shield│                                       │
│  │  (in-process)│                                       │
│  └──────────────┘                                       │
└─────────────────────────────────────────────────────────┘
         ▲
         │ HTTPS (externo)
    ┌────┴────┐
    │ Cliente │
    └─────────┘
```

### 1.2 Decisões Arquiteturais

| Decisão | Razão |
|---------|-------|
| Python para NLP/estilometria | Ecossistema numpy/scipy, maturidade para análise textual |
| Go para gateway + fraud | Performance (<50μs), sem GC pause crítico |
| Fraud shield in-process | Zero overhead de rede, latência microsegundos |
| Stateless | Privacidade, escalabilidade horizontal, LGPD |
| No external APIs | Determinismo, sem custo variável, offline-capable |

---

## 2. Módulo 1: Detecção de Prompt Injection

### 2.1 Metodologia

**Alinhamento**: OWASP LLM Top 10 (2025) LLM01, NIST AI 100-2e2025, MITRE ATLAS AML.T0051

**Pipeline**:
1. Normalização Unicode (NFKC + remoção zero-width + homóglifos)
2. Normalização de leetspeak
3. Scanning contra 13 padrões regex (com guard de 200k chars)
4. Detecção de esteganografia Unicode
5. Scoring ponderado por severidade com saturação em 100

**Categorias detectadas** (11):
- `injection_instrucao` — override explícito
- `injection_papel` — redefinição de identidade
- `injection_exfiltracao` — extração de system prompt
- `manipulacao_decisao` — nota dirigida a IA
- `injection_indireta` — instrução condicional
- `esteganografia` — caracteres invisíveis
- `ofuscacao` — homóglifos, leetspeak
- `payload_codificado` — base64 extenso
- `delimitador_suspeito` — ChatML, Llama tokens
- `jailbreak_conhecido` — DAN, DUDE, STAN
- `payload_fragmentado` — concatenação instruída

### 2.2 Sistema de Scoring

```
Score = Σ (peso_severidade × confiança × fator_repetição)
  onde:
    INFORMATIVA = 1, BAIXA = 5, MEDIA = 15, ALTA = 35
    fator_repetição = 1.0 (primeiro), 0.5 (subsequentes do mesmo padrão)
    amplificação = ×1.2 se texto < 500 chars
    saturação = min(100, score)

Classificação:
    score < 12  → "baixo"
    12 ≤ score < 30 → "atenção"
    score ≥ 30 → "elevado"
```

### 2.3 Guard contra ReDoS

Todas as regex são aplicadas a um texto truncado em `MAX_SCAN_CHARS = 200.000` caracteres. Além disso, as regex foram desenhadas para evitar backtracking catastrófico (sem quantificadores aninhados sobre strings variáveis).

### 2.4 Normalização de Leetspeak

Tabela de conversão aplicada antes do scan:
```
0→o, 1→i, 3→e, 4→a, 5→s, 7→t, 8→b, @→a, $→s, !→i
```

Matches na versão de-leetspeak recebem confiança reduzida (×0.85).

---

## 3. Módulo 2: Integridade Acadêmica

### 3.1 Estratégia

Análise estilométrica local pura (sem API). Determinística. 10 features estatísticas com pesos calibrados.

### 3.2 Features e Pesos

| Feature | Peso | O que mede |
|---------|------|-----------|
| zipf_deviation | 0.15 | Desvio do expoente da lei de Zipf |
| burstiness | 0.14 | Distribuição temporal de repetições |
| ttr_hapax | 0.12 | Riqueza vocabular (MSTTR + hapax ratio) |
| sentence_rhythm | 0.12 | CV do comprimento de frases |
| hedging_density | 0.09 | Marcadores de hesitação por 100 palavras |
| discourse_variance | 0.09 | CV dos intervalos entre conectivos |
| trigram_entropy | 0.08 | Proporção de trigramas únicos |
| char_entropy | 0.07 | Entropia de Shannon (com sinal de case) |
| repetition_pattern | 0.07 | Proporção de bigramas repetidos (>2x) |
| punctuation_rhythm | 0.07 | CV da densidade de pontuação por frase |

### 3.3 Classificação

```
Score = Σ (feature_valor × peso) × 100
  com ajuste para texto científico legítimo (≥3 marcadores → redução até 30%)

0-30:  provavelmente_humano (confiança alta se ≤20)
31-60: zona_cinza (segunda opinião recomendada)
61-100: provavelmente_ia (confiança alta se ≥75)

Textos < 200 palavras: confiança = "baixa" sempre
Textos < 30 palavras: classificação = "insuficiente"
```

### 3.4 Calibração (v0.2)

- Corpus de calibração: textos acadêmicos PT-BR (direito, ciências sociais) — corpus interno
- Acurácia estimada: 85-92% em corpus de teste interno (não validado externamente)
- Falso positivo em textos científicos: reduzido por marcadores (et al, hipótese nula, etc.)
- Nota: thresholds serão recalibrados na v0.3 com corpus ampliado e métricas F1/precision/recall publicadas

### 3.5 Escrita Científica Legítima

Textos com ≥3 marcadores científicos (apud, et al., hipótese nula, variável dependente, etc.) recebem atenuação de score para reduzir falso positivo em papers legítimos.

---

## 4. Módulo 3: Verificação de Assinatura Digital

### 4.1 Camadas de Verificação

1. **pyhanko** (quando disponível): Verificação criptográfica completa (CMS/PKCS#7, cadeia de certificados, hash)
2. **pypdf** (sempre): Verificação manual de ByteRange, detecção de campo vazio
3. **Heurística raw**: Busca de `/Type /Sig`, `/ByteRange`, `/Contents` no PDF bruto

### 4.2 Ataques Detectados

| Ataque | Detecção | Severidade |
|--------|----------|------------|
| Assinatura copiada | ByteRange não cobre final | Crítico |
| Hash não confere | pyhanko validation | Crítico |
| Modificação pós-assinatura | modification_level check | Crítico |
| Campo cosmético (/V ausente) | pypdf field check | Crítico |
| /Contents zerado | byte analysis | Crítico |
| SHA-1 depreciado | SubFilter analysis | Alerta |
| Sobreposição ByteRange | offset arithmetic | Crítico |
| ByteRange não começa em 0 | offset check | Crítico |

### 4.3 Nota sobre OCSP/CRL

Verificação de revogação (OCSP/CRL) requer acesso à rede. Em modo offline, a validação se limita a integridade estrutural e hash. A verificação de cadeia completa (ICP-Brasil) requer conectividade.

---

## 5. Módulo 4: Fraud Shield

### 5.1 Arquitetura

Engine Go stateful com VelocityCounter in-memory (sliding windows). Latência <50μs por avaliação.

### 5.2 Regras Globais (6)

| Regra | Tipo | Threshold |
|-------|------|-----------|
| high_single_amount | Valor | >R$10k medium, >R$50k high |
| velocity_count_1h | Frequência | >5 med, >10 high, >20 critical |
| velocity_amount_24h | Volume | >R$100k high, >R$200k critical |
| unusual_hour | Temporal | 0-6h + >R$5k |
| new_destination_high_amount | Behavioral | 1ª vez + >R$2k med, >R$10k high |
| rapid_fire | Burst | >3 em 2min high, >5 critical |

### 5.3 Regras de Betting (6)

| Regra | Padrão | Decisão |
|-------|--------|---------|
| betting_round_trip | Depósito + saque ≥80% em 24h | Block |
| betting_smurfing | >3 contas/IP em 1h | Review |
| betting_structuring | Soma >R$45k em ≥3 txs (COAF) | Review |
| betting_syndicate | >5 saques/merchant em 10min | Block |
| merchant_velocity | >150% do max/hora configurado | Review |
| betting_ticket_deviation | Avg 24h > 3× avg 30d | Review |

### 5.4 Scoring Híbrido

```
score_final = rule_score × (1 - ml_weight) + ml_score × 10 × ml_weight

Decisão:
  score ≥ 8.0 ou risk=critical → Block
  score ≥ 4.0 ou risk=high → Review
  caso contrário → Allow
```

### 5.5 Interfaces

```go
type Scorer interface {
    Score(features []float64) float64
}

type Persister interface {
    PersistDecision(ctx, txID, userID, amount, decision, risk, score, rules) error
}
```

Extensível via `WithScorer()`, `WithPersister()`, `WithRules()`.

---

## 6. API Reference

### 6.1 Prompt Injection

```
POST /v1/analisar/texto
Content-Type: application/json

{"texto": "string (max 500k chars)"}

Response:
{
  "score_risco": 0.0-100.0,
  "nivel": "baixo" | "atencao" | "elevado",
  "achados": [{categoria, severidade, descricao, trecho, posicao, padrao_id, confianca}],
  "metricas": {chars_originais, zero_width_removidos, ...},
  "metodologia_versao": "0.2.1",
  "aviso_falsos_positivos": "..."
}
```

```
POST /v1/analisar/arquivo
Content-Type: multipart/form-data
Body: arquivo (PDF, DOCX, TXT — max 10MB)
```

### 6.2 Integridade Acadêmica

```
POST /v1/integridade/texto
Content-Type: application/json

{"texto": "string (max 500k chars)"}

Response:
{
  "score_ia": 0.0-100.0,
  "classificacao": "provavelmente_humano" | "zona_cinza" | "provavelmente_ia" | "insuficiente",
  "confianca": "alta" | "media" | "baixa",
  "features": [{nome, valor, peso, contribuicao, interpretacao}],
  "metricas": {palavras, frases, caracteres, vocabulario_unico, texto_suficiente},
  "recomendacao": "...",
  "requer_segunda_opiniao": bool,
  "versao": "0.2.0",
  "aviso": "..."
}
```

### 6.3 Assinatura Digital

```
POST /v1/assinatura/verificar
Content-Type: multipart/form-data
Body: arquivo (PDF — max 10MB)

Response:
{
  "tem_assinatura": bool,
  "total_assinaturas": int,
  "achados": [{status, severidade, descricao, detalhes}],
  "assinaturas_validas": int,
  "assinaturas_invalidas": int,
  "risco": "baixo" | "alto",
  "metricas": {tamanho_pdf, pyhanko_disponivel, ...},
  "versao": "0.2.0",
  "aviso": "..."
}
```

### 6.4 Fraud Shield

```
POST /v1/fraude/avaliar
Content-Type: application/json

{
  "transaction_id": "string",
  "user_id": "string",
  "type": "pix_out" | "pix_in" | "withdrawal" | "swap" | "crypto_buy",
  "amount": int (centavos),
  "currency": "BRL",
  "destination": "string (opcional)",
  "ip": "string (opcional)",
  "merchant_id": "string (opcional)",
  "timestamp": "ISO 8601 (opcional)"
}

Response:
{
  "decision": "allow" | "review" | "block",
  "risk": "low" | "medium" | "high" | "critical",
  "score": float,
  "triggered_rules": ["rule_name", ...],
  "latency_us": int,
  "evaluated_at": "ISO 8601"
}
```

---

## 7. Deployment

### 7.1 Docker Compose

```yaml
services:
  gateway:
    build: ./api-go
    ports: ["8080:8080"]
    environment:
      - DETECTOR_URL=http://detector:8081
      - AMBIENTE=prod
      - IP_HASH_SALT=${IP_HASH_SALT}
  detector:
    build: ./detector-py
    expose: ["8081"]
```

### 7.2 Variáveis de Ambiente

| Variável | Default | Descrição |
|----------|---------|-----------|
| DETECTOR_URL | http://localhost:8081 | URL do microserviço Python |
| AMBIENTE | dev | dev/staging/prod |
| IP_HASH_SALT | (obrigatório em prod) | Salt para hash de IP |
| CONSTITUICAO_MAX_BYTES | 10MB | Limite de upload |
| CONSTITUICAO_MAX_CHARS | 500k | Limite de texto |

---

## 8. Segurança

### 8.1 Mitigações

- **ReDoS**: MAX_SCAN_CHARS = 200k, regex sem backtracking catastrófico
- **Input Validation**: Pydantic + Content-Type check + file extension whitelist
- **No Storage**: Stateless, nenhum dado persiste
- **IP Privacy**: Hash com salt, não armazena IP real
- **Rate Limiting**: Configurável no gateway
- **CSP Header**: Content-Security-Policy rigoroso

### 8.2 Limitações de Segurança

- Ataques semanticamente sutis (indirect injection sem padrão léxico) podem escapar
- Estilometria não detecta texto humano editado por IA
- Verificação de assinatura offline não valida revogação
- Fraud shield depende de sliding windows (reinício limpa histórico)

---

## 9. Testes

### 9.1 Python (34 testes)
```bash
cd detector-py && PYTHONPATH=. pytest tests/ -v
```

### 9.2 Go (17 testes)
```bash
cd fraud-shield && go test ./... -v
```

### 9.3 Cobertura de cenários

| Módulo | Testes | Cenários |
|--------|--------|----------|
| Prompt Injection | 13 | True positives (7) + True negatives (4) + edge cases (2) |
| Integridade | 11 | Humano, IA, misto, curto, vazio, determinismo, serialização |
| Assinatura | 10 | ByteRange (5), PDF (3), serialização, cobertura |
| Fraud Shield | 17 | Rules (5), betting (7), scoring (5) |

---

## 10. Roadmap Técnico

### v0.2 (atual)
- [x] 4 módulos funcionais
- [x] 51+ testes passando
- [x] ReDoS guard
- [x] Leetspeak detection
- [x] Scientific markers (reduz FP)
- [x] SHA-1 warning
- [x] Truncation header

### v0.3 (planejado)
- [ ] Corpus ampliado para calibração de estilometria
- [ ] ONNX model para fraud shield
- [ ] Benchmark automatizado de latência
- [ ] Integração CI/CD (GitHub Actions)
- [ ] Validação ICP-Brasil (com rede)
