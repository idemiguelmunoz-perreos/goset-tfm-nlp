"""Métricas de evaluación del Componente A.

Sobre campos escalares aplanados del :class:`DogHealthRecord`:
F1 por campo, exact-match por documento, hallucination rate y null-handling
accuracy. Latencia y coste se agregan desde los ``ExtractionResult``.
"""

from __future__ import annotations

from dataclasses import dataclass

from goset_extraccion.schemas import DogHealthRecord

_SCALAR_FIELDS = (
    "nombre", "especie", "raza", "sexo", "castrado",
    "fecha_nacimiento", "peso_kg", "microchip",
)


def flatten(record: DogHealthRecord) -> dict[str, str | None]:
    """Aplana los campos escalares a strings normalizados (o ``None``)."""
    data = record.model_dump()
    flat: dict[str, str | None] = {}
    for f in _SCALAR_FIELDS:
        v = data.get(f)
        flat[f] = None if v is None else str(v).strip().lower()
    return flat


@dataclass
class FieldScore:
    """Precisión/recall/F1 de un campo."""

    tp: int = 0
    fp: int = 0
    fn: int = 0

    @property
    def precision(self) -> float:
        return self.tp / (self.tp + self.fp) if (self.tp + self.fp) else 0.0

    @property
    def recall(self) -> float:
        return self.tp / (self.tp + self.fn) if (self.tp + self.fn) else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0


def evaluate(
    predictions: list[DogHealthRecord],
    gold: list[DogHealthRecord],
) -> dict[str, object]:
    """Calcula el cuadro de métricas para un conjunto de documentos.

    Args:
        predictions: Registros predichos por un extractor.
        gold: Registros de referencia (golden set anotado a mano).

    Returns:
        Diccionario con ``field_f1``, ``macro_f1``, ``exact_match_rate``,
        ``hallucination_rate`` y ``null_handling_accuracy``.
    """
    if len(predictions) != len(gold):
        raise ValueError("predictions y gold deben tener la misma longitud.")

    scores = {f: FieldScore() for f in _SCALAR_FIELDS}
    exact_hits = 0
    halluc_num = halluc_den = 0
    null_correct = null_total = 0

    for pred, ref in zip(predictions, gold):
        fp_, fr_ = flatten(pred), flatten(ref)
        if fp_ == fr_:
            exact_hits += 1
        for f in _SCALAR_FIELDS:
            p, g = fp_[f], fr_[f]
            if g is None:                      # campo ausente en la referencia
                null_total += 1
                if p is None:
                    null_correct += 1
                else:                          # inventado -> hallucination
                    halluc_num += 1
                    scores[f].fp += 1
            else:                              # campo presente en la referencia
                if p is None:
                    scores[f].fn += 1
                elif p == g:
                    scores[f].tp += 1
                else:
                    scores[f].fp += 1
                    scores[f].fn += 1
            if p is not None:
                halluc_den += 1

    field_f1 = {f: round(s.f1, 4) for f, s in scores.items()}
    macro_f1 = round(sum(field_f1.values()) / len(field_f1), 4)
    n = len(gold)
    return {
        "n_docs": n,
        "field_f1": field_f1,
        "macro_f1": macro_f1,
        "exact_match_rate": round(exact_hits / n, 4) if n else 0.0,
        "hallucination_rate": round(halluc_num / halluc_den, 4) if halluc_den else 0.0,
        "null_handling_accuracy": round(null_correct / null_total, 4) if null_total else 1.0,
    }
