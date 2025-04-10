from datetime import datetime
from dataclasses import dataclass

@dataclass
class Region:
    id: int
    name: str
    code: str
    description: str = None
    created_at: datetime = None
    updated_at: datetime = None