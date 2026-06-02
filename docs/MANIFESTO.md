# Manifesto constituicao.tech

## A Constituição da IA Saudável

---

### Preâmbulo

Nós, desenvolvedores, juristas e cidadãos digitais, reconhecemos que a inteligência artificial é uma força transformadora que exige princípios fundantes — não para restringi-la, mas para garantir que ela sirva à dignidade humana.

Assim como a Constituição de 1988 não surgiu contra o povo, mas para ele, a constituicao.tech não surge contra a IA, mas para que ela seja saudável.

---

### Fundamento Jurídico

#### Eficácia Horizontal dos Direitos Fundamentais (Drittwirkung)

Os direitos fundamentais não se limitam à relação vertical cidadão-Estado. Incidem entre particulares. Quando um sistema de IA processa um documento jurídico, ele participa de uma relação onde direitos fundamentais estão em jogo.

**Art. 5º, LIV, CF/88**: Ninguém será privado da liberdade ou de seus bens sem o devido processo legal.

O devido processo legal substancial exige que toda decisão — humana ou algorítmica — seja fundamentada, transparente e passível de controle.

#### Princípio da Proteção Integral e Direito à Educação

**Art. 205, CF/88**: A educação, direito de todos e dever do Estado e da família, será promovida e incentivada com a colaboração da sociedade, visando ao pleno desenvolvimento da pessoa.

**Art. 227, CF/88**: É dever da família, da sociedade e do Estado assegurar à criança, ao adolescente e ao jovem, com absoluta prioridade, o direito à educação.

A integridade acadêmica não é fiscalização punitiva — é proteção do direito à educação. Quando um aluno frauda com IA, ele frauda a si mesmo. Quando uma instituição não tem instrumentos para detectar, ela falha no dever constitucional de promover educação real.

#### Paridade de Armas

Se sistemas de IA podem gerar documentos sofisticados em segundos, as instituições precisam de instrumentos equivalentes para verificar integridade. Sem paridade, o devido processo é ilusão.

#### Boa-fé Objetiva e Princípio da Cooperação

**Art. 5º, CPC/2015**: A boa-fé processual é dever de todos os participantes.

**Art. 6º, CPC/2015**: Todos os sujeitos do processo devem cooperar entre si.

Documentos processados por IA devem manter integridade verificável. A cooperação processual inclui garantir que o que chega ao juízo é o que parece ser.

---

### Os Quatro Artigos

#### Art. I — Integridade de Documentos
*Fundamento: Art. 5º, LIV, CF/88 — Devido Processo Legal*

Nenhum documento processado por sistema de IA será presumido íntegro sem verificação. A detecção de prompt injection protege contra manipulação adversarial de sistemas que processam petições, pareceres e documentos jurídicos.

**Ataques que detectamos:**
- Injeção de instrução (override de sistema)
- Redefinição de papel (sequestro de identidade)
- Exfiltração de prompt (extração de regras)
- Injeção indireta (instrução condicional)
- Esteganografia digital (caracteres invisíveis)
- Jailbreaks documentados

#### Art. II — Integridade Acadêmica
*Fundamento: Art. 205-214, CF/88 — Direito à Educação + Proteção Integral*

O direito à educação inclui o dever de garantir que a avaliação mensure aprendizado real. A detecção de texto gerado por IA via estilometria local protege a meritocracia acadêmica sem depender de APIs externas ou violar privacidade.

**Princípio**: Nenhum veredito binário. O sistema informa probabilidades e recomenda avaliação humana.

**Features analisadas:**
- Desvio da lei de Zipf
- Burstiness (distribuição de repetições)
- Riqueza vocabular (TTR + Hapax)
- Ritmo sentencial
- Densidade de hedging
- Variância de conectivos
- Entropia de caracteres e trigramas
- Padrões de repetição e pontuação

#### Art. III — Autenticidade Digital
*Fundamento: Art. 19, CF/88 — Fé Pública*

A assinatura digital é garantia de autenticidade. Documentos com assinatura copiada, corrompida ou cosmética comprometem a fé pública e a segurança jurídica.

**Ataques que detectamos:**
- Assinatura copiada (ByteRange não cobre conteúdo)
- Hash não confere (documento alterado)
- Modificação pós-assinatura
- Campo cosmético (sem conteúdo criptográfico)
- Certificado expirado ou inválido
- SHA-1 depreciado

#### Art. IV — Integridade Financeira
*Fundamento: Art. 170, CF/88 — Ordem Econômica*

A ordem econômica fundada na valorização do trabalho humano e na livre iniciativa exige proteção contra fraude financeira. O fraud-shield detecta padrões de lavagem, structuring e ataques coordenados em tempo real.

**Padrões que detectamos:**
- Round-trip (depósito + saque sem atividade)
- Smurfing (múltiplas contas, mesmo IP)
- Structuring (fracionamento para evitar COAF)
- Syndicate (saques coordenados)
- Velocity abuse (explosão de frequência)
- Ticket deviation (desvio súbito de valor médio)

---

### Princípios Operacionais

1. **Nenhum veredito binário** — toda decisão é humana
2. **Toda detecção é explicável** — sem caixa-preta
3. **IA constrói defesa** — não apenas superfície de ataque
4. **Privacidade sobre conveniência** — nada é armazenado
5. **Código aberto** — a constituição é pública

---

### Compromisso

Este projeto não é autopromoção. É paridade de armas.

Se a IA pode gerar petições em 30 segundos, o judiciário precisa de ferramentas para verificar integridade em 30 milissegundos.

Se a IA pode produzir um TCC inteiro overnight, a universidade precisa de instrumentos para proteger o direito à educação real.

Se uma assinatura digital pode ser copiada com um editor hexadecimal, o sistema precisa detectar antes que produza efeitos jurídicos.

Se transações fraudulentas podem ocorrer em microsegundos, a defesa precisa operar na mesma escala temporal.

**constituicao.tech** — IA saudável, código aberto, princípios fundantes.

---

*Construído com Claude (Anthropic). Código aberto sob Apache 2.0.*
*Todos os módulos: zero dependência de API externa para análise core.*
*Latência: <50μs (fraud-shield), <100ms (detector-py).*
