# src\core\dtos
"""
Módulo que contiene los Data Transfer Objects (DTOs) relacionados con los vuelos.
Estos DTOs se utilizan para transferir datos entre las diferentes capas de la aplicación.
"""

from pydantic import BaseModel, validator
from typing import List, Optional, Dict
from datetime import datetime

class FlightFilterDTO:
    def __init__(
        self, 
        years: List[str] = None, 
        months: List[str] = None, 
        origins: List[str] = None, 
        destinations: List[str] = None, 
        flight_types: List[str] = None,
        airlines: List[str] = None,
        aircraft_types: List[str] = None,
        level_ranges: List[str] = None,
        level_min: int = None,
        level_max: int = None
    ):
        self.years = years or []
        self.months = months or []
        self.origins = origins or []
        self.destinations = destinations or []
        self.flight_types = flight_types or []
        self.airlines = airlines or []
        self.aircraft_types = aircraft_types or []
        self.level_ranges = level_ranges or []
        self.level_min = level_min
        self.level_max = level_max

class FlightOriginCountDTO(BaseModel):
    """
    DTO para el conteo de vuelos por aeropuerto de origen.

    Attributes:
        origin (str): Código del aeropuerto de origen
        count (int): Cantidad de vuelos desde ese origen
    """
    origin: str
    count: int

class FlightDestinationCountDTO(BaseModel):
    """
    DTO para el conteo de vuelos por aeropuerto de destino.

    Attributes:
        destination (str): Código del aeropuerto de destino
        count (int): Cantidad de vuelos hacia ese destino
    """
    destination: str
    count: int

class FlightAirlineCountDTO(BaseModel):
    """
    DTO para el conteo de vuelos por aerolínea.

    Attributes:
        airline (str): Nombre de la aerolínea
        count (int): Cantidad de vuelos de esa aerolínea
    """
    airline: str
    count: int

class FlightTypeCountDTO(BaseModel):
    """
    DTO para el conteo de vuelos por tipo.

    Attributes:
        flight_type (str): Tipo de vuelo
        count (int): Cantidad de vuelos de ese tipo
    """
    flight_type: str
    count: int

class DateRangeDTO(BaseModel):
    """
    DTO para representar un rango de fechas.
    """
    id: int
    start_date: str
    end_date: str
    label: str
    origin_airport: str
    destination_airport: str

class DateRangesAnalysisRequestDTO(BaseModel):
    """
    DTO para solicitar análisis de rangos de fechas.

    Attributes:
        date_ranges (List[DateRangeDTO]): Lista de rangos de fechas a analizar
        airport (str, optional): Código del aeropuerto para filtrar
        type (str): Tipo de análisis ('origin' o 'destination')
    """
    date_ranges: List[DateRangeDTO]
    airport: Optional[str] = None
    type: str

class FlightHourlyCountDTO(BaseModel):
    """
    DTO para el conteo de vuelos por hora.

    Attributes:
        hour (int): Hora del día (0-23)
        counts (Dict[str, int]): Diccionario con conteos por rango de fechas
    """
    hour: int
    counts: Dict[str, int]

