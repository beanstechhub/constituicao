"""
constituicao.tech — Módulo de Verificação de Assinatura Digital
Detecta documentos PDF com assinatura copiada, corrompida ou inválida.

Versão 0.2.0

Ataques detectados:
  1. Assinatura copiada de outro documento (ByteRange não cobre o conteúdo)
  2. Hash da assinatura não bate com o conteúdo real
  3. Documento modificado após assinatura
  4. Campo de assinatura presente mas objeto criptográfico ausente/inválido
  5. Certificado expirado ou cadeia inválida
  6. ByteRange com lacunas (bytes não cobertos)

Dependências: pyhanko, pypdf, cryptography
"""

from __future__ import annotations
import hashlib
import io
import struct
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, IO

try:
    from pyhanko.sign.validation import validate_pdf_signature
    from pyhanko.pdf_utils.reader import PdfFileReader
    from pyhanko.sign.fields import enumerate_sig_fields
    PYHANKO_DISPONIVEL = True
except ImportError:
    PYHANKO_DISPONIVEL = False

try:
    import pypdf
    PYPDF_DISPONIVEL = True
except ImportError:
    PYPDF_DISPONIVEL = False


VERSAO = "0.2.0"


class StatusAssinatura(str, Enum):
    VALIDA = "valida"
    INVALIDA = "invalida"
    CORROMPIDA = "corrompida"
    COPIADA = "copiada"
    MODIFICADA_APOS = "modificada_apos_assinatura"
    AUSENTE = "ausente"
    CAMPO_SEM_ASSINATURA = "campo_sem_assinatura"
    CERTIFICADO_INVALIDO = "certificado_invalido"
    ERRO_ANALISE = "erro_analise"


class Severidade(str, Enum):
    INFO = "informativa"
    ALERTA = "alerta"
    CRITICO = "critico"


@dataclass
class AchadoAssinatura:
    status: StatusAssinatura
    severidade: Severidade
    descricao: str
    detalhes: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResultadoAssinatura:
    tem_assinatura: bool
    total_assinaturas: int
    achados: list[AchadoAssinatura] = field(default_factory=list)
    assinaturas_validas: int = 0
    assinaturas_invalidas: int = 0
    risco: str = "baixo"  # "baixo" | "alto"
    metricas: dict[str, Any] = field(default_factory=dict)
    versao: str = VERSAO
    aviso: str = (
        "Verificação de assinatura digital não substitui validação em "
        "certificadora oficial (ICP-Brasil). Documentos com assinatura "
        "inválida podem ter sido adulterados ou simplesmente corrompidos "
        "durante transmissão."
    )

    def to_dict(self) -> dict:
        d = asdict(self)
        d["achados"] = [
            {**asdict(a), "status": a.status.value, "severidade": a.severidade.value}
            for a in self.achados
        ]
        return d


# ============================================================
# Verificações sem pyhanko (fallback com pypdf)
# ============================================================

def _verificar_byterange_basico(pdf_bytes: bytes, byte_range: list[int]) -> dict[str, Any]:
    """Verifica se ByteRange cobre o documento adequadamente."""
    resultado = {"valido": True, "problemas": []}
    tamanho_pdf = len(pdf_bytes)

    if len(byte_range) != 4:
        resultado["valido"] = False
        resultado["problemas"].append("ByteRange deveria ter 4 elementos")
        return resultado

    offset1, length1, offset2, length2 = byte_range

    if offset1 != 0:
        resultado["valido"] = False
        resultado["problemas"].append(f"ByteRange não começa em 0 (começa em {offset1})")

    bytes_cobertos = length1 + length2
    gap = offset2 - (offset1 + length1)
    fim_cobertura = offset2 + length2

    if fim_cobertura < tamanho_pdf - 1:
        lacuna = tamanho_pdf - fim_cobertura
        if lacuna > 100:
            resultado["valido"] = False
            resultado["problemas"].append(
                f"ByteRange não cobre final do documento ({lacuna} bytes descobertos). "
                "Possível assinatura copiada ou documento modificado após assinatura."
            )

    if gap < 0:
        resultado["valido"] = False
        resultado["problemas"].append("ByteRange tem sobreposição — estrutura inválida")

    resultado["bytes_cobertos"] = bytes_cobertos
    resultado["tamanho_pdf"] = tamanho_pdf
    resultado["gap_assinatura"] = gap
    resultado["cobertura_pct"] = round(bytes_cobertos / tamanho_pdf * 100, 1) if tamanho_pdf > 0 else 0

    return resultado


