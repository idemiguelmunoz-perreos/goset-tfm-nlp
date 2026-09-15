"""Normaliza un perfil crudo (dueño+perro) a features que consumen las reglas."""

from __future__ import annotations

import datetime as dt
import re

HOY = dt.date(2026, 8, 23)

_BRAQUI = ("bulldog", "frances", "francés", "carlino", "pug", "shih tzu",
           "pekines", "pekinés", "boston", "boxer", "cavalier king")
_GRANDE = ("pastor aleman", "pastor alemán", "labrador", "golden", "san bernardo",
           "gran danes", "gran danés", "mastin", "mastín", "rottweiler", "dogo",
           "montaña", "boyero", "setter", "malamute")
_MESES = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
          "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11,
          "diciembre": 12}


def _b(x: str | None) -> bool | None:
    """Convierte 'Sí/No/Leve/A veces' a booleano (parcial=True)."""
    if x is None:
        return None
    s = str(x).strip().lower()
    if s in ("sí", "si", "leve", "a veces", "leve/a veces"):
        return True
    if s in ("no", "no aplica", "n/a", "n/a (no senior)", "sin signos", "ninguno"):
        return False
    return None


def _num(x: str | None) -> float | None:
    if x is None:
        return None
    m = re.search(r"\d+(?:[.,]\d+)?", str(x))
    return float(m.group().replace(",", ".")) if m else None


def _fecha(x: str | None) -> dt.date | None:
    """Parseo tolerante de fechas en formatos mixtos (o None)."""
    if x is None:
        return None
    s = str(x).strip().lower()
    if "no consta" in s:
        return None
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    for mes, n in _MESES.items():
        if mes in s:
            y = re.search(r"\d{4}", s)
            return dt.date(int(y.group()), n, 15) if y else None
    if re.fullmatch(r"\d{4}", s):
        return dt.date(int(s), 7, 1)
    return None


def normalize(p: dict) -> dict:
    """Devuelve el dict de features normalizadas para el motor de reglas."""
    g = p.get
    raza = (g("Raza o mezcla") or "").lower()
    manto_txt = ((g("Tipo de manto") or "") + " " + (g("Capa (color y tipo de pelo)") or "")).lower()
    edad = _num(g("Edad (años)"))
    peso = _num(g("Peso (kg)"))
    sexo = (g("Sexo") or "").strip().lower()
    castrado = _b(g("Castrado/esterilizado"))
    bcs = (g("BCS (estado corporal)") or "").lower()
    dieta = (g("Tipo de dieta") or "").lower()

    if "doble" in manto_txt:
        manto = "doble"
    elif any(k in manto_txt for k in ("rizad", "lanoso")):
        manto = "rizado"
    elif any(k in manto_txt for k in ("largo", "sedoso")):
        manto = "largo"
    elif "corto" in manto_txt or "liso" in manto_txt:
        manto = "corto"
    elif "medio" in manto_txt:
        manto = "medio"
    else:
        manto = None

    etapa = None
    if edad is not None:
        etapa = "cachorro" if edad < 1 else ("senior" if edad >= 8 else "adulto")

    desp = _fecha(g("Desparasitación (fecha)"))
    desp_vencida = None
    if desp is not None:
        desp_vencida = (HOY - desp).days > 92

    rabia_v = _fecha(g("Rabia (válida hasta)"))
    poli_v = _fecha(g("Polivalente (válida hasta)"))
    vals = [d for d in (rabia_v, poli_v) if d is not None]
    vacuna_no_vigente = None if not vals else any(d < HOY for d in vals)

    return {
        "raza": raza, "edad": edad, "peso": peso, "etapa": etapa,
        "hembra_entera": sexo == "hembra" and castrado is False,
        "manto": manto,
        "enreda": _b(g("¿Se enreda/apelmaza?")),
        "orejas_caidas": (g("Orejas") or "").strip().lower() == "caídas",
        "piel_problema": bool(g("Problemas de piel/dermatitis") and _b(g("Problemas de piel/dermatitis")) is not False)
                         and str(g("Problemas de piel/dermatitis")).strip().lower() not in ("", "no"),
        "miedo_agua": _b(g("Miedo al agua")),
        "actividad_alta": (g("Nivel de actividad") or "").strip().lower() == "alto",
        "reactivo_perros": (g("Con otros perros") or "").strip().lower() == "reactivo",
        "reactivo_personas": (g("Con personas") or "").strip().lower() == "reactivo",
        "ansiedad_sep": _b(g("Ansiedad por separación")),
        "miedo_ruido": _b(g("Miedo a ruidos/tormentas")),
        "guarda_recursos": _b(g("Protección de recursos/agresividad")),
        "educacion_baja": (g("Nivel de educación/obediencia") or "").strip().lower() in ("nada", "básica", "basica", "ninguna"),
        "bcs_sobrepeso": "sobrepeso" in bcs or "obes" in bcs,
        "bcs_delgado": "delgad" in bcs,
        "movilidad_reducida": _b(g("Movilidad/artrosis")) is True,
        "cognitivo": _b(g("Disfunción cognitiva (senior)")) is True,
        "dieta_no_equilibrada": "casera" in dieta or "barf" in dieta,
        "alergia": bool(g("Alergias / condiciones / medicación")),
        "braquicefalo": any(k in raza for k in _BRAQUI),
        "raza_grande_cachorro": (etapa == "cachorro") and (any(k in raza for k in _GRANDE) or (peso or 0) > 20),
        "desparasitacion_vencida": desp_vencida,
        "vacuna_no_vigente": vacuna_no_vigente,
    }
