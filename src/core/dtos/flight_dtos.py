# src\core\dtos
from pydantic import BaseModel
from typing import List, Optional

class FlightFilterDTO(BaseModel):
    years: Optional[List[str]] = None
    months: Optional[List[str]] = None
    origins: Optional[List[str]] = None
    destinations: Optional[List[str]] = None
    flight_types: Optional[List[str]] = None
    airlines: Optional[List[str]] = None
    aircraft_types: Optional[List[str]] = None
    # Removed level_ranges field

class FlightOriginCountDTO(BaseModel):
    origin: str
    count: int

class FlightDestinationCountDTO(BaseModel):
    destination: str
    count: int

class FlightAirlineCountDTO(BaseModel):
    airline: str
    count: int

class FlightTypeCountDTO(BaseModel):
    flight_type: str
    count: int