def _extrair_byteranges_pypdf(pdf_bytes: bytes) -> list[dict[str, Any]]:
    """Extrai info de assinatura usando pypdf (fallback)."""
    assinaturas = []
    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        if "/AcroForm" not in reader.trailer.get("/Root", {}):
            return assinaturas

        root = reader.trailer["/Root"]
        acroform = root.get("/AcroForm", {})
        fields = acroform.get("/Fields", [])

        for field_ref in fields:
            field_obj = field_ref.get_object() if hasattr(field_ref, 'get_object') else field_ref
            ft = field_obj.get("/FT", "")
            if str(ft) == "/Sig":
                sig_info = {"campo_nome": str(field_obj.get("/T", "unknown"))}
                v = field_obj.get("/V")
                if v is None:
                    sig_info["status"] = "campo_sem_valor"
                else:
                    sig_obj = v.get_object() if hasattr(v, 'get_object') else v
                    byte_range = sig_obj.get("/ByteRange")
                    if byte_range:
                        br = [int(x) for x in byte_range]
                        sig_info["byte_range"] = br
                        sig_info["verificacao_br"] = _verificar_byterange_basico(pdf_bytes, br)
                    contents = sig_obj.get("/Contents")
                    sig_info["tem_contents"] = contents is not None
                    # Detectar /Contents vazio (hex zerada = assinatura cosmética)
                    if contents is not None:
                        raw = bytes(contents) if hasattr(contents, '__bytes__') else b""
                        sig_info["contents_vazio"] = (
                            len(raw) > 0 and all(b == 0 for b in raw)
                        )
                    sig_info["filter"] = str(sig_obj.get("/Filter", ""))
                    sig_info["sub_filter"] = str(sig_obj.get("/SubFilter", ""))
                assinaturas.append(sig_info)
    except Exception as e:
        assinaturas.append({"erro": str(e)})

    return assinaturas


def _verificar_hash_conteudo(pdf_bytes: bytes, byte_range: list[int]) -> dict[str, Any]:
    """Calcula hash do conteúdo coberto pelo ByteRange."""
    if len(byte_range) != 4:
        return {"valido": False, "motivo": "ByteRange inválido"}

    offset1, length1, offset2, length2 = byte_range
    try:
        parte1 = pdf_bytes[offset1:offset1 + length1]
        parte2 = pdf_bytes[offset2:offset2 + length2]
        conteudo_assinado = parte1 + parte2
        hash_sha256 = hashlib.sha256(conteudo_assinado).hexdigest()
        return {
            "hash_conteudo": hash_sha256,
            "bytes_hasheados": len(conteudo_assinado),
            "parte1_tamanho": len(parte1),
            "parte2_tamanho": len(parte2),
        }
    except Exception as e:
        return {"valido": False, "motivo": str(e)}


# ============================================================
# Verificação com pyhanko (completa)
# ============================================================

