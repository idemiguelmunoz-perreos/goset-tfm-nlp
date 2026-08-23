"""Registro de condicionados públicos de pólizas de seguro de mascotas (ES).

Aseguradoras identificadas en el resumen del TFM. Las URLs directas a cada
condicionado PDF debe rellenarlas el usuario desde la web oficial de cada
aseguradora (no se inventan aquí).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FuentePoliza:
    """Una fuente de condicionado de póliza."""

    aseguradora: str
    producto: str
    url_pdf: str | None = None  # rellenar con el enlace oficial


ASEGURADORAS: list[FuentePoliza] = [
    FuentePoliza("Mapfre", "Mapfre Mascotas"),
    FuentePoliza("Santa Lucía", "Santa Lucía Mascotas"),
    FuentePoliza("Caser", "Caser Mascotas"),
    FuentePoliza("SegurCaixa", "SegurCaixa Adeslas Mascotas"),
    FuentePoliza("Fiatc", "Fiatc Mascotas"),
]
