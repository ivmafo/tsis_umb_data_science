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
    
    # --- Parámetros RAC 14 (Capacidad y Performance) ---
    reference_code: Optional[str] = "4E"  # Código de referencia OACI (ej. 4E, 3C)
    has_rapid_exit_taxiway: bool = False  # Presencia de calles de salida rápida
    requires_backtrack: bool = False      # Si la pista requiere backtrack para el despegue
    
    @property
    def is_high_altitude(self) -> bool:
        """Determina automáticamente si la estación es de gran altitud (>5000 ft)"""
        return self.altitude > 5000