def _verificar_pyhanko(pdf_bytes: bytes) -> list[AchadoAssinatura]:
    """Verificação completa usando pyhanko."""
    achados = []
    try:
        reader = PdfFileReader(io.BytesIO(pdf_bytes))
        sig_fields = list(enumerate_sig_fields(reader))

        if not sig_fields:
            return achados

        for field_name, sig_obj, sig_field in sig_fields:
            if sig_obj is None:
                achados.append(AchadoAssinatura(
                    status=StatusAssinatura.CAMPO_SEM_ASSINATURA,
                    severidade=Severidade.ALERTA,
                    descricao=f"Campo '{field_name}' existe mas não contém assinatura criptográfica.",
                    detalhes={"campo": field_name},
                ))
                continue

            try:
                status = validate_pdf_signature(reader, sig_field)

                if status.bottom_line:
                    achados.append(AchadoAssinatura(
                        status=StatusAssinatura.VALIDA,
                        severidade=Severidade.INFO,
                        descricao=f"Assinatura '{field_name}' válida. Certificado e hash verificados.",
                        detalhes={
                            "campo": field_name,
                            "assinante": str(status.signer_reported_name) if hasattr(status, 'signer_reported_name') else "desconhecido",
                            "integridade": True,
                        },
                    ))
                else:
                    if status.modification_level is not None:
                        achados.append(AchadoAssinatura(
                            status=StatusAssinatura.MODIFICADA_APOS,
                            severidade=Severidade.CRITICO,
                            descricao=f"Documento modificado após assinatura '{field_name}'.",
                            detalhes={"campo": field_name, "nivel_modificacao": str(status.modification_level)},
                        ))
                    else:
                        achados.append(AchadoAssinatura(
                            status=StatusAssinatura.INVALIDA,
                            severidade=Severidade.CRITICO,
                            descricao=f"Assinatura '{field_name}' inválida — hash ou certificado não verificam.",
                            detalhes={"campo": field_name},
                        ))
            except Exception as e:
                achados.append(AchadoAssinatura(
                    status=StatusAssinatura.CORROMPIDA,
                    severidade=Severidade.CRITICO,
                    descricao=f"Assinatura '{field_name}' corrompida — impossível validar: {str(e)[:100]}",
                    detalhes={"campo": field_name, "erro": str(e)[:200]},
                ))

    except Exception as e:
        achados.append(AchadoAssinatura(
            status=StatusAssinatura.ERRO_ANALISE,
            severidade=Severidade.ALERTA,
            descricao=f"Erro ao processar assinaturas do PDF: {str(e)[:100]}",
            detalhes={"erro": str(e)[:200]},
        ))

    return achados


# ============================================================
# Função principal
# ============================================================

