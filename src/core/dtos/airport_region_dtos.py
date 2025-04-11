from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AirportRegionDTO(BaseModel):
    id: Optional[int] = None
    icao_code: str
    region_id: int
    created_at: Optional[datetime] = None

class AirportRegionCreateDTO(BaseModel):
    icao_code: str
    region_id: int

class AirportRegionUpdateDTO(BaseModel):
    icao_code: Optional[str] = None
    region_id: Optional[int] = None