from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class AirportRegion:
    id: int
    icao_code: str
    region_id: int
    created_at: Optional[datetime] = None