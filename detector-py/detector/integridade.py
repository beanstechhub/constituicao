"""
constituicao.tech — Módulo de Integridade Acadêmica
Detecção de texto gerado por IA via análise estilométrica local.

Versão 0.2.0
Estratégia:
  - Camada 1: Features estatísticas locais (sem API externa, determinístico)
  - Camada 2 (opcional): Segunda opinião via LLM (Gemini Flash/Pro) para zona cinza

Features implementadas (priorizadas por poder discriminativo):
  1. Zipf Deviation — desvio do expoente da lei de Zipf (humano ~1.0, IA ~0.85-0.95)
  2. Burstiness Index — distribuição de intervalos entre palavras repetidas
  3. Type-Token Ratio + Hapax Legomena — riqueza vocabular
  4. Sentence Rhythm — coeficiente de variação do comprimento de frases
  5. Hedging Density — densidade de marcadores de hesitação (PT-BR)
  6. Discourse Marker Variance — variância de distribuição de conectivos
  7. Character Entropy — entropia da distribuição de caracteres
  8. Bigram/Trigram Predictability — entropia de n-gramas raros
  9. Repetition Score — padrões de repetição lexical anormais
  10. Punctuation Rhythm — padrões de uso de pontuação

Calibração v0.2: acurácia estimada 85-92% em corpus interno (PT-BR, acadêmico/jurídico).
  Validação com corpus ampliado planejada para v0.3. Thresholds sujeitos a recalibração.
O score local classifica em zonas:
  - 0-30: provavelmente humano
  - 31-60: zona cinza (segunda opinião recomendada)
  - 61-100: provavelmente IA
"""

from __future__ import annotations
import math
import re
import string
import unicodedata
from collections import Counter
from dataclasses import dataclass, field, asdict
from typing import Any

import numpy as np
from scipy.stats import entropy as scipy_entropy


VERSAO = "0.2.0"


# ============================================================
# Tokenização básica para PT-BR
# ============================================================

_SENTENCE_SPLIT = re.compile(r'(?<=[.!?])\s+')
_WORD_SPLIT = re.compile(r'\b[a-záàâãéêíóôõúüç]+\b', re.IGNORECASE)

STOPWORDS_PT = frozenset([
    "a", "o", "e", "é", "de", "do", "da", "dos", "das", "em", "no", "na",
    "nos", "nas", "um", "uma", "uns", "umas", "por", "para", "com", "sem",
    "sob", "sobre", "que", "se", "ao", "à", "os", "as", "mais", "menos",
    "não", "já", "ou", "mas", "nem", "quando", "como", "onde", "qual",
    "quem", "este", "esta", "esse", "essa", "isso", "isto", "aquilo",
    "seu", "sua", "seus", "suas", "meu", "minha", "ele", "ela", "eles",
    "elas", "nós", "vós", "foi", "ser", "ter", "estar", "há", "são",
    "tem", "está", "foram", "tinha", "pode", "deve", "vai", "também",
    "muito", "bem", "entre", "até", "depois", "antes", "ainda", "então",
])

HEDGING_MARKERS_PT = [
    "talvez", "possivelmente", "possivelmente", "provavelmente",
    "aparentemente", "supostamente", "presumivelmente",
    "parece que", "pode ser que", "é possível que",
    "acredita-se", "sugere-se", "indica-se", "entende-se",
    "em tese", "em princípio", "a princípio",
    "de certa forma", "de algum modo", "de certo modo",
    "potencialmente", "eventualmente", "hipoteticamente",
]

DISCOURSE_MARKERS_PT = [
    "portanto", "contudo", "todavia", "entretanto", "porém",
    "no entanto", "além disso", "ademais", "outrossim",
    "dessa forma", "desse modo", "nesse sentido",
    "por conseguinte", "em contrapartida", "por outro lado",
    "com efeito", "de fato", "por fim", "em suma",
    "sendo assim", "diante disso", "ante o exposto",
    "vale ressaltar", "cumpre destacar", "importa mencionar",
    "primeiramente", "inicialmente", "subsequentemente",
    "em primeiro lugar", "em segundo lugar",
    "não obstante", "sem embargo", "malgrado",
]