def verificar_assinatura(pdf_stream: IO[bytes]) -> ResultadoAssinatura:
    """
    Verifica integridade de assinaturas digitais em PDF.
    Detecta: copiada, corrompida, modificada após, campo vazio.
    """
    pdf_bytes = pdf_stream.read()

    # Verificação rápida: é PDF?
    if not pdf_bytes[:5] == b'%PDF-':
        return ResultadoAssinatura(
            tem_assinatura=False,
            total_assinaturas=0,
            achados=[AchadoAssinatura(
                status=StatusAssinatura.ERRO_ANALISE,
                severidade=Severidade.ALERTA,
                descricao="Arquivo não é um PDF válido.",
            )],
            risco="baixo",
        )

    achados: list[AchadoAssinatura] = []

    # Camada 1: pyhanko (se disponível)
    if PYHANKO_DISPONIVEL:
        achados.extend(_verificar_pyhanko(pdf_bytes))

    # Camada 2: verificação manual de ByteRange (sempre roda)
    if PYPDF_DISPONIVEL:
        sigs_info = _extrair_byteranges_pypdf(pdf_bytes)
        for sig in sigs_info:
            if "erro" in sig:
                continue
            if sig.get("status") == "campo_sem_valor":
                if not any(a.status == StatusAssinatura.CAMPO_SEM_ASSINATURA for a in achados):
                    achados.append(AchadoAssinatura(
                        status=StatusAssinatura.CAMPO_SEM_ASSINATURA,
                        severidade=Severidade.CRITICO,
                        descricao=(
                            f"Campo de assinatura '{sig.get('campo_nome', '?')}' presente "
                            "mas sem conteúdo criptográfico. Possível cópia cosmética."
                        ),
                        detalhes=sig,
                    ))
                continue

            if not sig.get("tem_contents"):
                achados.append(AchadoAssinatura(
                    status=StatusAssinatura.CORROMPIDA,
                    severidade=Severidade.CRITICO,
                    descricao="Objeto de assinatura sem campo /Contents — estrutura corrompida.",
                    detalhes=sig,
                ))
                continue

            # Alerta SHA-1 depreciado
            sub_filter = sig.get("sub_filter", "").lower()
            if "sha1" in sub_filter or "sha-1" in sub_filter:
                achados.append(AchadoAssinatura(
                    status=StatusAssinatura.INVALIDA,
                    severidade=Severidade.ALERTA,
                    descricao=(
                        "Assinatura usa SHA-1 (depreciado desde 2017). "
                        "Vulnerável a colisão — não deve ser considerada confiável."
                    ),
                    detalhes={"sub_filter": sig.get("sub_filter"), "campo": sig.get("campo_nome")},
                ))

            # /Contents zerado = assinatura cosmética (sem valor criptográfico)
            if sig.get("contents_vazio"):
                achados.append(AchadoAssinatura(
                    status=StatusAssinatura.COPIADA,
                    severidade=Severidade.CRITICO,
                    descricao=(
                        "Campo /Contents contém apenas bytes nulos — assinatura cosmética "
                        "sem valor criptográfico. Documento NÃO está assinado de fato."
                    ),
                    detalhes={"campo": sig.get("campo_nome")},
                ))

            br = sig.get("byte_range")
            if br:
                verif = sig.get("verificacao_br", {})
                if not verif.get("valido", True):
                    for problema in verif.get("problemas", []):
                        achados.append(AchadoAssinatura(
                            status=StatusAssinatura.COPIADA,
                            severidade=Severidade.CRITICO,
                            descricao=f"ByteRange comprometido: {problema}",
                            detalhes={
                                "byte_range": br,
                                "cobertura_pct": verif.get("cobertura_pct"),
                                "tamanho_pdf": verif.get("tamanho_pdf"),
                            },
                        ))

    # Heurística: buscar indícios de assinatura no raw
    tem_sig_field = b"/Type /Sig" in pdf_bytes or b"/Type/Sig" in pdf_bytes
    tem_byterange = b"/ByteRange" in pdf_bytes
    tem_contents_hex = b"/Contents <" in pdf_bytes or b"/Contents<" in pdf_bytes

    total_sigs = len([a for a in achados if a.status != StatusAssinatura.ERRO_ANALISE])
    if total_sigs == 0 and tem_sig_field:
        achados.append(AchadoAssinatura(
            status=StatusAssinatura.CAMPO_SEM_ASSINATURA,
            severidade=Severidade.ALERTA,
            descricao="Estrutura de assinatura detectada no PDF mas não pôde ser parseada.",
            detalhes={"tem_sig_field": True, "tem_byterange": tem_byterange},
        ))
        total_sigs = 1

    has_any_sig = tem_sig_field or total_sigs > 0
    validas = len([a for a in achados if a.status == StatusAssinatura.VALIDA])
    invalidas = len([a for a in achados if a.status in (
        StatusAssinatura.INVALIDA, StatusAssinatura.CORROMPIDA,
        StatusAssinatura.COPIADA, StatusAssinatura.MODIFICADA_APOS,
        StatusAssinatura.CAMPO_SEM_ASSINATURA,
    )])

    risco = "alto" if invalidas > 0 else "baixo"

    return ResultadoAssinatura(
        tem_assinatura=has_any_sig,
        total_assinaturas=max(total_sigs, validas + invalidas),
        achados=achados,
        assinaturas_validas=validas,
        assinaturas_invalidas=invalidas,
        risco=risco,
        metricas={
            "tamanho_pdf": len(pdf_bytes),
            "pyhanko_disponivel": PYHANKO_DISPONIVEL,
            "pypdf_disponivel": PYPDF_DISPONIVEL,
            "tem_sig_field_raw": tem_sig_field,
            "tem_byterange_raw": tem_byterange,
        },
    )
