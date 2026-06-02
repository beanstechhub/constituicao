"""
Testes do módulo de integridade acadêmica.
Valida detecção estilométrica local sem API externa.
"""
import pytest
from detector.integridade import analisar_integridade


# ============================================================
# Textos de referência para teste
# ============================================================

TEXTO_HUMANO_TIPICO = """
Eu não sei se faz sentido começar por aqui, mas vou tentar. O problema que o
artigo de Alexy tenta resolver — e que na minha opinião ele resolve só parcialmente —
é como conciliar dois direitos fundamentais quando ambos são plenamente aplicáveis
ao caso. Não é uma colisão simples. Sei lá, quando você lê o Dworkin, ele diz que
princípios têm peso, mas nunca explica direito como medir esse peso. O Alexy pelo
menos dá uma fórmula. Que não funciona sempre, ok, mas pelo menos existe.

Acho que o ponto mais fraco do argumento é quando ele assume que dá pra quantificar
graus de interferência. Na prática? Como um juiz faz isso? Vi uns três acórdãos do
Bundesverfassungsgericht e em nenhum deles o tribunal de fato aplicou a fórmula peso.
Usam a proporcionalidade sim, mas de um jeito muito mais intuitivo do que o Alexy sugere.

Enfim, talvez o mérito não seja prático mas teórico — dar um framework que pelo menos
força transparência na argumentação. Mesmo que o resultado seja subjetivo, o caminho
precisa ser justificado. Isso por si só já é um avanço.
"""

TEXTO_IA_TIPICO = """
A ponderação de princípios constitucionais constitui um dos temas mais relevantes da
teoria constitucional contemporânea. Robert Alexy desenvolveu uma teoria amplamente
reconhecida que propõe a análise de colisões entre direitos fundamentais por meio de
uma fórmula peso que considera a intensidade da interferência em cada princípio envolvido.

Nesse contexto, é fundamental compreender que os princípios constitucionais operam como
mandamentos de otimização, sendo realizados na maior medida possível dentro das condições
fáticas e jurídicas existentes. A proporcionalidade em sentido estrito funciona como
instrumento para determinar qual princípio deve prevalecer em cada caso concreto.

Ademais, cumpre destacar que a teoria da ponderação recebeu significativas contribuições
da jurisprudência do Tribunal Constitucional Federal alemão, que consolidou a aplicação
do princípio da proporcionalidade em suas três dimensões: adequação, necessidade e
proporcionalidade em sentido estrito.

Portanto, conclui-se que a teoria de Alexy oferece um framework analítico consistente
para a resolução de conflitos entre direitos fundamentais, contribuindo para a
racionalidade e transparência da argumentação constitucional.
"""

TEXTO_CURTO = "Este é um texto muito curto para análise confiável."

TEXTO_MISTO = """
Olha, eu li o artigo do Barroso sobre neoconstitucionalismo e achei interessante mas
meio superficial em alguns pontos. Ele fala muito de força normativa da constituição
mas não enfrenta a crítica do Humberto Ávila sobre a inflação de princípios.

Nesse contexto, é fundamental compreender que o neoconstitucionalismo brasileiro
apresenta características distintas do modelo europeu. A centralidade dos direitos
fundamentais e a expansão da jurisdição constitucional constituem elementos definidores
deste paradigma que merecem análise aprofundada.

Enfim sei lá, acho que o Barroso simplifica demais. Mas o texto é de 2005, né.
Muita coisa mudou desde então. O próprio STF mudou bastante a jurisprudência sobre
controle de constitucionalidade concentrado.
"""


# ============================================================
# Testes
# ============================================================

def test_texto_humano_score_baixo():
    r = analisar_integridade(TEXTO_HUMANO_TIPICO)
    assert r.score_ia <= 45, f"Texto humano deveria ter score baixo, got {r.score_ia}"
    assert r.classificacao in ("provavelmente_humano", "zona_cinza")


def test_texto_ia_score_alto():
    r = analisar_integridade(TEXTO_IA_TIPICO)
    # Com texto de ~160 palavras, confiança é reduzida. Score >= 45 é aceitável.
    assert r.score_ia >= 45, f"Texto IA deveria ter score elevado, got {r.score_ia}"
    assert r.classificacao in ("provavelmente_ia", "zona_cinza")


def test_texto_misto_zona_cinza():
    r = analisar_integridade(TEXTO_MISTO)
    # Texto misto pode cair em qualquer zona, mas não deveria ser extremo
    assert 20 <= r.score_ia <= 80, f"Texto misto em extremo: {r.score_ia}"


def test_texto_curto_confianca_baixa():
    r = analisar_integridade(TEXTO_CURTO)
    assert r.confianca == "baixa"


def test_texto_insuficiente():
    r = analisar_integridade("Muito curto.")
    assert r.classificacao == "insuficiente"


def test_texto_vazio():
    r = analisar_integridade("")
    assert r.classificacao == "insuficiente"
    assert r.score_ia == 0.0


def test_features_retornadas():
    r = analisar_integridade(TEXTO_HUMANO_TIPICO)
    assert len(r.features) == 10
    nomes = {f.nome for f in r.features}
    assert "zipf_deviation" in nomes
    assert "burstiness" in nomes
    assert "sentence_rhythm" in nomes


def test_resultado_serializa():
    r = analisar_integridade(TEXTO_IA_TIPICO)
    d = r.to_dict()
    assert "score_ia" in d
    assert "classificacao" in d
    assert "features" in d
    assert isinstance(d["features"], list)


def test_determinismo():
    r1 = analisar_integridade(TEXTO_HUMANO_TIPICO)
    r2 = analisar_integridade(TEXTO_HUMANO_TIPICO)
    assert r1.score_ia == r2.score_ia
    assert r1.classificacao == r2.classificacao


def test_metricas_presentes():
    r = analisar_integridade(TEXTO_IA_TIPICO)
    assert "palavras" in r.metricas
    assert "frases" in r.metricas
    assert r.metricas["palavras"] > 50


def test_aviso_presente():
    r = analisar_integridade(TEXTO_IA_TIPICO)
    assert "determinística" in r.aviso
    assert "humana" in r.aviso
