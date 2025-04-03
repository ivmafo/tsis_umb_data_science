"""
Módulo que define la entidad LevelRange para el manejo de rangos de niveles de vuelo,
siguiendo los principios de arquitectura hexagonal y clean architecture.

Esta entidad forma parte del núcleo del dominio y encapsula las reglas de negocio
relacionadas con los rangos de niveles permitidos entre diferentes rutas.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LevelRange(BaseModel):
    """
    Entidad que representa un rango de niveles de vuelo entre dos puntos.

    Esta clase es una entidad de dominio pura que define los niveles de vuelo
    permitidos para rutas específicas, siguiendo los principios de Clean Architecture.
    No contiene dependencias externas ni lógica de infraestructura.

    Attributes:
        id (int, optional): Identificador único del rango de nivel
        origen (str): Punto de origen de la ruta
        destino (str): Punto de destino de la ruta
        nivel_min (int): Nivel de vuelo mínimo permitido
        nivel_max (int): Nivel de vuelo máximo permitido
        ruta (str): Identificador de la ruta aérea
        zona (str): Zona o sector aéreo al que pertenece la ruta

    Note:
        Esta entidad es fundamental para la gestión de niveles de vuelo
        y forma parte del núcleo del dominio de la aplicación.
    """
    id: Optional[int] = None
    origen: str
    destino: str
    nivel_min: int
    nivel_max: int
    ruta: str
    zona: str
    