from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class SectorDetailedAnalysis(BaseModel):
    sector: str
    hora: datetime
    num_vuelos: int
    tps: Decimal
    tipos_aeronaves: int
    aerolineas: int
    tipos_vuelo: int
    tiempo_total_comunicaciones: Decimal
    tiempo_total_coordinacion: Decimal
    tiempo_tareas_observables: Decimal
    factor_complejidad: Decimal