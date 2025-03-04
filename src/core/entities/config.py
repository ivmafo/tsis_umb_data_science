from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Config(BaseModel):
    key: str
    value: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None