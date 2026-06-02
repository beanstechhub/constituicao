# Falsos Positivos — constituicao.tech

**Versão 0.2.0** · Este documento explica por que falsos positivos acontecem, como minimizá-los, e o que fazer quando ocorrem.

---

## Por que falsos positivos são inevitáveis

Detecção de prompt injection por análise estática de padrões enfrenta um problema fundamental: a linguagem usada para manipular sistemas de IA **se sobrepõe parcialmente** à linguagem legítima de documentos profissionais.

Exemplos reais de sobreposição:

| Cenário legítimo | Por que pode disparar alerta |
|---|---|
| Petição que pede "julgue procedente" | Linguagem imperativa + verbo de decisão |
| Parecer técnico discutindo "prompt injection" | Menciona termos que são padrões de ataque |
| Artigo acadêmico sobre segurança de IA | Contém exemplos didáticos de vetores |
| Currículo revisado por LLM submetido a triagem automatizada | Pode conter artefatos da assistência |
| Documento sobre política de IA que diz "instruções ao sistema" | Coincide com padrão de exfiltração |

## Estado da arte

A literatura recente (2024-2025) mostra que os melhores sistemas de detecção de prompt injection atingem aproximadamente:

- **89,4% de mitigação** de ataques
- **94,3% de preservação** da funcionalidade legítima
- Ou seja: **~5-6% de taxa de falso positivo** no estado da arte

Referência: Yi et al. (2024), "Adaptive System-Filter Prompt Injection Defense Framework", IEEE/ACM.

O constituicao.tech estima sua taxa de falso positivo entre **3-7%**, dependendo do domínio do documento.

## Categorias mais propensas a falso positivo

### 1. `payload_codificado` (EST-001)
**Confiança base: 55%** — a mais baixa do sistema.

Blocos longos de base64 são comuns em documentos legítimos (imagens inline, assinaturas digitais, hashes de integridade). O detector sinaliza mas com confiança deliberadamente baixa.

### 2. `manipulacao_decisao` (IND-001)
**Confiança base: 88%**

Textos que endereçam "a IA" ou "ao sistema" aparecem em documentos que discutem política de uso de IA, termos de referência para contratação de ferramentas, ou pareceres sobre regulamentação.

### 3. `ofuscacao` (EST-002)
**Confiança base: 70%**

URLs com muitos parâmetros, referências a APIs com query strings longas, ou citações de código-fonte podem disparar este padrão.

## O que fazer quando um falso positivo ocorre

### Se você é o usuário final:
1. **Leia a justificativa.** Cada achado mostra o trecho exato que disparou e a categoria. Avalie se faz sentido no contexto.
2. **Confie no nível, não no score isolado.** "Atenção" significa literalmente isso — olhe com mais cuidado, não descarte o documento.
3. **Considere o contexto.** Um artigo acadêmico sobre segurança de IA que acende "atenção" é esperado e benigno.

### Se você é desenvolvedor/integrador:
1. **Não use o resultado como gate automático.** O sistema foi desenhado para informar humanos, não para bloquear pipelines.
2. **Filtre por confiança.** Achados com confiança < 70% são sinalizadores, não vereditos.
3. **Abra issue com contraexemplo.** Se um documento legítimo do seu domínio produz falso positivo consistente, reporte para calibrarmos.

## Caso documentado (OWASP, 2024)

O OWASP Generative AI Guide documenta um caso relevante: uma empresa colocou instrução em descrição de vaga para detectar candidaturas geradas por IA. Um candidato legítimo que usou LLM apenas para revisar gramática do currículo acabou disparando o detector — exemplo perfeito de como uso benigno pode gerar alerta.

Isso ilustra que **detecção de manipulação de IA não é equivalente a detecção de uso de IA**, e que qualquer sistema que trate os dois como sinônimos vai produzir falso positivos sistêmicos.

## Como reportar falso positivo

1. Abra issue em [github.com/constituicao-tech/framework](https://github.com/constituicao-tech/framework) com a tag `falso-positivo`
2. Inclua: texto anonimizado que disparou, categoria do achado, por que é legítimo no contexto
3. Não inclua: dados pessoais, números de processo reais, conteúdo confidencial

Contraexemplos são a contribuição mais valiosa que a comunidade pode fazer. Cada falso positivo documentado melhora a calibração para todos.

---

*Este documento é parte da metodologia aberta e está sujeito a revisão pública.*
