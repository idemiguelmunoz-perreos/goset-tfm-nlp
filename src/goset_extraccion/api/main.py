"""FastAPI del Componente A: extracción estructurada con OpenAPI autogenerada."""

from __future__ import annotations

import datetime as dt
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from goset_extraccion.extractors.base import ExtractionResult
from goset_extraccion.extractors.llm_few_shot import LLMFewShotExtractor
from goset_extraccion.extractors.llm_zero_shot import LLMZeroShotExtractor
from goset_extraccion.extractors.regex_extractor import RegexExtractor
from goset_extraccion.extractors.structured_outputs import StructuredOutputExtractor
from goset_extraccion.schemas import DogHealthRecord
from goset_recomendador.engine import recomendar

app = FastAPI(
    title="GOSET · Componente A — Extracción NLP",
    version="0.1.0",
    description="Extrae cartillas veterinarias a JSON validado (Pydantic).",
)

_EXTRACTORS = {
    "regex": RegexExtractor,
    "llm_zero_shot": LLMZeroShotExtractor,
    "llm_few_shot": LLMFewShotExtractor,
    "structured_outputs": StructuredOutputExtractor,
}


class ExtractRequest(BaseModel):
    """Petición de extracción."""

    text: str
    method: str = "regex"


class ExtractResponse(BaseModel):
    """Respuesta con el registro extraído y la telemetría."""

    method: str
    latency_s: float
    cost_usd: float
    record: DogHealthRecord


@app.get("/health")
def health() -> dict[str, str]:
    """Comprobación de vida."""
    return {"status": "ok"}


@app.get("/methods")
def methods() -> list[str]:
    """Lista los métodos de extracción disponibles."""
    return list(_EXTRACTORS)


@app.post("/extract", response_model=ExtractResponse)
def extract(req: ExtractRequest) -> ExtractResponse:
    """Extrae un documento con el método indicado (por defecto, regex)."""
    extractor_cls = _EXTRACTORS.get(req.method, RegexExtractor)
    result: ExtractionResult = extractor_cls().run(req.text)
    return ExtractResponse(
        method=result.method,
        latency_s=result.latency_s,
        cost_usd=result.cost_usd,
        record=result.record,
    )


def _record_a_perfil(rec: DogHealthRecord) -> dict[str, Any]:
    """Traduce el registro clínico extraído a las claves del recomendador."""
    perfil: dict[str, Any] = {}
    if rec.raza:
        perfil["Raza o mezcla"] = rec.raza
    if rec.sexo:
        perfil["Sexo"] = rec.sexo.value
    if rec.peso_kg is not None:
        perfil["Peso (kg)"] = rec.peso_kg
    if rec.castrado is not None:
        perfil["Castrado/esterilizado"] = "Sí" if rec.castrado else "No"
    if rec.fecha_nacimiento:
        dias = (dt.date(2026, 8, 23) - rec.fecha_nacimiento).days
        perfil["Edad (años)"] = round(dias / 365.25, 1)
    return perfil


class EndToEndRequest(BaseModel):
    """Petición end-to-end: cartilla + contexto opcional de comportamiento."""

    text: str
    method: str = "regex"
    contexto: dict[str, Any] = {}


@app.post("/end-to-end")
def end_to_end(req: EndToEndRequest) -> dict[str, Any]:
    """Cartilla a extracción a recomendación, en una sola llamada.

    Extrae el perfil clínico del texto, lo combina con el contexto de
    comportamiento aportado y devuelve extracción y recomendación explicable.
    """
    result: ExtractionResult = _EXTRACTORS.get(req.method, RegexExtractor)().run(req.text)
    perfil = {**_record_a_perfil(result.record), **req.contexto}
    return {
        "extraccion": result.record.model_dump(mode="json"),
        "perfil_derivado": perfil,
        "recomendacion": recomendar(perfil),
    }
