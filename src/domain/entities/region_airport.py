from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RegionAirport(BaseModel):
    id: Optional[int] = None
    icao_code: str
    region_id: int
    created_at: Optional[datetime] = None
