"""Baseline 3: LLM few-shot (prompt + 3-5 ejemplos anotados)."""

from __future__ import annotations

from goset_extraccion.config import Settings
from goset_extraccion.extractors.base import Extractor
from goset_extraccion.schemas import DogHealthRecord

# TODO: cargar ejemplos anotados reales desde data/golden al fijar el golden set.
_FEWSHOT_EXAMPLES: list[dict[str, str]] = []

_SYSTEM = (
    "Eres un extractor de cartillas veterinarias. Devuelve JSON válido; "
    "usa null en campos ausentes y nunca inventes valores."
)


class LLMFewShotExtractor(Extractor):
    """Extracción few-shot con ejemplos en el prompt."""

    name = "llm_few_shot"

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()

    def _extract(self, text: str) -> DogHealthRecord:
        if not self.settings.openai_api_key:
            raise RuntimeError("Falta OPENAI_API_KEY para el baseline LLM few-shot.")
        from openai import OpenAI

        client = OpenAI(api_key=self.settings.openai_api_key)
        messages: list[dict[str, str]] = [{"role": "system", "content": _SYSTEM}]
        for ex in _FEWSHOT_EXAMPLES:
            messages.append({"role": "user", "content": ex["input"]})
            messages.append({"role": "assistant", "content": ex["output"]})
        messages.append({"role": "user", "content": text})
        resp = client.chat.completions.create(
            model=self.settings.llm_model,
            temperature=self.settings.llm_temperature,
            response_format={"type": "json_object"},
            messages=messages,
        )
        return DogHealthRecord.model_validate_json(resp.choices[0].message.content)
