from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Region:
    """
    Entidad que representa una Región Aeronáutica o zona de control.
    
    Se utiliza para agrupar aeropuertos y sectores bajo una misma jurisdicción administrativa
    o geográfica para el cálculo de métricas y reportes.
    """
    name: str  # Nombre descriptivo de la región (ej. Región Andina)
    code: str  # Código único identificador de la región
    description: str  # Descripción detallada de la zona cubierta
    id: Optional[int] = None  # Identificador único en la base de datos
    created_at: Optional[datetime] = None  # Fecha de creación del registro
    updated_at: Optional[datetime] = None  # Fecha de la última actualización
    nivel_min: Optional[int] = 0  # Nivel de vuelo mínimo asociado a la región
