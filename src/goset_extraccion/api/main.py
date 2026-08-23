"""FastAPI del Componente A: extracción estructurada con OpenAPI autogenerada."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from goset_extraccion.extractors.base import ExtractionResult
from goset_extraccion.extractors.llm_few_shot import LLMFewShotExtractor
from goset_extraccion.extractors.llm_zero_shot import LLMZeroShotExtractor
from goset_extraccion.extractors.regex_extractor import RegexExtractor
from goset_extraccion.extractors.structured_outputs import StructuredOutputExtractor
from goset_extraccion.schemas import DogHealthRecord

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
