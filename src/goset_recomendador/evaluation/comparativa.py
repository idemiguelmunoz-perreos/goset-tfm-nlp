"""Comparación cuantificada: baseline (solo reglas duras) vs híbrido.

Ablación del scoring blando: cuánto aporta la capa BLANDA frente a usar solo
las reglas duras (bloqueantes). No requiere ground truth de relevancia.
"""

from __future__ import annotations

import time

from goset_recomendador.engine import recomendar


def _stats(perfiles: list[dict], *, solo_duras: bool) -> dict:
    n = len(perfiles)
    con_rec = n_serv = n_reglas = 0
    t0 = time.perf_counter()
    for p in perfiles:
        out = recomendar(p, solo_reglas_duras=solo_duras)
        if out["ranking"]:
            con_rec += 1
        n_serv += len(out["ranking"])
        n_reglas += sum(len(s["reglas_activadas"]) for s in out["ranking"])
    dur = time.perf_counter() - t0
    return {
        "perros_con_recomendacion_%": round(100 * con_rec / n, 1) if n else 0.0,
        "servicios_por_perro": round(n_serv / n, 2) if n else 0.0,
        "reglas_activadas_por_perro": round(n_reglas / n, 2) if n else 0.0,
        "latencia_media_ms": round(1000 * dur / n, 3) if n else 0.0,
    }


def comparar(perfiles: list[dict]) -> dict:
    """Devuelve las métricas de ambos modos, lado a lado."""
    return {
        "n": len(perfiles),
        "baseline_solo_duras": _stats(perfiles, solo_duras=True),
        "hibrido": _stats(perfiles, solo_duras=False),
    }
