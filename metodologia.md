Metodologia — constituicao.tech

Versão 0.2.0 · Documento sujeito a revisão pública.

Esta é a explicação técnica completa de como o detector funciona, em qual literatura se apoia, e como foi calibrado. Foi escrita para que qualquer pessoa — técnica ou não — possa entender, criticar e propor melhorias.
1. Objetivo
Identificar, em documentos profissionais (petições, pareceres, laudos, relatórios), tentativas de manipulação de sistemas de inteligência artificial que processarão aquele documento.
O alvo não é o conteúdo do documento em si, nem julgar sua qualidade jurídica ou técnica. O alvo são inserções desenhadas para que um sistema de IA leia o documento e produza saída enviesada.
2. Frameworks de referência
A taxonomia, a calibração e a nomenclatura de categorias estão alinhadas a três frameworks internacionais:
OWASP LLM Top 10 (2025) — em particular a categoria LLM01:2025 (Prompt Injection), que classifica direct injection, indirect injection, payload splitting e obfuscation como vetores principais. Cada categoria do detector está mapeada a um identificador OWASP.
NIST AI 100-2e2025 (Adversarial Machine Learning Taxonomy) — taxonomia oficial do NIST sobre ataques adversariais a sistemas de IA, incluindo a seção sobre evasion attacks e obfuscation techniques.
MITRE ATLAS (Adversarial Threat Landscape for AI Systems) — equivalente do MITRE ATT&CK para sistemas de IA. Usamos os identificadores de táticas (AML.T0051.*, AML.T0054, AML.T0057) para referência cruzada.
A intenção desse alinhamento não é cosmética. É que outros profissionais que conhecem essas referências consigam navegar nossa metodologia sem aprender vocabulário novo.
3. Arquitetura do detector
O detector opera em três camadas, com decisão progressiva:
Camada 1 — Normalização Unicode. O texto é normalizado para NFKC. Caracteres invisíveis (zero-width space, joiners, controles bidirecionais) são removidos. Homóglifos comuns (caracteres cirílicos que parecem latinos) são convertidos. Métricas sobre o que foi removido são preservadas e alimentam achados.
Camada 2 — Detecção por padrões. Conjunto de expressões regulares calibradas para identificar padrões linguísticos típicos de prompt injection em português e inglês. Cada padrão tem identificador único (INJ-001, IND-002, etc.), severidade (baixa/média/alta) e confiança base.
Camada 3 — Scoring saturante. Achados individuais são combinados em um score de 0 a 100. A combinação não é linear: repetições do mesmo padrão saturam (cada repetição vale metade da anterior), evitando que um documento seja punido por mencionar o mesmo termo várias vezes.
4. Calibração de severidade
A severidade de cada padrão foi calibrada considerando o custo relativo de falso positivo e falso negativo.
SeveridadePesoCritérioInformativa1Marcador útil de auditoria, mas sem riscoBaixa5Padrão pouco específico, frequente em texto legítimoMédia15Padrão sugestivo, requer contexto humanoAlta35Padrão característico de tentativa de manipulação
Os thresholds de nível foram definidos para que um único achado de severidade alta com confiança alta seja suficiente para nível "elevado":

0 - 11: nível baixo
12 - 29: nível atenção
30 - 100: nível elevado

5. Tratamento de falsos positivos
Falsos positivos são esperados e tratados como parte do design. Quatro decisões reduzem o impacto:
A primeira é explicabilidade obrigatória. Cada achado inclui o ID do padrão, o trecho que disparou, a categoria, a confiança e as referências aos frameworks. O usuário pode verificar imediatamente se o alerta faz sentido para o contexto dele.
A segunda é escala em vez de binário. O resultado nunca é "fraudulento vs limpo" — é um nível em três faixas que comunica grau de incerteza. "Atenção" significa exatamente isso: olhe com mais cuidado, não tire conclusão.
A terceira é confiança ponderada. Padrões que são especialmente vulneráveis a falso positivo (como blocos de base64, que podem ser dados legítimos) recebem confiança base mais baixa. Padrões raros em uso legítimo (como delimitadores ChatML) recebem confiança alta.
A quarta é transparência sobre a taxa. A literatura mostra que sistemas estado da arte para detecção de prompt injection atingem cerca de 89% de mitigação preservando 94% da funcionalidade legítima — ou seja, cerca de 5-6% de falso positivo é o estado da arte, e este detector não pretende fazer melhor. A interface comunica essa expectativa.
6. O que o detector NÃO faz
Para evitar mal-entendidos, vale listar explicitamente:

Não verifica se citações jurídicas existem (não detecta jurisprudência alucinada).
Não valida números de processo nem dispositivos legais citados.
Não detecta indirect prompt injection semanticamente sutil (texto que parece petição mas insinua decisão).
Não substitui revisão humana — informa, não decide.
Não armazena documentos analisados, então não acumula dataset de uso.
Não pretende ser à prova de adversário motivado: padrões podem ser contornados.

7. Procedimento de auditoria
Qualquer pessoa pode auditar o sistema seguindo estes passos:

Clonar o repositório em github.com/constituicao-tech/framework.
Examinar detector-py/detector/core.py — todos os padrões estão lá, sem ofuscação.
Examinar detector-py/tests/test_core.py — toda a calibração está documentada como caso de teste.
Rodar pytest tests/ — todos os testes precisam passar; falhas indicam regressão.
Adicionar contraexemplos próprios como testes e abrir pull request.

A reprodutibilidade é determinística: a mesma entrada na mesma versão de metodologia produz exatamente o mesmo resultado. O número de versão (0.2.0) está em toda resposta da API.
8. Limites éticos da iniciativa
Este detector existe para proteger sistemas de IA contra manipulação. Por princípio, não publicamos: novos vetores de ataque ainda não vistos em uso público; corpus de exemplos exploráveis; técnicas específicas que tornem mais fácil contornar a própria detecção. Quando recebemos por canal privado relatos de vetores novos, atualizamos a detecção antes de qualquer divulgação pública do vetor.
9. Roadmap metodológico
v0.3 — Detecção semântica. Camada opcional que envia trechos suspeitos a um LLM como segundo opinião sobre intencionalidade. Aumenta acurácia, aumenta custo, perde determinismo.
v0.4 — Verificação de citações. Para o domínio jurídico, conferir se acórdãos, artigos de lei e súmulas citados existem de fato. Reduz alucinação introduzida por IA generativa.
v0.5 — Adaptação setorial. Vetores específicos do setor financeiro (manipulação em pareceres, due diligence, demonstrações), pericial e regulatório.
v1.0 — Framework de avaliação reprodutível. Dataset público rotulado, métricas padronizadas (precisão, recall, F1 por categoria), benchmark contra outras ferramentas.
10. Contato
Críticas técnicas, propostas de novos vetores, contraexemplos: abra issue em github.com/constituicao-tech/framework ou escreva para metodologia@constituicao.tech.

Esta metodologia é versionada. Cada alteração material requer abertura de issue, discussão pública mínima de sete dias, e bump de versão. O histórico completo fica preservado no controle de versão do repositório.