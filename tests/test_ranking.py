"""Tests de las métricas de ranking (Componente B)."""

from __future__ import annotations

import math

import pytest

from goset_recomendador.evaluation.ranking import (
    dcg_at_k,
    mrr,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
)

RANKING = ["A", "B", "C", "D"]
REL = {"A": 3.0, "C": 1.0}  # A y C relevantes; B y D no


def test_precision_at_k() -> None:
    assert precision_at_k(RANKING, REL, 1) == 1.0
    assert precision_at_k(RANKING, REL, 2) == 0.5  # A sí, B no
    assert precision_at_k(RANKING, REL, 4) == 0.5  # 2 de 4


def test_recall_at_k() -> None:
    assert recall_at_k(RANKING, REL, 1) == 0.5  # recupera A de {A, C}
    assert recall_at_k(RANKING, REL, 3) == 1.0  # recupera A y C


def test_recall_sin_relevantes_es_nan() -> None:
    assert math.isnan(recall_at_k(RANKING, {}, 3))


def test_mrr_primer_relevante_en_rank1() -> None:
    assert mrr(RANKING, REL) == 1.0


def test_mrr_primer_relevante_en_rank2() -> None:
    assert mrr(["X", "A"], REL) == 0.5


def test_mrr_sin_relevantes() -> None:
    assert mrr(["X", "Y"], REL) == 0.0


def test_ndcg_ranking_ideal_es_1() -> None:
    rel = {"A": 3.0, "B": 2.0, "C": 1.0}
    assert ndcg_at_k(["A", "B", "C"], rel, 3) == pytest.approx(1.0)


def test_ndcg_penaliza_orden_subooptimo() -> None:
    rel = {"A": 3.0, "B": 2.0, "C": 1.0}
    assert ndcg_at_k(["C", "B", "A"], rel, 3) < 1.0


def test_k_invalido() -> None:
    with pytest.raises(ValueError):
        precision_at_k(RANKING, REL, 0)
