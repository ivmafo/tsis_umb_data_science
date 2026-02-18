from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RegionAirport(BaseModel):
    """
    Entidad que gestiona la relación entre una Región y un Aeropuerto.
    
    Define a qué región pertenece cada aeropuerto identificado por su código ICAO.
    """
    id: Optional[int] = None
    icao_code: str  # El código ICAO del aeropuerto asociado
    region_id: int  # El ID de la región a la cual pertenece
    created_at: Optional[datetime] = None  # Fecha de asignación de la relación
