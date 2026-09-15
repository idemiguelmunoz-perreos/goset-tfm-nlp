"""FastAPI de GOSET — extracción (A), recomendación (B) y end-to-end.

Expone OpenAPI automática en /docs. El Componente A por defecto usa el baseline
regex (corre sin API key); los métodos LLM se activan si hay OPENAI_API_KEY.
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

from goset_extraccion.extractors.regex_extractor import RegexExtractor
from goset_extraccion.schemas import DogHealthRecord
from goset_recomendador.engine import recomendar

app = FastAPI(
    title="GOSET · TFM · API",
    version="0.1.0",
    description="Extracción NLP (Componente A) + recomendador knowledge-based "
                "(Componente B) + pipeline end-to-end.",
)


class PerfilInput(BaseModel):
    """Perfil de entrada del recomendador (campos del formulario + cartilla).

    Acepta campos extra; se documentan aquí los drivers principales.
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    raza: str | None = Field(None, alias="Raza o mezcla")
    sexo: str | None = Field(None, alias="Sexo")
    castrado: str | None = Field(None, alias="Castrado/esterilizado")
    edad: str | None = Field(None, alias="Edad (años)")
    peso: str | None = Field(None, alias="Peso (kg)")
    manto: str | None = Field(None, alias="Tipo de manto")
    orejas: str | None = Field(None, alias="Orejas")
    enreda: str | None = Field(None, alias="¿Se enreda/apelmaza?")
    piel: str | None = Field(None, alias="Problemas de piel/dermatitis")
    miedo_agua: str | None = Field(None, alias="Miedo al agua")
    actividad: str | None = Field(None, alias="Nivel de actividad")
    con_perros: str | None = Field(None, alias="Con otros perros")
    con_personas: str | None = Field(None, alias="Con personas")
    ansiedad_sep: str | None = Field(None, alias="Ansiedad por separación")
    miedo_ruido: str | None = Field(None, alias="Miedo a ruidos/tormentas")
    guarda_recursos: str | None = Field(None, alias="Protección de recursos/agresividad")
    educacion: str | None = Field(None, alias="Nivel de educación/obediencia")
    bcs: str | None = Field(None, alias="BCS (estado corporal)")
    movilidad: str | None = Field(None, alias="Movilidad/artrosis")
    cognitivo: str | None = Field(None, alias="Disfunción cognitiva (senior)")
    dieta: str | None = Field(None, alias="Tipo de dieta")
    rabia_valida: str | None = Field(None, alias="Rabia (válida hasta)")
    desparasitacion_fecha: str | None = Field(None, alias="Desparasitación (fecha)")

    def to_profile(self) -> dict:
        """Convierte a dict con las claves que consume el motor."""
        return self.model_dump(by_alias=True, exclude_none=True)


class ExtractRequest(BaseModel):
    """Texto de una cartilla para extraer."""

    text: str


class EndToEndRequest(BaseModel):
    """Cartilla (texto) + contexto del formulario, para el pipeline completo."""

    cartilla_text: str
    formulario: PerfilInput


def _record_to_profile(rec: DogHealthRecord) -> dict:
    """Mapea el registro extraído a las claves del perfil del recomendador."""
    prof: dict = {}
    if rec.raza:
        prof["Raza o mezcla"] = rec.raza
    if rec.sexo:
        prof["Sexo"] = rec.sexo.value
    if rec.castrado is not None:
        prof["Castrado/esterilizado"] = "Sí" if rec.castrado else "No"
    if rec.peso_kg is not None:
        prof["Peso (kg)"] = str(rec.peso_kg)
    return prof


@app.get("/salud", tags=["infra"])
def salud() -> dict[str, str]:
    """Comprobación de vida."""
    return {"status": "ok"}


@app.post("/componente-a/extract", tags=["Componente A · extracción"])
def extract(req: ExtractRequest) -> dict:
    """Extrae una cartilla (baseline regex) a JSON estructurado."""
    res = RegexExtractor().run(req.text)
    return {"method": res.method, "latency_s": res.latency_s,
            "record": res.record.model_dump(exclude_none=True)}


@app.post("/componente-b/recomendar", tags=["Componente B · recomendador"])
def recomendar_endpoint(perfil: PerfilInput) -> dict:
    """Devuelve el ranking de servicios explicable para un perfil."""
    return recomendar(perfil.to_profile())


@app.post("/end-to-end", tags=["Pipeline end-to-end"])
def end_to_end(req: EndToEndRequest) -> dict:
    """Cartilla (texto) → extracción (A) → perfil → recomendación (B)."""
    res = RegexExtractor().run(req.cartilla_text)
    perfil = req.formulario.to_profile()
    perfil.update(_record_to_profile(res.record))
    return {
        "extraccion": res.record.model_dump(exclude_none=True),
        "recomendacion": recomendar(perfil),
    }
