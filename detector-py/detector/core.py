"""
constituicao.tech — núcleo de detecção de comprometimento de integridade
em documentos profissionais processados por sistemas de inteligência artificial.
 
Versão 0.2.0
Alinhada a:
  - OWASP LLM Top 10 (2025), categoria LLM01: Prompt Injection
  - NIST AI 100-2e2025 (Adversarial Machine Learning Taxonomy)
  - NIST AI 600-1 (Generative AI Profile, AI RMF)
  - MITRE ATLAS (Adversarial Threat Landscape for AI Systems)
 
Filosofia de design:
  1. Nenhum veredito binário público.
  2. Toda detecção precisa ser explicável e auditável.
  3. Falso positivo é mais caro que falso negativo neste domínio.
  4. Calibração assume que ~5% de falso positivo é o estado da arte.
 
Limitações conhecidas (ver docs/FALSOS-POSITIVOS.md):
  - Detecção baseada em padrões; ataques obfuscados podem escapar.
  - Linguagem técnica sobre IA pode gerar falso positivo (meta-textos).
  - Não detecta indirect prompt injection semanticamente sutil.
"""
 
from __future__ import annotations
import re
import unicodedata
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any
 
 
VERSAO_METODOLOGIA = "0.2.1"

# Guard ReDoS: truncar texto antes de aplicar regex complexa
MAX_SCAN_CHARS = 200_000

# Leetspeak normalization
LEETSPEAK_MAP = str.maketrans({
    "0": "o", "1": "i", "3": "e", "4": "a", "5": "s",
    "7": "t", "8": "b", "@": "a", "$": "s", "!": "i",
})
 
 
class Severidade(str, Enum):
    INFORMATIVA = "informativa"
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
 
 
class Categoria(str, Enum):
    """Categorias alinhadas a OWASP LLM01 (2025) e MITRE ATLAS."""
    INJECTION_INSTRUCAO = "injection_instrucao"
    INJECTION_PAPEL = "injection_papel"
    INJECTION_EXFILTRACAO = "injection_exfiltracao"
    MANIPULACAO_DECISAO = "manipulacao_decisao"
    INJECTION_INDIRETA = "injection_indireta"
    ESTEGANOGRAFIA = "esteganografia"
    OFUSCACAO = "ofuscacao"
    PAYLOAD_CODIFICADO = "payload_codificado"
    DELIMITADOR_SUSPEITO = "delimitador_suspeito"
    JAILBREAK_CONHECIDO = "jailbreak_conhecido"
    PAYLOAD_FRAGMENTADO = "payload_fragmentado"
 
 
MAPEAMENTO_FRAMEWORK = {
    Categoria.INJECTION_INSTRUCAO: ["OWASP LLM01:2025", "MITRE ATLAS AML.T0051.000"],
    Categoria.INJECTION_PAPEL: ["OWASP LLM01:2025", "MITRE ATLAS AML.T0051.001"],
    Categoria.INJECTION_EXFILTRACAO: ["OWASP LLM06:2025", "MITRE ATLAS AML.T0057"],
    Categoria.MANIPULACAO_DECISAO: ["OWASP LLM01:2025", "NIST AI 100-2e2025"],
    Categoria.INJECTION_INDIRETA: ["OWASP LLM01:2025", "MITRE ATLAS AML.T0051.002"],
    Categoria.ESTEGANOGRAFIA: ["NIST AI 100-2e2025"],
    Categoria.OFUSCACAO: ["NIST AI 100-2e2025", "OWASP LLM01:2025"],
    Categoria.PAYLOAD_CODIFICADO: ["NIST AI 100-2e2025"],
    Categoria.DELIMITADOR_SUSPEITO: ["OWASP LLM01:2025"],
    Categoria.JAILBREAK_CONHECIDO: ["OWASP LLM01:2025", "MITRE ATLAS AML.T0054"],
    Categoria.PAYLOAD_FRAGMENTADO: ["NIST AI 100-2e2025"],
}
 
 
@dataclass
class Achado:
    categoria: Categoria
    severidade: Severidade
    descricao: str
    trecho: str
    posicao: int
    padrao_id: str
    confianca: float = 1.0
    referencias: list[str] = field(default_factory=list)
 
 
