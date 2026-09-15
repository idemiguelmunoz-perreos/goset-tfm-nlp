"""Evaluación del Componente B: Capa 1 + comparativa baseline/híbrido + errores.

Uso:
    PYTHONPATH=src python scripts/run_eval_recomendador.py
"""

from __future__ import annotations

import json
import pathlib
from collections import Counter

from goset_recomendador.engine import recomendar
from goset_recomendador.evaluation.comparativa import comparar
from goset_recomendador.evaluation.coverage import rule_coverage
from goset_recomendador.normalize import normalize

FIX = pathlib.Path("tests/fixtures/perfiles_sinteticos.json")
OUT = pathlib.Path("docs/evaluacion_componenteB.md")


def analisis_errores(perfiles: list[dict]) -> dict:
    """Modos de fallo por dato ausente/ambiguo (análisis cualitativo cuantificado)."""
    n = len(perfiles)
    sin_manto = sin_vacuna = sin_etapa = sin_bcs = 0
    for p in perfiles:
        f = normalize(p)
        sin_manto += f["manto"] is None
        sin_vacuna += f["vacuna_no_vigente"] is None
        sin_etapa += f["etapa"] is None
        sin_bcs += not (f["bcs_sobrepeso"] or f["bcs_delgado"])
    return {
        "manto_no_determinado_%": round(100 * sin_manto / n, 1),
        "estado_vacunal_no_verificable_%": round(100 * sin_vacuna / n, 1),
        "etapa_desconocida_%": round(100 * sin_etapa / n, 1),
    }


def main() -> None:
    perfiles = json.loads(FIX.read_text("utf-8"))["perfiles"]
    cov = rule_coverage()
    comp = comparar(perfiles)
    err = analisis_errores(perfiles)
    top = Counter(recomendar(p)["servicio_top"] for p in perfiles)

    md = []
    md.append("# Evaluación — Componente B (recomendador)\n")
    md.append("> Ejecutada sobre fixtures sintéticas (desarrollo). Las métricas de "
              "ranking (precision@k, NDCG, MRR) y la validación clínica (Capa 2, "
              "kappa) requieren etiquetas de expertas sobre casos reales.\n")
    md.append("## Capa 1 — Rule coverage accuracy\n")
    md.append(f"- Casos canónicos: **{cov['casos']}** · reglas esperadas: **{cov['reglas_esperadas']}**")
    md.append(f"- **Coverage accuracy: {cov['coverage_accuracy']*100:.1f}%** (objetivo >95%)")
    md.append(f"- Fallos: {cov['fallos'] if cov['fallos'] else 'ninguno'}\n")
    md.append("## Comparativa baseline (solo reglas duras) vs híbrido\n")
    md.append("| Métrica | Baseline | Híbrido |")
    md.append("|---|---|---|")
    b, h = comp["baseline_solo_duras"], comp["hibrido"]
    for k in b:
        md.append(f"| {k} | {b[k]} | {h[k]} |")
    md.append("")
    md.append("## Servicio prioritario (top-1) — distribución\n")
    for s, c in top.most_common():
        md.append(f"- {s}: {c}")
    md.append("\n## Análisis de errores (modos de fallo por dato ausente)\n")
    for k, v in err.items():
        md.append(f"- {k}: {v}%")
    OUT.write_text("\n".join(md), "utf-8")

    print(f"Capa 1 coverage: {cov['coverage_accuracy']*100:.1f}%  (fallos: {len(cov['fallos'])})")
    print("Baseline vs híbrido:")
    print("  con_recomendación:", b["perros_con_recomendacion_%"], "vs", h["perros_con_recomendacion_%"], "%")
    print("  servicios/perro:", b["servicios_por_perro"], "vs", h["servicios_por_perro"])
    print("  reglas/perro:", b["reglas_activadas_por_perro"], "vs", h["reglas_activadas_por_perro"])
    print("  latencia_ms:", b["latencia_media_ms"], "vs", h["latencia_media_ms"])
    print("errores (dato ausente):", err)
    print("reporte ->", OUT)
    if cov["fallos"]:
        print("FALLOS COVERAGE:", cov["fallos"])


if __name__ == "__main__":
    main()
