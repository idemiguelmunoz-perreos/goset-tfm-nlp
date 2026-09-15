"""Capa 1 — Rule coverage accuracy.

Verifica que el motor active las reglas que DEBE activar en casos canónicos
construidos a mano (fidelidad de la implementación a la base de conocimiento).
No mide calidad de recomendación (eso es Capa 2, con expertas); mide que el
código encode correctamente las 50 reglas. Objetivo: >95%.
"""

from __future__ import annotations

from goset_recomendador.engine import recomendar

# (descripción, perfil, reglas que DEBEN dispararse)
CASOS: list[tuple[str, dict, list[str]]] = [
    ("hembra entera adulta", {"Sexo": "Hembra", "Castrado/esterilizado": "No", "Edad (años)": "4"}, ["GU-10"]),
    ("cachorro", {"Edad (años)": "0.5"}, ["EN-01", "SP-05", "AL-04"]),
    ("senior", {"Edad (años)": "10"}, ["SP-06", "SP-09", "GU-07", "AL-05", "HO-03"]),
    ("manto rizado", {"Tipo de manto": "rizado/lanoso", "Edad (años)": "3"}, ["PE-01", "PE-07"]),
    ("manto doble", {"Tipo de manto": "doble capa", "Edad (años)": "3"}, ["PE-02"]),
    ("manto largo + orejas caídas", {"Tipo de manto": "largo/sedoso", "Orejas": "caídas", "Edad (años)": "3"}, ["PE-03", "PE-05", "PE-07"]),
    ("sobrepeso", {"BCS (estado corporal)": "sobrepeso", "Edad (años)": "5"}, ["AL-01", "AL-07"]),
    ("delgado", {"BCS (estado corporal)": "delgado", "Edad (años)": "5"}, ["AL-02"]),
    ("braquicéfalo", {"Raza o mezcla": "Bulldog francés", "Edad (años)": "3"}, ["SP-08", "GU-06", "HO-04"]),
    ("braqui + sobrepeso", {"Raza o mezcla": "Carlino", "BCS (estado corporal)": "sobrepeso", "Edad (años)": "4"}, ["SP-08", "SP-12", "AL-01"]),
    ("reactivo con perros", {"Con otros perros": "Reactivo", "Edad (años)": "3"}, ["EN-04", "GU-08"]),
    ("ansiedad separación", {"Ansiedad por separación": "Sí", "Edad (años)": "3"}, ["EN-03", "GU-05", "HO-02"]),
    ("miedo a ruidos", {"Miedo a ruidos/tormentas": "Sí", "Edad (años)": "3"}, ["EN-06", "GU-09"]),
    ("agresión (safety)", {"Protección de recursos/agresividad": "Sí", "Edad (años)": "3"}, ["EN-07"]),
    ("miedo al agua", {"Miedo al agua": "Sí", "Edad (años)": "3"}, ["PE-08"]),
    ("dermatitis", {"Problemas de piel/dermatitis": "Dermatitis atópica", "Edad (años)": "3"}, ["PE-09"]),
    ("dieta casera", {"Tipo de dieta": "Casera", "Edad (años)": "3"}, ["AL-06"]),
    ("movilidad reducida", {"Movilidad/artrosis": "Sí", "Edad (años)": "6"}, ["SP-09", "SP-11", "GU-07", "HO-03"]),
    ("cognitivo senior", {"Disfunción cognitiva (senior)": "Sí", "Edad (años)": "11"}, ["SP-10"]),
    ("desparasitación vencida", {"Desparasitación (fecha)": "01/01/2025", "Edad (años)": "3"}, ["SP-04"]),
    ("cachorro raza grande", {"Edad (años)": "0.6", "Raza o mezcla": "Labrador", "Peso (kg)": "22"}, ["AL-03"]),
    ("educación nula", {"Nivel de educación/obediencia": "Nada", "Edad (años)": "3"}, ["EN-05"]),
    ("vacuna caducada", {"Rabia (válida hasta)": "01/01/2025", "Edad (años)": "3"}, ["SP-01", "HO-01"]),
]


def _reglas_disparadas(perfil: dict) -> set[str]:
    out = recomendar(perfil)
    fired = {r["id"] for s in out["ranking"] for r in s["reglas_activadas"]}
    fired |= {n["id"] for n in out["notas_operativas"]}
    return fired


def rule_coverage() -> dict:
    """Calcula la cobertura de reglas sobre los casos canónicos."""
    total_esperadas = aciertos = 0
    fallos: list[dict] = []
    for desc, perfil, esperadas in CASOS:
        fired = _reglas_disparadas(perfil)
        faltan = [r for r in esperadas if r not in fired]
        total_esperadas += len(esperadas)
        aciertos += len(esperadas) - len(faltan)
        if faltan:
            fallos.append({"caso": desc, "no_disparadas": faltan})
    return {
        "casos": len(CASOS),
        "reglas_esperadas": total_esperadas,
        "aciertos": aciertos,
        "coverage_accuracy": round(aciertos / total_esperadas, 4) if total_esperadas else 0.0,
        "fallos": fallos,
    }
