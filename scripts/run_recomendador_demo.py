"""Ejecuta el recomendador sobre las fixtures sintéticas y guarda las salidas.

Uso:
    PYTHONPATH=src python scripts/run_recomendador_demo.py
"""

from __future__ import annotations

import json
import pathlib

from goset_recomendador.engine import recomendar

FIX = pathlib.Path("tests/fixtures/perfiles_sinteticos.json")
OUT = pathlib.Path("tests/fixtures/recomendaciones_demo.json")


def main() -> None:
    data = json.loads(FIX.read_text("utf-8"))
    perfiles = data["perfiles"]
    salidas = [recomendar(p) for p in perfiles]
    OUT.write_text(json.dumps(
        {"_ADVERTENCIA": data.get("_ADVERTENCIA", "datos sinteticos - demo"),
         "n": len(salidas), "recomendaciones": salidas},
        ensure_ascii=False, indent=2), "utf-8")

    # cobertura: reglas que se activan al menos una vez
    from collections import Counter
    servicios = Counter()
    for s in salidas:
        for r in s["ranking"]:
            servicios[r["servicio"]] += 1
    print(f"Perfiles procesados: {len(salidas)}")
    print("Veces que cada servicio aparece en un ranking:")
    for srv, n in servicios.most_common():
        print(f"  {srv:<18} {n}")
    print(f"needs_human_review: {sum(1 for s in salidas if s['flags']['needs_human_review'])}")
    print(f"no elegibles a grupo: {sum(1 for s in salidas if not s['flags']['elegible_grupo'])}")
    print(f"\nSalidas -> {OUT}")


if __name__ == "__main__":
    main()
