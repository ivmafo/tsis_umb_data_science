# src\core\dtos
from pydantic import BaseModel, validator
from typing import List, Optional, Dict
from datetime import datetime

class FlightFilterDTO(BaseModel):
    years: Optional[List[str]] = None
    months: Optional[List[str]] = None
    origins: Optional[List[str]] = None
    destinations: Optional[List[str]] = None
    flight_types: Optional[List[str]] = None
    airlines: Optional[List[str]] = None
    aircraft_types: Optional[List[str]] = None

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

# Add these classes to the existing file
class DateRangeDTO(BaseModel):
    id: int
    start_date: str
    end_date: str
    label: str

class DateRangesAnalysisRequestDTO(BaseModel):
    date_ranges: List[DateRangeDTO]
    airport: Optional[str] = None
    type: str

class FlightHourlyCountDTO(BaseModel):
    hour: int
    counts: Dict[str, int]

