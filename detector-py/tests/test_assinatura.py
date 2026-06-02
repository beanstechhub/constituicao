"""
Testes do módulo de verificação de assinatura digital.
Testa detecção de assinatura copiada, corrompida e ausente.
"""
import io
import pytest
from detector.assinatura import (
    verificar_assinatura,
    _verificar_byterange_basico,
    StatusAssinatura,
)


# ============================================================
# Testes de ByteRange
# ============================================================

def test_byterange_valido():
    """ByteRange que cobre todo o documento."""
    pdf_bytes = b'x' * 10000
    # ByteRange [0, 4000, 5000, 5000] -> cobre 0-4000 + 5000-10000 = 9000 bytes
    resultado = _verificar_byterange_basico(pdf_bytes, [0, 4000, 5000, 5000])
    assert resultado["valido"] is True


def test_byterange_nao_cobre_final():
    """ByteRange que deixa muitos bytes descobertos — possível cópia."""
    pdf_bytes = b'x' * 10000
    # ByteRange cobre até 3000, mas PDF tem 10000 bytes
    resultado = _verificar_byterange_basico(pdf_bytes, [0, 1000, 1500, 1500])
    assert resultado["valido"] is False
    assert any("não cobre" in p or "descobertos" in p for p in resultado["problemas"])


def test_byterange_nao_comeca_em_zero():
    """ByteRange que não começa em offset 0 — inválido."""
    pdf_bytes = b'x' * 5000
    resultado = _verificar_byterange_basico(pdf_bytes, [100, 2000, 2500, 2500])
    assert resultado["valido"] is False
    assert any("não começa em 0" in p for p in resultado["problemas"])


def test_byterange_sobreposicao():
    """ByteRange com sobreposição — corrompido."""
    pdf_bytes = b'x' * 5000
    resultado = _verificar_byterange_basico(pdf_bytes, [0, 3000, 2000, 3000])
    assert resultado["valido"] is False


def test_byterange_tamanho_errado():
    """ByteRange com número errado de elementos."""
    pdf_bytes = b'x' * 5000
    resultado = _verificar_byterange_basico(pdf_bytes, [0, 1000, 2000])
    assert resultado["valido"] is False


# ============================================================
# Testes de verificação de PDF
# ============================================================

def test_arquivo_nao_pdf():
    """Arquivo que não é PDF."""
    stream = io.BytesIO(b"Este nao e um PDF")
    resultado = verificar_assinatura(stream)
    assert resultado.tem_assinatura is False
    assert any(a.status == StatusAssinatura.ERRO_ANALISE for a in resultado.achados)


def test_pdf_sem_assinatura():
    """PDF mínimo válido sem campos de assinatura."""
    # PDF minimal sem sig fields
    pdf_minimo = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj
xref
0 4
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
trailer<</Size 4/Root 1 0 R>>
startxref
190
%%EOF"""
    stream = io.BytesIO(pdf_minimo)
    resultado = verificar_assinatura(stream)
    assert resultado.tem_assinatura is False
    assert resultado.risco == "baixo"


def test_pdf_com_sig_field_vazio():
    """PDF que tem /Type /Sig mas sem conteúdo real — campo cosmético."""
    # PDF com menção a Sig type no raw
    pdf_com_sig = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R/AcroForm<</Fields[3 0 R]>>>>endobj
2 0 obj<</Type/Pages/Kids[4 0 R]/Count 1>>endobj
3 0 obj<</FT/Sig/T(Signature1)/Type /Sig>>endobj
4 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000080 00000 n
0000000130 00000 n
0000000190 00000 n
trailer<</Size 5/Root 1 0 R>>
startxref
260
%%EOF"""
    stream = io.BytesIO(pdf_com_sig)
    resultado = verificar_assinatura(stream)
    assert resultado.tem_assinatura is True


def test_resultado_serializa():
    """Resultado serializa para dict sem erro."""
    stream = io.BytesIO(b"%PDF-1.4\ntest content\n%%EOF")
    resultado = verificar_assinatura(stream)
    d = resultado.to_dict()
    assert "tem_assinatura" in d
    assert "achados" in d
    assert "versao" in d


def test_cobertura_pct_calculada():
    """Cobertura percentual é calculada corretamente."""
    pdf_bytes = b'x' * 10000
    resultado = _verificar_byterange_basico(pdf_bytes, [0, 4000, 5000, 5000])
    assert resultado["cobertura_pct"] == 90.0
