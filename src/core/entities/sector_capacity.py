from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import Optional

class SectorCapacityResponse(BaseModel):
    sector: str
    hora: datetime
    tps: Decimal
    tfc: Decimal
    tm: Decimal
    tc: Decimal
    tt: Decimal
    scv_value: Decimal
    capacidad_horaria_base: int
    capacidad_horaria_alta: int
    capacidad_horaria_baja: int
    carga_trabajo_total_base: Decimal
    carga_trabajo_total_alta: Decimal
    carga_trabajo_total_baja: Decimal
    