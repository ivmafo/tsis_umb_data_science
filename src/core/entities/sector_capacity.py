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
    factor_complejidad: Decimal
    scv: Decimal
    capacidad_horaria: int
    carga_trabajo_total: Decimal
    tipos_aeronaves: Optional[int] = None
    aerolineas: Optional[int] = None
    factor_complejidad_total: Optional[Decimal] = None
    vuelos_alto_nivel: Optional[int] = None
    vuelos_bajo_nivel: Optional[int] = None