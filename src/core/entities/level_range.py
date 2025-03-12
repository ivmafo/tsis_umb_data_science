from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LevelRange(BaseModel):
    id: Optional[int] = None
    min_level: int
    max_level: int
    alias: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None