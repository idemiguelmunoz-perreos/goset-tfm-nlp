"""Método propuesto: LLM con *structured outputs* nativos + validación Pydantic.

Usa el parseo estructurado del proveedor (function calling / JSON schema) para
forzar que la salida cumpla el esquema, y valida con Pydantic. Es la hipótesis
central del TFM: mayor exact-match y menor hallucination que los baselines.
"""

from __future__ import annotations

from goset_extraccion.config import Settings
from goset_extraccion.extractors.base import Extractor
from goset_extraccion.schemas import DogHealthRecord

_INSTRUCTION = (
    "Extrae la cartilla veterinaria al esquema. Campos ausentes = null. "
    "No inventes datos."
)


class StructuredOutputExtractor(Extractor):
    """Extractor propuesto con salida estructurada validada por Pydantic."""

    name = "structured_outputs"

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()

    def _extract(self, text: str) -> DogHealthRecord:
        if not self.settings.openai_api_key:
            raise RuntimeError("Falta OPENAI_API_KEY para el método propuesto.")
        from openai import OpenAI

        client = OpenAI(api_key=self.settings.openai_api_key)
        # API de parseo estructurado: valida contra el modelo Pydantic.
        completion = client.beta.chat.completions.parse(
            model=self.settings.llm_model,
            temperature=self.settings.llm_temperature,
            messages=[
                {"role": "system", "content": _INSTRUCTION},
                {"role": "user", "content": text},
            ],
            response_format=DogHealthRecord,
        )
        parsed = completion.choices[0].message.parsed
        return parsed or DogHealthRecord()