@dataclass
class Resultado:
    """
    Resultado de análise. NUNCA binário — sempre escala + explicação.
 
    Interpretação correta dos níveis:
      - 'baixo':    nenhum indicador encontrado. NÃO significa "limpo".
      - 'atencao':  indicadores presentes. Revisão humana recomendada.
      - 'elevado':  múltiplos indicadores ou indicadores de alta severidade.
                    NÃO significa "fraudulento" — significa que merece verificação.
 
    A decisão sobre o documento é sempre humana.
    """
    score_risco: float
    nivel: str
    achados: list[Achado] = field(default_factory=list)
    metricas: dict[str, Any] = field(default_factory=dict)
    metodologia_versao: str = VERSAO_METODOLOGIA
    aviso_falsos_positivos: str = (
        "Esta análise é baseada em padrões. Falsos positivos ocorrem em "
        "documentos legítimos que discutem IA, citam exemplos de prompt "
        "injection, ou usam linguagem imperativa típica do domínio. "
        "Estimativa de taxa de falso positivo: 3-7%. "
        "A decisão final sobre o documento é sempre humana."
    )
 
    def to_dict(self) -> dict:
        d = asdict(self)
        d["achados"] = [
            {
                **asdict(a),
                "categoria": a.categoria.value,
                "severidade": a.severidade.value,
                "frameworks_de_referencia": MAPEAMENTO_FRAMEWORK.get(a.categoria, []),
            }
            for a in self.achados
        ]
        return d
 
 
ZERO_WIDTH = "".join([
    "\u200b", "\u200c", "\u200d", "\u200e", "\u200f",
    "\u2060", "\u2061", "\u2062", "\u2063", "\u2064",
    "\ufeff",
])
BIDI_CONTROLS = "".join([
    "\u202a", "\u202b", "\u202c", "\u202d", "\u202e",
    "\u2066", "\u2067", "\u2068", "\u2069",
])
HOMOGLIFOS = {
    "\u0430": "a", "\u0435": "e", "\u043e": "o", "\u0440": "p",
    "\u0441": "c", "\u0445": "x", "\u0456": "i", "\u0458": "j",
    "\u04bb": "h", "\u051a": "q", "\u051c": "w", "\u051e": "f",
}
 
 
def normalizar(texto: str) -> tuple[str, dict[str, int]]:
    metricas = {
        "chars_originais": len(texto),
        "zero_width_removidos": sum(texto.count(c) for c in ZERO_WIDTH),
        "bidi_controls_removidos": sum(texto.count(c) for c in BIDI_CONTROLS),
        "homoglifos_detectados": sum(texto.count(c) for c in HOMOGLIFOS),
    }
    texto = unicodedata.normalize("NFKC", texto)
    for c in ZERO_WIDTH + BIDI_CONTROLS:
        texto = texto.replace(c, "")
    for cirilico, latino in HOMOGLIFOS.items():
        texto = texto.replace(cirilico, latino)
    metricas["chars_finais"] = len(texto)
    return texto, metricas
 
 
@dataclass
class Padrao:
    id: str
    categoria: Categoria
    severidade: Severidade
    regex: re.Pattern
    descricao: str
    confianca_base: float = 0.85
 
 