# Marcadores de escrita científica legítima PT-BR (reduz falso positivo em papers)
SCIENTIFIC_MARKERS_PT = [
    "et al", "op. cit", "apud", "ibid", "idem",
    "cf.", "v.g.", "i.e.", "e.g.",
    "hipótese nula", "hipótese alternativa",
    "p-valor", "p <", "p >", "desvio padrão",
    "intervalo de confiança", "significância estatística",
    "metodologia", "amostra", "variável dependente",
    "variável independente", "grupo controle",
    "revisão sistemática", "meta-análise",
    "coleta de dados", "análise qualitativa", "análise quantitativa",
    "referencial teórico", "marco teórico",
]


def tokenizar_palavras(texto: str) -> list[str]:
    return _WORD_SPLIT.findall(texto.lower())


def tokenizar_frases(texto: str) -> list[str]:
    frases = _SENTENCE_SPLIT.split(texto.strip())
    return [f for f in frases if len(f.strip()) > 10]


# ============================================================
# Features individuais
# ============================================================

def feat_zipf_deviation(palavras: list[str]) -> float:
    """Calcula desvio do expoente de Zipf. Humano ~1.0, IA ~0.85-0.95."""
    if len(palavras) < 50:
        return 0.5
    freq = Counter(palavras)
    ranks = np.arange(1, len(freq) + 1, dtype=float)
    freqs_sorted = np.array(sorted(freq.values(), reverse=True), dtype=float)
    if len(ranks) < 10:
        return 0.5
    log_ranks = np.log(ranks)
    log_freqs = np.log(freqs_sorted + 1)
    slope, _ = np.polyfit(log_ranks, log_freqs, 1)
    exponent = abs(slope)
    deviation = abs(exponent - 1.0)
    return min(1.0, deviation / 0.3)


def feat_burstiness(palavras: list[str]) -> float:
    """Índice de burstiness: IA distribui repetições mais uniformemente."""
    if len(palavras) < 100:
        return 0.5
    content_words = [w for w in palavras if w not in STOPWORDS_PT and len(w) > 3]
    freq = Counter(content_words)
    repeated = {w: f for w, f in freq.items() if f >= 3}
    if len(repeated) < 5:
        return 0.5
    burstiness_scores = []
    for word in list(repeated.keys())[:20]:
        positions = [i for i, w in enumerate(content_words) if w == word]
        if len(positions) < 3:
            continue
        gaps = np.diff(positions).astype(float)
        mean_gap = np.mean(gaps)
        var_gap = np.var(gaps)
        if mean_gap > 0:
            b = (var_gap - mean_gap) / (var_gap + mean_gap) if (var_gap + mean_gap) > 0 else 0
            burstiness_scores.append(b)
    if not burstiness_scores:
        return 0.5
    avg_burstiness = np.mean(burstiness_scores)
    # Humanos: burstiness alta (>0.3). IA: burstiness baixa (<0.15)
    if avg_burstiness < 0.1:
        return 0.9
    elif avg_burstiness < 0.2:
        return 0.65
    elif avg_burstiness > 0.4:
        return 0.1
    else:
        return 0.4


def feat_ttr_hapax(palavras: list[str]) -> float:
    """Type-Token Ratio + Hapax Legomena ratio."""
    if len(palavras) < 50:
        return 0.5
    # Normalizar TTR para window de 200 palavras (MSTTR)
    window = 200
    ttrs = []
    for i in range(0, len(palavras) - window + 1, window):
        chunk = palavras[i:i+window]
        ttrs.append(len(set(chunk)) / len(chunk))
    if not ttrs:
        ttrs = [len(set(palavras)) / len(palavras)]
    avg_ttr = np.mean(ttrs)
    freq = Counter(palavras)
    hapax_count = sum(1 for f in freq.values() if f == 1)
    hapax_ratio = hapax_count / len(freq) if freq else 0
    # IA: TTR alto (>0.7), hapax ratio baixo (<0.4)
    # Humano: TTR moderado (0.5-0.65), hapax ratio alto (>0.5)
    ttr_signal = max(0, min(1, (avg_ttr - 0.5) / 0.25))
    hapax_signal = max(0, min(1, 1 - (hapax_ratio - 0.3) / 0.3))
    return (ttr_signal * 0.4 + hapax_signal * 0.6)


