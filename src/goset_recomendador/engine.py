"""Motor del recomendador híbrido knowledge-based (Componente B).

Diseño en dos planos, para no confundir "qué servicio recomendar" con
"cómo prestarlo":

* Reglas DRIVER (BLANDA/DURA) -> puntúan y deciden el ranking de servicios.
* Reglas OPERATIVAS -> no puntúan; se adjuntan como notas de manejo/gate
  cuando el servicio ya está recomendado (p. ej. evaluación de temperamento
  o política de refuerzo positivo).

Salida explicable con el esquema de metadatos acordado (prioridad, ventana
temporal, zona/manejo, confianza agregada, needs_human_review con motivos,
trazabilidad de fuente).
"""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field

from goset_recomendador.normalize import normalize

_RULES_META = json.loads(
    (pathlib.Path(__file__).parent / "reglas_v3.json").read_text("utf-8")
)["reglas"]
_META_BY_ID = {r["id"]: r for r in _RULES_META}

# Reglas que NO puntúan: son gate/política/manejo operativo.
OPERATIVAS = {"GU-01", "GU-02", "GU-03", "EN-02"}

_CONF_RANK = {"[Certain]": 2, "[Likely]": 1, "[Guessing]": 0}
_RANK_CONF = {v: k for k, v in _CONF_RANK.items()}


def _T(v: object) -> bool:
    return v is True


PREDICATES = {
    # Salud preventiva
    "SP-01": lambda f: f["vacuna_no_vigente"] is True,
    "SP-04": lambda f: f["desparasitacion_vencida"] is True,
    "SP-05": lambda f: f["etapa"] == "cachorro",
    "SP-06": lambda f: f["etapa"] == "senior",
    "SP-08": lambda f: f["braquicefalo"],
    "SP-09": lambda f: f["etapa"] == "senior" or f["movilidad_reducida"],
    "SP-10": lambda f: f["cognitivo"],
    "SP-11": lambda f: f["movilidad_reducida"],
    "SP-12": lambda f: f["braquicefalo"] and f["bcs_sobrepeso"],
    # Peluquería
    "PE-01": lambda f: f["manto"] == "rizado",
    "PE-02": lambda f: f["manto"] == "doble",
    "PE-03": lambda f: f["manto"] == "largo",
    "PE-04": lambda f: _T(f["enreda"]),
    "PE-05": lambda f: f["orejas_caidas"],
    "PE-07": lambda f: f["manto"] in ("largo", "rizado"),
    "PE-08": lambda f: _T(f["miedo_agua"]),
    "PE-09": lambda f: f["piel_problema"],
    # Entrenamiento
    "EN-01": lambda f: f["etapa"] == "cachorro",
    "EN-03": lambda f: _T(f["ansiedad_sep"]),
    "EN-04": lambda f: f["reactivo_perros"],
    "EN-05": lambda f: f["educacion_baja"],
    "EN-06": lambda f: _T(f["miedo_ruido"]),
    "EN-07": lambda f: _T(f["guarda_recursos"]),
    # Guardería (solo drivers reales)
    "GU-04": lambda f: f["actividad_alta"] and f["etapa"] in ("cachorro", "adulto"),
    "GU-05": lambda f: _T(f["ansiedad_sep"]),
    "GU-06": lambda f: f["braquicefalo"],
    "GU-07": lambda f: f["etapa"] == "senior" or f["movilidad_reducida"],
    "GU-08": lambda f: f["reactivo_perros"] or f["reactivo_personas"],
    "GU-09": lambda f: _T(f["miedo_ruido"]),
    "GU-10": lambda f: f["hembra_entera"],
    # Alimentación
    "AL-01": lambda f: f["bcs_sobrepeso"],
    "AL-02": lambda f: f["bcs_delgado"],
    "AL-03": lambda f: f["raza_grande_cachorro"],
    "AL-04": lambda f: f["etapa"] == "cachorro",
    "AL-05": lambda f: f["etapa"] == "senior",
    "AL-06": lambda f: f["dieta_no_equilibrada"],
    "AL-07": lambda f: f["bcs_sobrepeso"],
    # Hotel
    "HO-01": lambda f: f["vacuna_no_vigente"] is True,
    "HO-02": lambda f: _T(f["ansiedad_sep"]),
    "HO-03": lambda f: f["etapa"] == "senior" or f["movilidad_reducida"],
    "HO-04": lambda f: f["braquicefalo"],
    # Reglas operativas (evaluadas aparte, no puntúan):
    "GU-01": lambda f: True,
    "GU-02": lambda f: True,
}

_PESO_PRIORIDAD = {
    "Alta (bloqueante)": 3.0, "Alta (bloqueante grupo)": 3.0, "Alta": 3.0,
    "Alta-temporal": 3.0, "Media-Alta": 2.5, "Media": 2.0, "Baja-Media": 1.5, "Baja": 1.0,
}


@dataclass
class ServicioRec:
    """Recomendación agregada para un servicio."""

    servicio: str
    score: float = 0.0
    prioridad_max: str = "Baja"
    conf_rank: int = 2
    reglas: list[dict] = field(default_factory=list)
    zona_manejo: list[str] = field(default_factory=list)
    frecuencias: list[str] = field(default_factory=list)
    ventana_temporal: bool = False


