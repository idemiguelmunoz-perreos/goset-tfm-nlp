"""Tests del esquema Pydantic."""

from goset_extraccion.schemas import DogHealthRecord, Sexo


def test_defaults_son_none_y_listas_vacias() -> None:
    rec = DogHealthRecord()
    assert rec.nombre is None
    assert rec.peso_kg is None
    assert rec.vacunas == []


def test_validacion_desde_json() -> None:
    rec = DogHealthRecord.model_validate_json('{"nombre":"Luna","sexo":"hembra","peso_kg":8.5}')
    assert rec.nombre == "Luna"
    assert rec.sexo is Sexo.HEMBRA
    assert rec.peso_kg == 8.5