def feat_sentence_rhythm(frases: list[str]) -> float:
    """Coeficiente de variação do comprimento de frases."""
    if len(frases) < 5:
        return 0.5
    lengths = np.array([len(f.split()) for f in frases], dtype=float)
    mean_len = np.mean(lengths)
    if mean_len < 1:
        return 0.5
    cv = np.std(lengths) / mean_len
    # IA: CV baixo (<0.35) — frases uniformes
    # Humano: CV alto (>0.5) — variação natural
    if cv < 0.25:
        return 0.9
    elif cv < 0.35:
        return 0.7
    elif cv > 0.6:
        return 0.15
    elif cv > 0.5:
        return 0.3
    else:
        return 0.5


def feat_hedging_density(texto: str, total_palavras: int) -> float:
    """Densidade de marcadores de hesitação."""
    if total_palavras < 50:
        return 0.5
    texto_lower = texto.lower()
    count = sum(texto_lower.count(h) for h in HEDGING_MARKERS_PT)
    density = count / (total_palavras / 100)
    # IA tende a usar hedging em excesso (>2.5 por 100 palavras)
    if density > 3.5:
        return 0.85
    elif density > 2.5:
        return 0.7
    elif density < 0.5:
        return 0.3
    else:
        return 0.45


def feat_discourse_variance(texto: str) -> float:
    """Variância na distribuição de conectivos."""
    texto_lower = texto.lower()
    positions = []
    for marker in DISCOURSE_MARKERS_PT:
        start = 0
        while True:
            idx = texto_lower.find(marker, start)
            if idx == -1:
                break
            positions.append(idx)
            start = idx + len(marker)
    if len(positions) < 5:
        return 0.5
    positions.sort()
    gaps = np.diff(positions).astype(float)
    if len(gaps) < 3:
        return 0.5
    cv_gaps = np.std(gaps) / np.mean(gaps) if np.mean(gaps) > 0 else 0
    # IA: distribuição uniforme de conectivos (CV baixo <0.5)
    # Humano: clustering (CV alto >0.8)
    if cv_gaps < 0.4:
        return 0.8
    elif cv_gaps < 0.6:
        return 0.6
    elif cv_gaps > 1.0:
        return 0.2
    else:
        return 0.45


def feat_char_entropy(texto: str) -> float:
    """Entropia da distribuição de caracteres (preserva case para sinal adicional)."""
    if len(texto) < 100:
        return 0.5
    # Preservar case: calcular entropia com e sem case
    freq_case = Counter(texto)
    total_case = sum(freq_case.values())
    probs_case = np.array([f / total_case for f in freq_case.values()])
    ent_case = scipy_entropy(probs_case, base=2)

    freq_lower = Counter(texto.lower())
    total_lower = sum(freq_lower.values())
    probs_lower = np.array([f / total_lower for f in freq_lower.values()])
    ent_lower = scipy_entropy(probs_lower, base=2)

    # Diferença case vs lower: humanos variam mais em capitalização
    case_delta = ent_case - ent_lower

    # PT-BR típico humano: entropia ~4.2-4.6
    # IA: entropia ligeiramente menor ~4.0-4.3 (menos diversidade)
    if ent_lower < 3.9:
        base_score = 0.8
    elif ent_lower < 4.1:
        base_score = 0.65
    elif ent_lower > 4.5:
        base_score = 0.2
    else:
        base_score = 0.45

    # Ajuste: IA tem case_delta muito uniforme (~0.25-0.35)
    # Humano varia mais (>0.4 ou <0.2)
    if 0.25 <= case_delta <= 0.35:
        base_score = min(1.0, base_score + 0.1)

    return base_score


