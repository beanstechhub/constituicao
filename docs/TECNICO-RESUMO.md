# constituicao.tech — Resumo Técnico

## Visão Geral

Plataforma de integridade documental na era da IA generativa. 4 módulos independentes, zero APIs externas para análise core, código aberto.

## Arquitetura

```
[Cliente] → [Gateway Go :8080] → [Detector Python :8081]
                ↓
         [Fraud Shield (in-process)]
```

- **Gateway Go**: Rate limiting, CORS, logging estruturado, request ID
- **Detector Python**: FastAPI, 3 endpoints de análise
- **Fraud Shield**: Engine Go in-process, <50μs latência

## Módulos

| # | Módulo | Endpoint | Latência |
|---|--------|----------|----------|
| 1 | Prompt Injection | `POST /v1/analisar/texto` | ~5ms |
| 2 | Integridade Acadêmica | `POST /v1/integridade/texto` | ~50ms |
| 3 | Assinatura Digital | `POST /v1/assinatura/verificar` | ~100ms |
| 4 | Fraud Shield | `POST /v1/fraude/avaliar` | ~100μs |

## Stack

- Python 3.11+: FastAPI, numpy, scipy, pypdf, pyhanko
- Go 1.22+: stdlib pura (gateway + fraud shield)
- Docker: compose com 2 serviços
- CI: GitHub Actions (Python + Go tests + benchmarks)

## Testes

- Detector Python: 34 testes (pytest)
- Fraud Shield: 17 testes (go test)
- Total: 51+ testes automatizados

## Segurança

- ReDoS guard em todas as regex (MAX_SCAN_CHARS = 200k)
- Normalização de leetspeak, homóglifos, zero-width
- Input validation em todas as bordas
- Nenhum dado armazenado (stateless)
- VPC interna (detector-py não exposto)

## Limitações Conhecidas

- Falso positivo ~3-7% (prompt injection)
- Estilometria calibrada para PT-BR (v0.2, ~85-92% acurácia)
- Assinatura: OCSP/CRL requer rede (indisponível offline)
- Thresholds sujeitos a recalibração com corpus maior
