"""
Módulo que define la entidad de configuración del sistema.
Esta entidad se utiliza para almacenar pares clave-valor de configuración
con seguimiento temporal.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Config(BaseModel):
    """
    Clase que representa una configuración del sistema.

    Esta clase maneja las configuraciones del sistema utilizando un modelo
    de clave-valor con marcas de tiempo para seguimiento de cambios.

    Attributes:
        key (str): Clave única que identifica la configuración
        value (str): Valor asociado a la configuración
        created_at (datetime, optional): Fecha y hora de creación de la configuración
        updated_at (datetime, optional): Fecha y hora de la última actualización
    """
    key: str
    value: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None