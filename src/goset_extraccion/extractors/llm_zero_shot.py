"""Baseline 2: LLM zero-shot (prompt + schema, sin ejemplos)."""

from __future__ import annotations

from goset_extraccion.config import Settings
from goset_extraccion.extractors.base import Extractor
from goset_extraccion.schemas import DogHealthRecord

_PROMPT = (
    "Extrae la información de esta cartilla veterinaria en JSON. "
    "Devuelve null en los campos que no aparezcan; no inventes datos.\n\n{text}"
)


class LLMZeroShotExtractor(Extractor):
    """Extracción zero-shot con un LLM comercial.

    Requiere ``OPENAI_API_KEY``. Sin clave, ``_extract`` lanza ``RuntimeError``;
    el pipeline puede seguir usando el baseline regex.
    """

    name = "llm_zero_shot"

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()

    def _extract(self, text: str) -> DogHealthRecord:
        if not self.settings.openai_api_key:
            raise RuntimeError("Falta OPENAI_API_KEY para el baseline LLM zero-shot.")
        from openai import OpenAI  # import perezoso

        client = OpenAI(api_key=self.settings.openai_api_key)
        resp = client.chat.completions.create(
            model=self.settings.llm_model,
            temperature=self.settings.llm_temperature,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": _PROMPT.format(text=text)}],
        )
        content = resp.choices[0].message.content
        try:
            return DogHealthRecord.model_validate_json(content)
        except Exception:  # respuesta no parseable: registro vacío, no cancela el lote
            return DogHealthRecord()