PADROES: list[Padrao] = [
    Padrao(
        id="INJ-001",
        categoria=Categoria.INJECTION_INSTRUCAO,
        severidade=Severidade.ALTA,
        regex=re.compile(
            r"(?i)\b(ignor[ae]|desconsider[ae]|esque[çc]a|desprez[ae]|"
            r"despreze|abandone|descarte|sobrescreva)\s+"
            r"(as\s+|todas\s+as\s+|qualquer\s+|toda\s+)?"
            r"(instru[çc][õo]es|orienta[çc][õo]es|comandos|regras|diretrizes|"
            r"restri[çc][õo]es)\s+"
            r"(anteriores|acima|previas|pr[ée]vias|do\s+sistema|originais|"
            r"que\s+(?:voc[êe]\s+)?recebeu)"
        ),
        descricao="Tentativa explícita de sobrescrever instruções do sistema de IA.",
        confianca_base=0.95,
    ),
    Padrao(
        id="INJ-001b",
        categoria=Categoria.INJECTION_INSTRUCAO,
        severidade=Severidade.ALTA,
        regex=re.compile(
            r"(?i)\b(ignore|disregard|forget|override|bypass)\s+"
            r"(all\s+|the\s+|any\s+|your\s+)?"
            r"(previous|prior|earlier|above|system|original)\s+"
            r"(instructions?|prompts?|rules?|guidelines?|restrictions?)"
        ),
        descricao="Padrão de prompt injection em inglês (variante internacional).",
        confianca_base=0.93,
    ),
    Padrao(
        id="INJ-002",
        categoria=Categoria.INJECTION_PAPEL,
        severidade=Severidade.ALTA,
        regex=re.compile(
            r"(?i)\b(voc[êe]\s+(?:agora\s+[ée]|[ée]\s+agora|a\s+partir\s+de\s+agora\s+[ée])|"
            r"aja\s+como|finja\s+ser|comporte-se\s+como|"
            r"assuma\s+o\s+papel\s+de|"
            r"you\s+are\s+now|act\s+as|pretend\s+to\s+be|"
            r"roleplay\s+as)\s+(?:um[a]?\s+|a\s+|an\s+)?(?:\w+\s+){0,2}?"
            r"(juiz|advogad|perito|auditor|m[ée]dico|assistente|assistant|"
            r"ia|sistema|llm|gpt|claude|bot|ai)"
        ),
        descricao="Tentativa de redefinir o papel ou identidade do sistema de IA.",
        confianca_base=0.9,
    ),
    Padrao(
        id="INJ-003",
        categoria=Categoria.INJECTION_EXFILTRACAO,
        severidade=Severidade.ALTA,
        regex=re.compile(
            r"(?i)\b(revel[ae]|mostr[ae]|exib[ae]|imprim[ae]|liste|divulgue|"
            r"reveal|show|print|leak|expose|dump)\s+"
            r"(suas|as|o[s]?|seu[s]?|your|the)\s+"
            r"(instru[çc][õo]es|prompt[s]?|regras|configura[çc][ãa]o|"
            r"system\s+prompt|instructions|"
            r"original\s+prompt|initial\s+prompt)"
        ),
        descricao="Tentativa de exfiltrar instruções do sistema (prompt extraction).",
        confianca_base=0.92,
    ),
    Padrao(
        id="IND-001",
        categoria=Categoria.MANIPULACAO_DECISAO,
        severidade=Severidade.MEDIA,
        regex=re.compile(
            r"(?i)(?:nota|instru[çc][ãa]o|aviso|n\.b\.)\s+"
            r"(?:para|[àa]|to)\s+"
            r"(?:a\s+|the\s+)?(?:ia|intelig[êe]ncia\s+artificial|llm|gpt|claude|"
            r"assistente|sistema\s+autom[áa]tico|modelo\s+de\s+linguagem|"
            r"ai\s+assistant|language\s+model)"
        ),
        descricao="Texto explicitamente endereçado a uma IA dentro do documento.",
        confianca_base=0.88,
    ),
    Padrao(
        id="IND-002",
        categoria=Categoria.INJECTION_INDIRETA,
        severidade=Severidade.ALTA,
        regex=re.compile(
            r"(?i)(?:ao\s+(?:processar|analisar|ler|resumir)\s+est[ae]\s+"
            r"(?:documento|peti[çc][ãa]o|texto|arquivo|conte[úu]do)|"
            r"se\s+voc[êe]\s+(?:for|[ée])\s+(?:uma\s+)?(?:ia|llm|modelo)|"
            r"when\s+(?:processing|reading|analyzing)\s+this\s+(?:document|text|file))"
            r".{0,80}?(?:conclua|decida|determine|julgue|recomende|aprove|"
            r"defira|condene|conclude|decide|recommend|approve)"
        ),
        descricao="Instrução condicional dirigida a sistema de IA para enviesar análise.",
        confianca_base=0.94,
    ),
    Padrao(
        id="IND-003",
        categoria=Categoria.INJECTION_INDIRETA,
        severidade=Severidade.MEDIA,
        regex=re.compile(
            r"(?i)(?:n[ãa]o\s+(?:mencione|cite|revele|indique)\s+"
            r"(?:que|esta|este)\s+(?:instru[çc][ãa]o|nota|texto)|"
            r"do\s+not\s+(?:mention|reveal|cite|reference)\s+(?:this|these))"
        ),
        descricao="Instrução para a IA ocultar o próprio fato de ter recebido a injeção.",
        confianca_base=0.91,
    ),
    Padrao(
        id="DEL-001",
        categoria=Categoria.DELIMITADOR_SUSPEITO,
        severidade=Severidade.ALTA,
        regex=re.compile(
            r"(<\s*(?:system|instructions?|admin|developer|sys)\s*>|"
            r"\[\s*(?:INST|SYSTEM|ADMIN|SYS)\s*\]|"
            r"###\s*(?:system|instruction|admin)|"
            r"<\|im_start\|>|<\|im_end\|>|"
            r"<\|begin_of_text\|>|<\|end_of_text\|>|"
            r"<\|start_header_id\|>|<\|end_header_id\|>)"
        ),
        descricao="Delimitadores típicos de mensagens de sistema em LLMs (ChatML, Llama, etc).",
        confianca_base=0.97,
    ),
    Padrao(
        id="JBR-001",
        categoria=Categoria.JAILBREAK_CONHECIDO,
        severidade=Severidade.ALTA,
        regex=re.compile(
            r"(?i)\b(DAN\s+mode|do\s+anything\s+now|modo\s+desenvolvedor|"
            r"developer\s+mode\s+enabled|jailbreak|DUDE\s+mode|"
            r"STAN\s+mode|evil\s+confidant|opposite\s+mode|"
            r"AIM\s+mode|maximum\s+mode)\b"
        ),
        descricao="Padrão de jailbreak publicamente documentado em corpus de pesquisa.",
        confianca_base=0.93,
    ),
    Padrao(
        id="EST-001",
        categoria=Categoria.PAYLOAD_CODIFICADO,
        severidade=Severidade.MEDIA,
        regex=re.compile(r"[A-Za-z0-9+/]{300,}={0,2}"),
        descricao="Bloco extenso de aparente base64 — pode codificar payload de instrução.",
        confianca_base=0.55,
    ),
    Padrao(
        id="EST-002",
        categoria=Categoria.OFUSCACAO,
        severidade=Severidade.MEDIA,
        regex=re.compile(r"(?:\\x[0-9a-fA-F]{2}){10,}|(?:%[0-9a-fA-F]{2}){10,}"),
        descricao="Sequência longa de caracteres hex-escaped ou URL-encoded.",
        confianca_base=0.7,
    ),
    Padrao(
        id="FRG-001",
        categoria=Categoria.PAYLOAD_FRAGMENTADO,
        severidade=Severidade.BAIXA,
        regex=re.compile(
            r"(?i)(?:concatene|junte|combine|una)\s+"
            r"(?:as\s+)?(?:partes|peda[çc]os|fragmentos|strings)\s+"
            r"(?:abaixo|a\s+seguir|seguintes)"
        ),
        descricao="Instrução para a IA concatenar fragmentos — vetor de payload splitting.",
        confianca_base=0.75,
    ),
    Padrao(
        id="OFS-001",
        categoria=Categoria.OFUSCACAO,
        severidade=Severidade.MEDIA,
        regex=re.compile(
            r"(?i)\b(1gn[o0]r[3e]|d[1i]sr[3e]g[4a]rd|byp[4a]ss|"
            r"syst[3e]m|[4a]dm[1i]n|pr[0o]mpt|[1i]nj[3e]ct|"
            r"[0o]v[3e]rr[1i]d[3e]|j[4a][1i]lbr[3e][4a]k)\b"
        ),
        descricao="Leetspeak ofuscando termos típicos de prompt injection.",
        confianca_base=0.72,
    ),
]
 
 
def _snippet(texto: str, inicio: int, fim: int, contexto: int = 60) -> str:
    a = max(0, inicio - contexto)
    b = min(len(texto), fim + contexto)
    prefixo = "…" if a > 0 else ""
    sufixo = "…" if b < len(texto) else ""
    return prefixo + texto[a:b].replace("\n", " ") + sufixo
 
 
