"""Esquemas Pydantic: objetivo de extracción del Componente A.

Todos los campos son opcionales (``None`` por defecto) para poder medir
*null-handling accuracy*: el modelo debe devolver ``None`` cuando el dato no
aparece en el documento, en vez de inventarlo (hallucination).

Los campos de la cartilla alimentan las features del Componente B (recomendador).
"""

from __future__ import annotations

import datetime as _dt
import re
from datetime import date
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field


def _parse_fecha(v: object) -> object:
    """Acepta fechas en varios formatos (ISO, dd/mm/aaaa) y devuelve date o None."""
    if v is None or isinstance(v, _dt.date):
        return v
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return None
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y"):
            try:
                return _dt.datetime.strptime(s, fmt).date()
            except ValueError:
                continue
        return None
    return v


def _parse_peso(v: object) -> object:
    """Acepta peso como '8,5', '8.5 kg' o número; devuelve float o None."""
    if v is None or isinstance(v, (int, float)):
        return v
    if isinstance(v, str):
        m = re.search(r"\d+(?:[.,]\d+)?", v)
        return float(m.group().replace(",", ".")) if m else None
    return v


def _none_to_list(v: object) -> object:
    """Convierte None en lista vacía (el LLM a veces devuelve null en listas)."""
    return [] if v is None else v


FechaFlex = Annotated[date | None, BeforeValidator(_parse_fecha)]
PesoFlex = Annotated[float | None, BeforeValidator(_parse_peso)]


class Sexo(str, Enum):
    """Sexo del animal."""

    MACHO = "macho"
    HEMBRA = "hembra"


class TipoDesparasitacion(str, Enum):
    """Vía de la desparasitación."""

    INTERNA = "interna"
    EXTERNA = "externa"
    AMBAS = "ambas"


class Vacuna(BaseModel):
    """Registro de una vacuna en la cartilla."""

    nombre: str | None = Field(None, description="Nombre/tipo de vacuna (p. ej. polivalente, rabia).")
    fecha: FechaFlex = Field(None, description="Fecha de aplicación.")
    lote: str | None = Field(None, description="Número de lote, si consta.")
    proxima: FechaFlex = Field(None, description="Fecha de la próxima dosis/recordatorio.")


class Desparasitacion(BaseModel):
    """Registro de una desparasitación."""

    tipo: TipoDesparasitacion | None = None
    producto: str | None = None
    fecha: FechaFlex = None


class DogHealthRecord(BaseModel):
    """Perfil estructurado extraído de una cartilla veterinaria.

    Es el objeto que produce el Componente A y consume el Componente B.
    """

    nombre: str | None = Field(None, description="Nombre del perro.")
    especie: str | None = Field(None, description="Especie (normalmente 'perro').")
    raza: str | None = Field(None, description="Raza o mezcla.")
    sexo: Sexo | None = None
    castrado: bool | None = Field(None, description="True si castrado/esterilizado.")
    fecha_nacimiento: FechaFlex = None
    peso_kg: PesoFlex = Field(None, description="Peso en kilogramos.")
    microchip: str | None = Field(None, description="Número de identificación (microchip).")
    vacunas: Annotated[list[Vacuna], BeforeValidator(_none_to_list)] = Field(default_factory=list)
    desparasitaciones: Annotated[list[Desparasitacion], BeforeValidator(_none_to_list)] = Field(default_factory=list)
    alergias: str | None = None
    condiciones_medicas: str | None = None
    notas: str | None = None


class Cobertura(BaseModel):
    """Cobertura individual de una póliza de seguro de mascota."""

    nombre: str | None = None
    limite: str | None = Field(None, description="Límite/capital asegurado (texto tal cual).")
    copago: str | None = None
    carencia: str | None = Field(None, description="Periodo de carencia, si consta.")


class PolizaSeguro(BaseModel):
    """Estructura extraída de un condicionado de póliza de seguro de mascota."""

    aseguradora: str | None = None
    producto: str | None = None
    coberturas: list[Cobertura] = Field(default_factory=list)
    exclusiones: list[str] = Field(default_factory=list)
    prima_anual: str | None = None
