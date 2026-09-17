"""FastAPI del Componente B: recomendador híbrido con OpenAPI autogenerada."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from goset_recomendador.engine import recomendar

app = FastAPI(
    title="GOSET · Componente B — Recomendador híbrido",
    version="0.1.0",
    description="Recomienda servicios de cuidado canino, de forma explicable, "
    "a partir de un perfil (clínico + comportamiento). Apto para cold start.",
)


class RecomendarRequest(BaseModel):
    """Petición de recomendación."""

    perfil: dict[str, Any] = Field(
        ..., description="Perfil crudo del perro (features clínicas y de comportamiento)."
    )
    solo_reglas_duras: bool = Field(
        False, description="Si True, ejecuta el baseline de solo reglas duras."
    )


@app.get("/health")
def health() -> dict[str, str]:
    """Comprobación de vida."""
    return {"status": "ok"}


@app.post("/recomendar")
def recomendar_endpoint(req: RecomendarRequest) -> dict[str, Any]:
    """Devuelve el ranking de servicios explicable para el perfil dado."""
    return recomendar(req.perfil, solo_reglas_duras=req.solo_reglas_duras)