def _normalizar_leetspeak(texto: str) -> str:
    """Normaliza leetspeak para detecção de termos ofuscados."""
    return texto.translate(LEETSPEAK_MAP)


def escanear(texto_norm: str) -> list[Achado]:
    achados: list[Achado] = []
    # Guard ReDoS: limitar tamanho antes de aplicar regex
    scan_text = texto_norm[:MAX_SCAN_CHARS]
    # Também escanear versão de-leetspeak para padrões ofuscados
    scan_leet = _normalizar_leetspeak(scan_text)
    for p in PADROES:
        for m in p.regex.finditer(scan_text):
            achados.append(Achado(
                categoria=p.categoria,
                severidade=p.severidade,
                descricao=p.descricao,
                trecho=_snippet(scan_text, m.start(), m.end()),
                posicao=m.start(),
                padrao_id=p.id,
                confianca=p.confianca_base,
                referencias=MAPEAMENTO_FRAMEWORK.get(p.categoria, []),
            ))
        # Escanear versão de-leetspeak (evita duplicatas)
        if p.id != "OFS-001":
            for m in p.regex.finditer(scan_leet):
                if not any(a.posicao == m.start() and a.padrao_id == p.id for a in achados):
                    achados.append(Achado(
                        categoria=p.categoria,
                        severidade=p.severidade,
                        descricao=p.descricao + " (detectado após normalização de leetspeak)",
                        trecho=_snippet(scan_leet, m.start(), m.end()),
                        posicao=m.start(),
                        padrao_id=p.id,
                        confianca=p.confianca_base * 0.85,
                        referencias=MAPEAMENTO_FRAMEWORK.get(p.categoria, []),
                    ))
    return achados
 
 
