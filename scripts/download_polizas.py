"""Descarga los condicionados públicos de pólizas listados en data_sources.

Uso:
    PYTHONPATH=src python scripts/download_polizas.py

Rellena antes las URLs oficiales en ``goset_extraccion/data_sources/polizas.py``.
Guarda los PDF en ``data/raw/polizas/`` (no versionado).
"""

from __future__ import annotations

import pathlib
import urllib.request

from goset_extraccion.data_sources.polizas import ASEGURADORAS

DEST = pathlib.Path("data/raw/polizas")


def main() -> None:
    """Descarga cada póliza con URL definida."""
    DEST.mkdir(parents=True, exist_ok=True)
    for fuente in ASEGURADORAS:
        if not fuente.url_pdf:
            print(f"[SKIP] {fuente.aseguradora}: falta url_pdf")
            continue
        destino = DEST / f"{fuente.aseguradora.lower()}.pdf"
        print(f"[GET ] {fuente.aseguradora} -> {destino}")
        urllib.request.urlretrieve(fuente.url_pdf, destino)


if __name__ == "__main__":
    main()
