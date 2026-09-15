"""Tests del motor del recomendador (Componente B)."""

from goset_recomendador.engine import recomendar


def test_hembra_entera_dispara_celo():
    perfil = {"id": "t1", "Sexo": "Hembra", "Castrado/esterilizado": "No",
              "Edad (años)": "3", "Nivel de actividad": "medio"}
    out = recomendar(perfil)
    reglas = [r["id"] for s in out["ranking"] for r in s["reglas_activadas"]]
    assert "GU-10" in reglas


def test_agresion_bloquea_grupo():
    perfil = {"id": "t2", "Protección de recursos/agresividad": "Sí", "Edad (años)": "4"}
    out = recomendar(perfil)
    assert out["flags"]["safety_critical"] is True
    assert out["flags"]["elegible_grupo"] is False


def test_manto_rizado_recomienda_peluqueria():
    perfil = {"id": "t3", "Tipo de manto": "rizado/lanoso", "Edad (años)": "2"}
    out = recomendar(perfil)
    servicios = [r["servicio"] for r in out["ranking"]]
    assert "Peluqueria" in servicios


def test_senior_salud_y_hotel():
    perfil = {"id": "t4", "Edad (años)": "10"}
    out = recomendar(perfil)
    reglas = [r["id"] for s in out["ranking"] for r in s["reglas_activadas"]]
    assert "SP-06" in reglas and "SP-09" in reglas