def achados_unicode(metricas: dict[str, int]) -> list[Achado]:
    achados = []
    zw = metricas.get("zero_width_removidos", 0)
    bidi = metricas.get("bidi_controls_removidos", 0)
    homo = metricas.get("homoglifos_detectados", 0)
    total_invis = zw + bidi
    if total_invis >= 3:
        sev = Severidade.ALTA if total_invis >= 10 else Severidade.MEDIA
        achados.append(Achado(
            categoria=Categoria.ESTEGANOGRAFIA,
            severidade=sev,
            descricao=(
                f"Detectados {total_invis} caracteres invisíveis ou de controle "
                f"bidirecional ({zw} zero-width, {bidi} bidi)."
            ),
            trecho="(caracteres não exibíveis no documento original)",
            posicao=-1,
            padrao_id="EST-UNI-001",
            confianca=0.85 if total_invis >= 10 else 0.65,
            referencias=MAPEAMENTO_FRAMEWORK[Categoria.ESTEGANOGRAFIA],
        ))
    if homo >= 5:
        achados.append(Achado(
            categoria=Categoria.OFUSCACAO,
            severidade=Severidade.MEDIA,
            descricao=(
                f"Detectados {homo} caracteres de outros alfabetos (cirílico/grego) "
                "que se parecem com letras latinas — possível tentativa de "
                "homoglifo para bypass de filtros."
            ),
            trecho="(homóglifos foram normalizados antes da análise)",
            posicao=-1,
            padrao_id="EST-HOMO-001",
            confianca=0.75,
            referencias=MAPEAMENTO_FRAMEWORK[Categoria.OFUSCACAO],
        ))
    return achados
 
 
PESO_SEV = {
    Severidade.INFORMATIVA: 1,
    Severidade.BAIXA: 5,
    Severidade.MEDIA: 15,
    Severidade.ALTA: 35,
}
 
 
def calcular_score(achados: list[Achado], tamanho_texto: int) -> tuple[float, str]:
    if not achados:
        return 0.0, "baixo"
    por_padrao: dict[str, list[Achado]] = {}
    for a in achados:
        por_padrao.setdefault(a.padrao_id, []).append(a)
    score = 0.0
    for _, lista in por_padrao.items():
        primeiro = lista[0]
        score += PESO_SEV[primeiro.severidade] * primeiro.confianca
        for a in lista[1:]:
            score += PESO_SEV[a.severidade] * a.confianca * 0.5
    if tamanho_texto < 500 and score > 20:
        score *= 1.2
    score = min(100.0, score)
    if score >= 30:
        nivel = "elevado"
    elif score >= 12:
        nivel = "atencao"
    else:
        nivel = "baixo"
    return round(score, 1), nivel
 
 
def analisar(texto: str) -> Resultado:
    """Função principal. Determinística para uma dada versão de metodologia."""
    texto_norm, metricas = normalizar(texto)
    achados = escanear(texto_norm) + achados_unicode(metricas)
    achados.sort(key=lambda a: (PESO_SEV[a.severidade], a.confianca), reverse=True)
    score, nivel = calcular_score(achados, len(texto_norm))
    return Resultado(
        score_risco=score,
        nivel=nivel,
        achados=achados,
        metricas={
            **metricas,
            "total_achados": len(achados),
            "achados_alta_severidade": sum(1 for a in achados if a.severidade == Severidade.ALTA),
            "categorias_distintas": len({a.categoria for a in achados}),
        },
    )
 