"""Tests de las métricas."""

from goset_extraccion.evaluation.metrics import evaluate
from goset_extraccion.schemas import DogHealthRecord


def test_exact_match_perfecto() -> None:
    gold = [DogHealthRecord(nombre="Luna", peso_kg=8.5)]
    pred = [DogHealthRecord(nombre="Luna", peso_kg=8.5)]
    m = evaluate(pred, gold)
    assert m["exact_match_rate"] == 1.0
    assert m["hallucination_rate"] == 0.0
    assert m["null_handling_accuracy"] == 1.0


def test_detecta_hallucination() -> None:
    gold = [DogHealthRecord(nombre="Luna")]                       # microchip None
    pred = [DogHealthRecord(nombre="Luna", microchip="999")]      # inventado
    m = evaluate(pred, gold)
    assert m["hallucination_rate"] > 0.0
    assert m["null_handling_accuracy"] < 1.0
