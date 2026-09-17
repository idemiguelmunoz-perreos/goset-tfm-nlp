"""Métricas de ranking para el recomendador (Componente B).

Implementa precision@k, recall@k, NDCG@k y MRR sobre listas ordenadas de
servicios, dadas etiquetas de relevancia por ítem. Las funciones son genéricas y
deterministas; su interpretación en este TFM se discute en el informe de
evaluación, dado que la validación experta (Capa 2) produce un juicio holístico
de la recomendación principal y no una relevancia graduada por posición.

Convención: ``relevancia`` es un dict {servicio: rel} con rel >= 0 (0 = no
relevante). ``ranking`` es la lista ordenada de servicios (mejor primero).
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence


def precision_at_k(ranking: Sequence[str], relevancia: Mapping[str, float], k: int) -> float:
    """Fracción de los k primeros ítems que son relevantes (rel > 0)."""
    if k <= 0:
        raise ValueError("k debe ser >= 1")
    top = ranking[:k]
    if not top:
        return 0.0
    return sum(1 for s in top if relevancia.get(s, 0) > 0) / len(top)


def recall_at_k(ranking: Sequence[str], relevancia: Mapping[str, float], k: int) -> float:
    """Fracción de ítems relevantes totales recuperados en los k primeros."""
    total_rel = sum(1 for v in relevancia.values() if v > 0)
    if total_rel == 0:
        return float("nan")
    top = ranking[:k]
    return sum(1 for s in top if relevancia.get(s, 0) > 0) / total_rel


def dcg_at_k(ranking: Sequence[str], relevancia: Mapping[str, float], k: int) -> float:
    """Discounted Cumulative Gain con ganancia lineal y descuento log2."""
    return sum(
        relevancia.get(s, 0) / math.log2(i + 2)  # i+2: rank 1 -> log2(2)=1
        for i, s in enumerate(ranking[:k])
    )


def ndcg_at_k(ranking: Sequence[str], relevancia: Mapping[str, float], k: int) -> float:
    """NDCG@k: DCG del ranking normalizado por el DCG ideal."""
    ideal = sorted(relevancia.values(), reverse=True)
    idcg = sum(rel / math.log2(i + 2) for i, rel in enumerate(ideal[:k]) if rel > 0)
    if idcg == 0:
        return float("nan")
    return dcg_at_k(ranking, relevancia, k) / idcg


def mrr(ranking: Sequence[str], relevancia: Mapping[str, float]) -> float:
    """Mean Reciprocal Rank (para un solo ranking): 1/posición del 1er relevante."""
    for i, s in enumerate(ranking, start=1):
        if relevancia.get(s, 0) > 0:
            return 1.0 / i
    return 0.0
