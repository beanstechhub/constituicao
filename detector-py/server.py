"""
constituicao.tech — Microserviço de detecção v0.2.0
Três módulos:
  1. /v1/analisar/* — detecção de prompt injection (OWASP/NIST/MITRE)
  2. /v1/integridade/* — detecção de texto gerado por IA (estilometria local)
  3. /v1/assinatura/* — verificação de assinatura digital em PDF

Stateless. Comunica-se com a API Go via HTTP interno.
Não fica exposto na internet — apenas dentro da VPC.
"""
from __future__ import annotations
import io
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from detector.core import analisar
from detector.integridade import analisar_integridade
from detector.assinatura import verificar_assinatura
from detector.extracao import extrair

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("constituicao-detector")

MAX_BYTES = int(os.environ.get("CONSTITUICAO_MAX_BYTES", 50 * 1024 * 1024))
MAX_CHARS = int(os.environ.get("CONSTITUICAO_MAX_CHARS", 500_000))


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("constituicao.tech detector v0.2.0 — 3 módulos ativos")
    log.info("  módulo 1: prompt injection (OWASP/NIST/MITRE)")
    log.info("  módulo 2: integridade acadêmica (estilometria)")
    log.info("  módulo 3: assinatura digital (PDF)")
    yield


app = FastAPI(
    title="constituicao.tech detector",
    version="0.2.0",
    description="Integridade de documentos na era da IA generativa",
    lifespan=lifespan,
)


# ============================================================
# Modelos de request
# ============================================================

class AnalisarTextoRequest(BaseModel):
    texto: str = Field(..., max_length=500_000)


class IntegridadeTextoRequest(BaseModel):
    texto: str = Field(..., max_length=500_000)


# ============================================================
# Health
# ============================================================

@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "versao": "0.2.0",
        "modulos": ["prompt_injection", "integridade_academica", "assinatura_digital"],
    }


# ============================================================
# Módulo 1: Detecção de Prompt Injection
# ============================================================

@app.post("/v1/analisar/texto")
def endpoint_analisar_texto(req: AnalisarTextoRequest) -> JSONResponse:
    if len(req.texto) > MAX_CHARS:
        raise HTTPException(413, f"Texto excede {MAX_CHARS} caracteres")
    resultado = analisar(req.texto)
    if resultado.score_risco >= 30:
        log.info("detecção elevada: score=%.1f achados=%d chars=%d",
                 resultado.score_risco, len(resultado.achados), len(req.texto))
    return JSONResponse(resultado.to_dict())


@app.post("/v1/analisar/arquivo")
async def endpoint_analisar_arquivo(arquivo: UploadFile = File(...)) -> JSONResponse:
    if not arquivo.filename:
        raise HTTPException(400, "Arquivo sem nome")
    conteudo = await arquivo.read()
    if len(conteudo) > MAX_BYTES:
        raise HTTPException(413, f"Arquivo excede {MAX_BYTES} bytes")
    try:
        texto = extrair(arquivo.filename, io.BytesIO(conteudo))
    except ValueError as e:
        raise HTTPException(415, str(e))
    except Exception as e:
        log.exception("falha extração arquivo=%s", arquivo.filename)
        raise HTTPException(422, "Não foi possível extrair texto deste arquivo.")
    truncado = len(texto) > MAX_CHARS
    if truncado:
        texto = texto[:MAX_CHARS]
    resultado = analisar(texto)
    data = resultado.to_dict()
    if truncado:
        data["metricas"]["truncado"] = True
    headers = {"X-Analysis-Truncated": "true"} if truncado else {}
    return JSONResponse(data, headers=headers)


# ============================================================
# Módulo 2: Integridade Acadêmica (detecção de IA)
# ============================================================

@app.post("/v1/integridade/texto")
def endpoint_integridade_texto(req: IntegridadeTextoRequest) -> JSONResponse:
    if len(req.texto) > MAX_CHARS:
        raise HTTPException(413, f"Texto excede {MAX_CHARS} caracteres")
    resultado = analisar_integridade(req.texto)
    if resultado.score_ia >= 60:
        log.info("integridade alta: score=%.1f classificacao=%s palavras=%d",
                 resultado.score_ia, resultado.classificacao, len(req.texto.split()))
    return JSONResponse(resultado.to_dict())


@app.post("/v1/integridade/arquivo")
async def endpoint_integridade_arquivo(arquivo: UploadFile = File(...)) -> JSONResponse:
    if not arquivo.filename:
        raise HTTPException(400, "Arquivo sem nome")
    conteudo = await arquivo.read()
    if len(conteudo) > MAX_BYTES:
        raise HTTPException(413, f"Arquivo excede {MAX_BYTES} bytes")
    try:
        texto = extrair(arquivo.filename, io.BytesIO(conteudo))
    except ValueError as e:
        raise HTTPException(415, str(e))
    except Exception as e:
        log.warning("falha extração integridade: %s", e)
        raise HTTPException(422, "Não foi possível extrair texto deste arquivo.")
    truncado = len(texto) > MAX_CHARS
    if truncado:
        texto = texto[:MAX_CHARS]
    resultado = analisar_integridade(texto)
    data = resultado.to_dict()
    if truncado:
        data["metricas"]["truncado"] = True
    headers = {"X-Analysis-Truncated": "true"} if truncado else {}
    return JSONResponse(data, headers=headers)


# ============================================================
# Módulo 3: Verificação de Assinatura Digital
# ============================================================

@app.post("/v1/assinatura/verificar")
async def endpoint_verificar_assinatura(arquivo: UploadFile = File(...)) -> JSONResponse:
    if not arquivo.filename:
        raise HTTPException(400, "Arquivo sem nome")
    if not arquivo.filename.lower().endswith(".pdf"):
        raise HTTPException(415, "Verificação de assinatura disponível apenas para PDF.")
    conteudo = await arquivo.read()
    if len(conteudo) > MAX_BYTES:
        raise HTTPException(413, f"Arquivo excede {MAX_BYTES} bytes")
    resultado = verificar_assinatura(io.BytesIO(conteudo))
    return JSONResponse(resultado.to_dict())
