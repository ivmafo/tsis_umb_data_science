from pydantic import BaseModel
from typing import Optional

class Airport(BaseModel):
    """
    Representa un aeropuerto dentro del sistema.
    
    Esta entidad contiene la información básica y geográfica necesaria para 
    identificar aeropuertos y realizar cálculos de distancias y zonas horarias.
    """
    id: Optional[int] = None
    icao_code: str  # Código OACI (ICAO) de 4 caracteres (ej. SKBO)
    iata_code: Optional[str] = None  # Código IATA de 3 caracteres (ej. BOG)
    name: str  # Nombre completo del aeropuerto
    city: str  # Ciudad donde se ubica
    country: str  # País de ubicación
    latitude: float  # Latitud en coordenadas decimales
    longitude: float  # Longitud en coordenadas decimales
    altitude: int  # Altitud sobre el nivel del mar en pies
    timezone: float  # Desplazamiento horario UTC
    dst: str  # Horario de verano (Daylight Saving Time)
    type: str  # Tipo de instalación (aeropuerto, helipuerto, etc.)
    source: str  # Fuente de los datos (ej. OurAirports)
