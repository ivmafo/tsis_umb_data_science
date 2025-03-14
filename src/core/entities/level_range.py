# src\core\entities\level_range.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LevelRange(BaseModel):
    id: Optional[int] = None
    origen: str
    destino: str
    nivel_min: int
    nivel_max: int
    ruta: str
    zona: str    
    