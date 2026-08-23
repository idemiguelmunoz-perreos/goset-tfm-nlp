"""Interfaz común a todos los extractores (propuesto y baselines)."""

from __future__ import annotations

import abc
import time
from dataclasses import dataclass, field

from goset_extraccion.schemas import DogHealthRecord


@dataclass
class ExtractionResult:
    """Resultado de una extracción, con telemetría para las métricas."""

    record: DogHealthRecord
    method: str
    latency_s: float
    cost_usd: float = 0.0
    tokens_in: int = 0
    tokens_out: int = 0
    meta: dict = field(default_factory=dict)


class Extractor(abc.ABC):
    """Contrato de un extractor de cartillas.

    Implementa ``_extract`` en las subclases; ``run`` añade la medición de
    latencia y homogeneiza la salida en un :class:`ExtractionResult`.
    """

    name: str = "base"

    @abc.abstractmethod
    def _extract(self, text: str) -> DogHealthRecord:
        """Extrae un :class:`DogHealthRecord` desde el texto del documento."""

    def run(self, text: str) -> ExtractionResult:
        """Ejecuta la extracción midiendo la latencia.

        Args:
            text: Texto plano del documento (OCR o transcripción).

        Returns:
            El resultado con el registro y la telemetría.
        """
        t0 = time.perf_counter()
        record = self._extract(text)
        latency = time.perf_counter() - t0
        return ExtractionResult(record=record, method=self.name, latency_s=latency)
