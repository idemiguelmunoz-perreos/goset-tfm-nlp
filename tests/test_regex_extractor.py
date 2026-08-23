"""Tests del baseline regex."""

from goset_extraccion.extractors.regex_extractor import RegexExtractor
from goset_extraccion.schemas import Sexo


def test_extrae_campos_basicos() -> None:
    texto = (
        "Nombre: Luna\nRaza: Caniche\nSexo: hembra\n"
        "Microchip: 941000012345678\nPeso: 8,5 kg\n"
        "Vacuna polivalente 12/03/2026\n"
    )
    res = RegexExtractor().run(texto)
    rec = res.record
    assert rec.nombre == "Luna"
    assert rec.microchip == "941000012345678"
    assert rec.peso_kg == 8.5
    assert rec.sexo is Sexo.HEMBRA
    assert len(rec.vacunas) == 1
    assert res.latency_s >= 0


def test_campo_ausente_es_none() -> None:
    res = RegexExtractor().run("Documento sin datos estructurados.")
    assert res.record.microchip is None
    assert res.record.peso_kg is None
