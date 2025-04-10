from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RegionDTO(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class RegionCreateDTO(BaseModel):
    name: str
    code: str
    description: Optional[str] = None

class RegionUpdateDTO(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None