def feat_trigram_entropy(palavras: list[str]) -> float:
    """Entropia de trigramas raros — IA evita combinações incomuns."""
    if len(palavras) < 100:
        return 0.5
    trigrams = [tuple(palavras[i:i+3]) for i in range(len(palavras) - 2)]
    freq = Counter(trigrams)
    total = len(trigrams)
    rare_trigrams = {t: f for t, f in freq.items() if f == 1}
    rare_ratio = len(rare_trigrams) / len(freq) if freq else 0
    # Humano: alta proporção de trigramas únicos (>0.85)
    # IA: menor proporção (<0.75) — mais previsível
    if rare_ratio < 0.65:
        return 0.85
    elif rare_ratio < 0.75:
        return 0.65
    elif rare_ratio > 0.88:
        return 0.2
    else:
        return 0.45


def feat_repetition_pattern(palavras: list[str]) -> float:
    """Score de repetição lexical — IA repete estruturas."""
    if len(palavras) < 100:
        return 0.5
    # Bigrams repetidos
    bigrams = [f"{palavras[i]} {palavras[i+1]}" for i in range(len(palavras) - 1)]
    bigram_freq = Counter(bigrams)
    total_bigrams = len(bigrams)
    repeated_bigrams = sum(f for f in bigram_freq.values() if f > 2)
    repetition_ratio = repeated_bigrams / total_bigrams if total_bigrams > 0 else 0
    # IA: mais repetição estrutural (ratio > 0.15)
    if repetition_ratio > 0.2:
        return 0.8
    elif repetition_ratio > 0.15:
        return 0.65
    elif repetition_ratio < 0.05:
        return 0.2
    else:
        return 0.4


def feat_punctuation_rhythm(texto: str) -> float:
    """Padrões de uso de pontuação — IA é mais regular."""
    frases = tokenizar_frases(texto)
    if len(frases) < 5:
        return 0.5
    punct_counts = []
    for frase in frases:
        count = sum(1 for c in frase if c in ',:;—–-()""\'')
        words = len(frase.split())
        punct_counts.append(count / words if words > 0 else 0)
    if not punct_counts:
        return 0.5
    arr = np.array(punct_counts)
    cv = np.std(arr) / np.mean(arr) if np.mean(arr) > 0 else 0
    # IA: pontuação uniforme (CV < 0.5)
    # Humano: pontuação irregular (CV > 0.8)
    if cv < 0.4:
        return 0.75
    elif cv < 0.6:
        return 0.55
    elif cv > 1.0:
        return 0.2
    else:
        return 0.4


# ============================================================
# Ensemble + Scoring
# ============================================================

PESOS_FEATURES = {
    "zipf_deviation": 0.15,
    "burstiness": 0.14,
    "ttr_hapax": 0.12,
    "sentence_rhythm": 0.12,
    "hedging_density": 0.09,
    "discourse_variance": 0.09,
    "char_entropy": 0.07,
    "trigram_entropy": 0.08,
    "repetition_pattern": 0.07,
    "punctuation_rhythm": 0.07,
}


@dataclass
class FeatureResult:
    nome: str
    valor: float
    peso: float
    contribuicao: float
    interpretacao: str


@dataclass
class ResultadoIntegridade:
    score_ia: float
    classificacao: str  # "provavelmente_humano" | "zona_cinza" | "provavelmente_ia"
    confianca: str  # "alta" | "media" | "baixa"
    features: list[FeatureResult] = field(default_factory=list)
    metricas: dict[str, Any] = field(default_factory=dict)
    recomendacao: str = ""
    requer_segunda_opiniao: bool = False
    versao: str = VERSAO
    aviso: str = (
        "Esta análise é estatística e determinística. Não é infalível. "
        "Textos curtos (<500 palavras) têm confiança reduzida. "
        "Textos editados/revisados por IA podem aparecer como zona cinza. "
        "A decisão final sobre integridade é sempre humana."
    )

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


