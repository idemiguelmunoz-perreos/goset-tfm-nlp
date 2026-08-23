"""Configuración y determinismo (seed fija) para reproducibilidad."""

from __future__ import annotations

import os
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Ajustes globales del pipeline."""

    seed: int = int(os.getenv("GOSET_SEED", "42"))
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY") or None
    llm_model: str = os.getenv("GOSET_LLM_MODEL", "gpt-4o-mini")
    llm_temperature: float = 0.0  # determinismo


def set_seeds(seed: int | None = None) -> int:
    """Fija las seeds para reproducibilidad.

    Args:
        seed: Semilla a usar; si es ``None`` usa la de ``Settings``.

    Returns:
        La semilla aplicada.
    """
    settings = Settings()
    s = settings.seed if seed is None else seed
    random.seed(s)
    os.environ["PYTHONHASHSEED"] = str(s)
    return s