def recomendar(perfil: dict, *, solo_reglas_duras: bool = False) -> dict:
    """Genera el conjunto de recomendaciones explicable para un perfil.

    Args:
        perfil: Perfil crudo (campos del formulario + cartilla).
        solo_reglas_duras: Si True, ignora las reglas BLANDA (baseline de
            comparación: recomendador de solo reglas duras).

    Returns:
        Dict con ranking de servicios, banderas, notas operativas y trazabilidad.
    """
    f = normalize(perfil)
    servicios: dict[str, ServicioRec] = {}
    notas_operativas: list[dict] = []
    safety_critical = False
    bloqueo_grupo = False

    for pid, pred in PREDICATES.items():
        try:
            fired = bool(pred(f))
        except Exception:  # noqa: BLE001 - feature ausente => no dispara
            fired = False
        if not fired:
            continue
        meta = _META_BY_ID[pid]

        if pid in OPERATIVAS:
            notas_operativas.append({"id": pid, "nota": meta["recomendacion"], "fuente": meta["fuentes"]})
            continue
        if solo_reglas_duras and meta["tipo"] != "DURA":
            continue

        srv = meta["servicio"]
        rec = servicios.setdefault(srv, ServicioRec(servicio=srv))
        w = _PESO_PRIORIDAD.get(meta["prioridad"], 2.0)
        # Capa 3: peluquería incidental (oídos/agua/piel) pesa menos si el manto no es intensivo
        if pid in ("PE-05", "PE-08", "PE-09") and f["manto"] not in ("largo", "rizado", "doble"):
            w *= 0.4
        rec.score += w * (1.3 if meta["tipo"] == "DURA" else 1.0)
        if _PESO_PRIORIDAD.get(meta["prioridad"], 0) >= _PESO_PRIORIDAD.get(rec.prioridad_max, 0):
            rec.prioridad_max = meta["prioridad"]
        rec.conf_rank = min(rec.conf_rank, _CONF_RANK.get(meta["confianza"], 1))
        rec.reglas.append({"id": pid, "recomendacion": meta["recomendacion"],
                           "fuente": meta["fuentes"], "confianza": meta["confianza"]})
        if meta["zona_manejo"] and meta["zona_manejo"] not in rec.zona_manejo:
            rec.zona_manejo.append(meta["zona_manejo"])
        if meta["frecuencia"]:
            rec.frecuencias.append(f"{pid}: {meta['frecuencia']}")
        if "temporal" in meta["prioridad"]:
            rec.ventana_temporal = True
        if pid == "EN-07":
            safety_critical = bloqueo_grupo = True
        if pid in ("SP-01", "HO-01"):
            bloqueo_grupo = True

    # Capa 3 · ajustes derivados de la validación experta:
    # (a) ansiedad/reactividad no debe llevar la guardería a lo alto; antes, etología.
    if (f["reactivo_perros"] or f["reactivo_personas"] or f["ansiedad_sep"]) and "Guarderia" in servicios:
        servicios["Guarderia"].score *= 0.5
        notas_operativas.append({
            "id": "AJUSTE-CONDUCTA",
            "nota": "Ansiedad/reactividad: modificación de conducta (etología) antes de integrar en grupo.",
            "fuente": ["S7"]})
    # (b) en cachorro, la salud preventiva (vacunación) domina sobre la peluquería.
    if f["etapa"] == "cachorro" and "Salud preventiva" in servicios:
        servicios["Salud preventiva"].score *= 1.5

    # ranking con score normalizado y desempate determinista
    ordenados = sorted(
        servicios.values(),
        key=lambda r: (-r.score, -_PESO_PRIORIDAD.get(r.prioridad_max, 0), r.servicio),
    )
    max_score = ordenados[0].score if ordenados else 0.0

    # motivos de revisión humana (calibración explícita)
    motivos = []
    if safety_critical:
        motivos.append("agresión/protección de recursos declarada")
    if f["vacuna_no_vigente"] is None:
        motivos.append("estado vacunal no verificable en la cartilla")
    if f["etapa"] is None:
        motivos.append("edad/etapa vital desconocida")

    ranking = [
        {
            "servicio": r.servicio,
            "score": round(r.score, 2),
            "score_norm": round(r.score / max_score, 3) if max_score else 0.0,
            "prioridad": r.prioridad_max,
            "confianza": _RANK_CONF[r.conf_rank],
            "ventana_temporal": r.ventana_temporal,
            "zona_manejo": r.zona_manejo,
            "frecuencias": r.frecuencias,
            "reglas_activadas": r.reglas,
        }
        for r in ordenados
    ]
    return {
        "id": perfil.get("id"),
        "etapa": f["etapa"],
        "modo": "solo_reglas_duras" if solo_reglas_duras else "hibrido",
        "servicio_top": ranking[0]["servicio"] if ranking else None,
        "flags": {
            "safety_critical": safety_critical,
            "elegible_grupo": not bloqueo_grupo,
            "requiere_evaluacion_temperamento": True,
            "needs_human_review": bool(motivos),
            "motivos_revision": motivos,
        },
        "notas_operativas": notas_operativas,
        "ranking": ranking,
    }
