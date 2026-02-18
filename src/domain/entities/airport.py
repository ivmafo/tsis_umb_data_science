from pydantic import BaseModel
from typing import Optional

class Airport(BaseModel):
    id: Optional[int] = None
    icao_code: str
    iata_code: Optional[str] = None
    name: str
    city: str
    country: str
    latitude: float
    longitude: float
    altitude: int
    timezone: float
    dst: str
    type: str
    source: str
