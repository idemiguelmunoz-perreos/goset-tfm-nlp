"""Baseline 1: extracción con regex y reglas heurísticas.

Baseline mínimo, sin dependencias externas: sirve como suelo comparativo y
permite que el pipeline corra end-to-end sin claves de API.
"""

from __future__ import annotations

import re
from datetime import date

from goset_extraccion.extractors.base import Extractor
from goset_extraccion.schemas import DogHealthRecord, Sexo, Vacuna

_MICROCHIP = re.compile(r"\b(\d{15})\b")
_PESO = re.compile(r"(\d{1,2}(?:[.,]\d{1,2})?)\s?kg", re.IGNORECASE)
_FECHA = re.compile(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b")
_RAZA = re.compile(r"raza[:\s]+([A-Za-zÁÉÍÓÚÑáéíóúñ ]{2,30})", re.IGNORECASE)
_NOMBRE = re.compile(r"nombre[:\s]+([A-Za-zÁÉÍÓÚÑáéíóúñ ]{2,30})", re.IGNORECASE)


def _parse_fecha(m: re.Match) -> date | None:
    """Convierte una coincidencia dd/mm/aaaa en ``date`` (o ``None``)."""
    try:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if y < 100:
            y += 2000
        return date(y, mo, d)
    except (ValueError, TypeError):
        return None


class RegexExtractor(Extractor):
    """Extractor por reglas para campos de alta regularidad."""

    name = "regex"

    def _extract(self, text: str) -> DogHealthRecord:
        rec = DogHealthRecord()

        if m := _NOMBRE.search(text):
            rec.nombre = m.group(1).strip()
        if m := _RAZA.search(text):
            rec.raza = m.group(1).strip()
        if m := _MICROCHIP.search(text):
            rec.microchip = m.group(1)
        if m := _PESO.search(text):
            rec.peso_kg = float(m.group(1).replace(",", "."))

        low = text.lower()
        if "hembra" in low:
            rec.sexo = Sexo.HEMBRA
        elif "macho" in low:
            rec.sexo = Sexo.MACHO
        if "castrado" in low or "esterilizad" in low:
            rec.castrado = True

        # Vacunas: líneas que mencionan 'vacuna' con una fecha próxima.
        for linea in text.splitlines():
            if "vacun" in linea.lower():
                fecha = None
                if fm := _FECHA.search(linea):
                    fecha = _parse_fecha(fm)
                rec.vacunas.append(Vacuna(nombre=linea.strip()[:40], fecha=fecha))
        return rec


if __name__ == "__main__":  # smoke test end-to-end sin dependencias
    demo = (
        "Nombre: Luna\nRaza: Caniche\nSexo: hembra\n"
        "Microchip: 941000012345678\nPeso: 8,5 kg\n"
        "Vacuna polivalente 12/03/2026\n"
    )
    result = RegexExtractor().run(demo)
    print(result.record.model_dump_json(indent=2, exclude_none=True))
    print(f"latencia={result.latency_s*1000:.1f} ms")
