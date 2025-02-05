# src/domain/entities/flight.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Flight(BaseModel):
    callsign: str                   # Callsign
    matricula: str                  # Matrícula
    tipo_aeronave: str              # Tip Aer
    empresa: str                    # Empresa
    numero_vuelo: str               # # Vuelo
    tipo_vuelo: str                 # Tip Vuel
    tiempo_inicial: datetime        # Tiempo Inicial
    origen: str                     # Origen
    pista_origen: Optional[str]     # Pista (Origen)
    sid: Optional[str]              # SID
    fecha_salida: datetime          # Fec Sal
    hora_salida: datetime           # Hr Sal (se combina con fecha_salida)
    destino: str                    # Destino
    pista_destino: Optional[str]    # Pista (Destino)
    fecha_llegada: datetime         # Fec Lle
    hora_llegada: datetime          # Hr Lle (se combina con fecha_llegada)
    nivel: Optional[str]            # Nivel
    ambito: Optional[str]           # Ambito
    nombre_origen: str              # Nombre origen ZZZZ
    nombre_destino: str             # Nombre destino ZZZZ

