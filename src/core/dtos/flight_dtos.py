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
    level_ranges: Optional[List[str]] = None

class FlightOriginCountDTO(BaseModel):
    origin: str
    count: int

class FlightDestinationCountDTO(BaseModel):
    destination: str
    count: int