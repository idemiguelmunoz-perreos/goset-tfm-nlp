"""Esquemas Pydantic: objetivo de extracción del Componente A.

Todos los campos son opcionales (``None`` por defecto) para poder medir
*null-handling accuracy*: el modelo debe devolver ``None`` cuando el dato no
aparece en el documento, en vez de inventarlo (hallucination).

Los campos de la cartilla alimentan las features del Componente B (recomendador).
"""

from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


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
    fecha: date | None = Field(None, description="Fecha de aplicación.")
    lote: str | None = Field(None, description="Número de lote, si consta.")
    proxima: date | None = Field(None, description="Fecha de la próxima dosis/recordatorio.")


class Desparasitacion(BaseModel):
    """Registro de una desparasitación."""

    tipo: TipoDesparasitacion | None = None
    producto: str | None = None
    fecha: date | None = None


class DogHealthRecord(BaseModel):
    """Perfil estructurado extraído de una cartilla veterinaria.

    Es el objeto que produce el Componente A y consume el Componente B.
    """

    nombre: str | None = Field(None, description="Nombre del perro.")
    especie: str | None = Field(None, description="Especie (normalmente 'perro').")
    raza: str | None = Field(None, description="Raza o mezcla.")
    sexo: Sexo | None = None
    castrado: bool | None = Field(None, description="True si castrado/esterilizado.")
    fecha_nacimiento: date | None = None
    peso_kg: float | None = Field(None, ge=0, description="Peso en kilogramos.")
    microchip: str | None = Field(None, description="Número de identificación (microchip).")
    vacunas: list[Vacuna] = Field(default_factory=list)
    desparasitaciones: list[Desparasitacion] = Field(default_factory=list)
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
