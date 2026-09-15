"""Calcula el acuerdo inter-evaluador (Capa 2) desde el Excel relleno.

Kappa ponderado cuadrático (apropiado para Likert ordinal 1-4) por cada par de
evaluadoras, más la media de puntuación de cada una.

Uso:
    PYTHONPATH=src python scripts/calcular_kappa_capa2.py docs/kit_evaluacion_capa2.xlsx
"""

from __future__ import annotations

import sys
from itertools import combinations

from openpyxl import load_workbook

RATERS = {"Vet": 4, "Peluquera": 5, "Isabela": 6}  # columnas (1-indexadas)


def kappa_ponderado(pares: list[tuple[int, int]], k: int = 4) -> float:
    """Cohen's kappa con pesos cuadráticos para escalas ordinales."""
    n = len(pares)
    if n == 0:
        return float("nan")
    cats = list(range(1, k + 1))
    obs = {(i, j): 0 for i in cats for j in cats}
    for a, b in pares:
        obs[(a, b)] += 1
    ma = {c: sum(1 for a, _ in pares if a == c) / n for c in cats}
    mb = {c: sum(1 for _, b in pares if b == c) / n for c in cats}

    def w(i: int, j: int) -> float:
        return (i - j) ** 2 / (k - 1) ** 2

    num = sum(w(i, j) * obs[(i, j)] / n for i in cats for j in cats)
    den = sum(w(i, j) * ma[i] * mb[j] for i in cats for j in cats)
    return 1.0 if den == 0 else 1 - num / den


def main(path: str) -> None:
    ws = load_workbook(path)["Evaluacion"]
    filas = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or str(row[0]).strip().upper() == "EJEMPLO":
            continue
        filas.append(row)

    puntuaciones = {r: [] for r in RATERS}
    for row in filas:
        for r, col in RATERS.items():
            v = row[col - 1]
            puntuaciones[r].append(int(v) if isinstance(v, (int, float)) and v else None)

    print(f"Ítems evaluados: {len(filas)}\n")
    for r in RATERS:
        vals = [v for v in puntuaciones[r] if v is not None]
        media = sum(vals) / len(vals) if vals else float("nan")
        print(f"  {r}: n={len(vals)}  media Likert={media:.2f}")
    print("\nKappa ponderado (acuerdo entre pares):")
    algun = False
    for a, b in combinations(RATERS, 2):
        pares = [(x, y) for x, y in zip(puntuaciones[a], puntuaciones[b]) if x and y]
        if pares:
            algun = True
            print(f"  {a} vs {b}: kappa_w = {kappa_ponderado(pares):.3f}  (n={len(pares)})")
    if not algun:
        print("  (aún sin celdas rellenas: complétalas y vuelve a ejecutar)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "docs/kit_evaluacion_capa2.xlsx")
