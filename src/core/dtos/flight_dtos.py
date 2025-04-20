# src\core\dtos
"""
Módulo que contiene los Data Transfer Objects (DTOs) relacionados con los vuelos.
Estos DTOs se utilizan para transferir datos entre las diferentes capas de la aplicación.
"""

from pydantic import BaseModel, validator
from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime, date

class FlightFilterDTO(BaseModel):
    years: Optional[List[str]] = []
    months: Optional[List[str]] = []
    origins: Optional[List[str]] = []
    destinations: Optional[List[str]] = []
    flight_types: Optional[List[str]] = []
    airlines: Optional[List[str]] = []
    aircraft_types: Optional[List[str]] = []
    level_ranges: Optional[List[str]] = []
    level_min: Optional[int] = None
    level_max: Optional[int] = None

    class Config:
        arbitrary_types_allowed = True

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
    id: str
    start_date: str
    end_date: str
    label: str
    origin_airport: Optional[str] = None
    destination_airport: Optional[str] = None
    nivel_min: Optional[int] = None
    nivel_max: Optional[int] = None

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


@dataclass
class FlightMonthlyCountDTO:
    year: int
    month: int
    counts: Dict[str, int]

# Update the imports in the repository file

