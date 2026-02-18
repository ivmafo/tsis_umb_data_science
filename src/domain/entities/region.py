from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Region:
    name: str
    code: str
    description: str
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    nivel_min: Optional[int] = 0