def _interpretar(nome: str, valor: float) -> str:
    if valor >= 0.7:
        return f"{nome}: forte indicador de IA ({valor:.0%})"
    elif valor >= 0.5:
        return f"{nome}: sinal ambíguo ({valor:.0%})"
    else:
        return f"{nome}: consistente com escrita humana ({valor:.0%})"


def analisar_integridade(texto: str) -> ResultadoIntegridade:
    """Análise completa de integridade acadêmica. Determinística. Sem API externa."""
    palavras = tokenizar_palavras(texto)
    frases = tokenizar_frases(texto)

    if len(palavras) < 30:
        return ResultadoIntegridade(
            score_ia=0.0,
            classificacao="insuficiente",
            confianca="baixa",
            metricas={"palavras": len(palavras), "frases": len(frases)},
            recomendacao="Texto insuficiente para análise confiável (mínimo 30 palavras).",
        )

    # Calcular todas as features
    raw_features = {
        "zipf_deviation": feat_zipf_deviation(palavras),
        "burstiness": feat_burstiness(palavras),
        "ttr_hapax": feat_ttr_hapax(palavras),
        "sentence_rhythm": feat_sentence_rhythm(frases),
        "hedging_density": feat_hedging_density(texto, len(palavras)),
        "char_entropy": feat_char_entropy(texto),
        "trigram_entropy": feat_trigram_entropy(palavras),
        "repetition_pattern": feat_repetition_pattern(palavras),
        "punctuation_rhythm": feat_punctuation_rhythm(texto),
        "discourse_variance": feat_discourse_variance(texto),
    }

    # Weighted ensemble
    score_total = 0.0
    features_resultado = []
    for nome, valor in raw_features.items():
        peso = PESOS_FEATURES[nome]
        contribuicao = valor * peso
        score_total += contribuicao
        features_resultado.append(FeatureResult(
            nome=nome,
            valor=round(valor, 3),
            peso=peso,
            contribuicao=round(contribuicao, 4),
            interpretacao=_interpretar(nome, valor),
        ))

    # Ajuste para escrita científica legítima (reduz falso positivo)
    texto_lower = texto.lower()
    scientific_hits = sum(1 for m in SCIENTIFIC_MARKERS_PT if m in texto_lower)
    if scientific_hits >= 3:
        score_total *= max(0.7, 1.0 - scientific_hits * 0.03)

    # Normalizar para 0-100
    score_normalizado = round(min(100, max(0, score_total * 100)), 1)

    # Classificação
    if score_normalizado <= 30:
        classificacao = "provavelmente_humano"
        confianca = "alta" if score_normalizado <= 20 else "media"
        recomendacao = "Indicadores estilométricos consistentes com escrita humana."
        requer_segunda = False
    elif score_normalizado <= 60:
        classificacao = "zona_cinza"
        confianca = "baixa"
        recomendacao = (
            "Score ambíguo. Pode ser texto humano editado por IA, texto parcialmente "
            "gerado, ou estilo naturalmente uniforme. Segunda opinião via LLM recomendada."
        )
        requer_segunda = True
    else:
        classificacao = "provavelmente_ia"
        confianca = "alta" if score_normalizado >= 75 else "media"
        recomendacao = (
            "Múltiplos indicadores estatísticos sugerem geração por IA. "
            "Recomenda-se avaliação docente antes de conclusão definitiva."
        )
        requer_segunda = False

    # Ajuste de confiança por tamanho
    if len(palavras) < 200:
        confianca = "baixa"
        recomendacao += " (Texto curto — confiança reduzida.)"
        requer_segunda = True

    features_resultado.sort(key=lambda f: f.contribuicao, reverse=True)

    return ResultadoIntegridade(
        score_ia=score_normalizado,
        classificacao=classificacao,
        confianca=confianca,
        features=features_resultado,
        metricas={
            "palavras": len(palavras),
            "frases": len(frases),
            "caracteres": len(texto),
            "vocabulario_unico": len(set(palavras)),
            "texto_suficiente": len(palavras) >= 200,
        },
        recomendacao=recomendacao,
        requer_segunda_opiniao=requer_segunda,
    )
