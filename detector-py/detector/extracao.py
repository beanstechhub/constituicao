"""Extração de texto de PDF, DOCX, TXT e imagens (OCR opcional)."""
from __future__ import annotations
from pathlib import Path
from typing import IO


def extrair_pdf(stream: IO[bytes]) -> str:
    import pypdf
    reader = pypdf.PdfReader(stream)
    partes = [(page.extract_text() or "") for page in reader.pages]
    return "\n".join(partes)


def extrair_docx(stream: IO[bytes]) -> str:
    from docx import Document
    doc = Document(stream)
    partes: list[str] = []
    for p in doc.paragraphs:
        partes.append(p.text)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    partes.append(cell.text)
    # cabeçalhos e rodapés são vetor comum de injection oculto
    for section in doc.sections:
        for p in section.header.paragraphs:
            if p.text.strip():
                partes.append(p.text)
        for p in section.footer.paragraphs:
            if p.text.strip():
                partes.append(p.text)
    return "\n".join(partes)


def extrair(filename: str, stream: IO[bytes]) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return extrair_pdf(stream)
    if ext == ".docx":
        return extrair_docx(stream)
    if ext == ".txt":
        return stream.read().decode("utf-8", errors="replace")
    raise ValueError(f"Formato não suportado: {ext}")
