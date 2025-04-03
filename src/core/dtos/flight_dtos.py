# src\core\dtos
"""
Módulo que contiene los Data Transfer Objects (DTOs) relacionados con los vuelos.
Estos DTOs se utilizan para transferir datos entre las diferentes capas de la aplicación.
"""

from pydantic import BaseModel, validator
from typing import List, Optional, Dict
from datetime import datetime

class FlightFilterDTO(BaseModel):
    """
    DTO para filtrar vuelos según diferentes criterios.

    Attributes:
        years (List[str]): Lista de años para filtrar
        months (List[str]): Lista de meses para filtrar
        origins (List[str]): Lista de aeropuertos de origen
        destinations (List[str]): Lista de aeropuertos de destino
        flight_types (List[str]): Lista de tipos de vuelo
        airlines (List[str]): Lista de aerolíneas
        aircraft_types (List[str]): Lista de tipos de aeronaves
    """
    years: Optional[List[str]] = None
    months: Optional[List[str]] = None
    origins: Optional[List[str]] = None
    destinations: Optional[List[str]] = None
    flight_types: Optional[List[str]] = None
    airlines: Optional[List[str]] = None
    aircraft_types: Optional[List[str]] = None

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

    Attributes:
        id (int): Identificador único del rango
        start_date (str): Fecha de inicio en formato string
        end_date (str): Fecha de fin en formato string
        label (str): Etiqueta descriptiva del rango
    """
    id: int
    start_date: str
    end_date: str
    label: str

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

