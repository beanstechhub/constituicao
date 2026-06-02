# Changelog

Todas as alterações materiais na metodologia e no código são documentadas aqui.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/). Este projeto usa [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [0.2.0] — 2026-05-25

### Adicionado
- Alinhamento formal a OWASP LLM Top 10 (2025), NIST AI 100-2e2025 e MITRE ATLAS.
- Mapeamento de cada categoria a identificadores de frameworks internacionais.
- Campo `frameworks_de_referencia` em cada achado da resposta da API.
- Campo `aviso_falsos_positivos` em toda resposta, com taxa estimada (3-7%).
- Novas categorias: `injection_indireta`, `ofuscacao`, `payload_codificado`, `payload_fragmentado`.
- Padrões novos: INJ-001b (injection EN), IND-002 (indireta condicional), IND-003 (ocultação), EST-001 (base64), EST-002 (hex-escape), FRG-001 (fragmentação).
- Detecção de homóglifos cirílicos (normalização + alerta).
- Detecção de controles bidirecionais Unicode.
- Suite de testes expandida: 24 testes incluindo true negatives para petição, parecer técnico, artigo acadêmico sobre IA.
- Documentação: `docs/FALSOS-POSITIVOS.md`, `docs/API.md`, `CONTRIBUTING.md`, `CHANGELOG.md`.
- Fundamentação constitucional: eficácia horizontal dos direitos fundamentais.

### Alterado
- Scoring refatorado: saturação por padrão (repetições valem 50% cada), limita inflação.
- Confiança base calibrada por padrão (0.55 a 0.97) em vez de uniforme.
- Regex INJ-002 permite adjetivos entre artigo e substantivo ("a helpful assistant").
- Marca migrada de "defesa.tech" para "constituicao.tech".
- Versão da API e detector atualizada para 0.2.0.

### Corrigido
- Regex de role hijack em inglês não capturava "You are now a helpful assistant" (adjetivo intermediário).

---

## [0.1.0] — 2026-05-20

### Adicionado
- Detector inicial com 7 categorias de vetor.
- API Go com rate limiting e CORS.
- Frontend estático com analisador integrado.
- Política de privacidade LGPD-safe.
- Suite básica de testes.
- Documentação de metodologia.
- Scripts de deploy para GCP (Cloud Run + Cloud Armor).
