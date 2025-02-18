# src/domain/entities/flight.py
from pydantic import BaseModel, Field, validator
from datetime import datetime, time, date
from typing import Optional

class Flight(BaseModel):
    fecha: Optional[datetime]                 # Fecha
    sid: Optional[int]                        # SID (db) /  ID Excel
    ssr: Optional[int]                        # SSR
    callsign: Optional[str]                   # Callsign
    matricula: Optional[str]                  # Matrícula
    tipo_aeronave: Optional[str]              # Tip Aer
    empresa: Optional[str]                    # Empresa
    numero_vuelo: Optional[int]               # Vuelo
    tipo_vuelo: Optional[str]                 # Tip Vuel
    tiempo_inicial: Optional[datetime]        # Tiempo Inicial
    origen: Optional[str]                     # Origen
    fecha_salida: Optional[datetime]          # Fec Sal
    hora_salida: Optional[time]           # Hr Sal (se combina con fecha_salida)
    #hora_salida: time = Field(..., description="Hora de salida del vuelo")
    hora_pv: Optional[time]               # hora pv  
    destino: Optional[str]                    # Pista (Destino)
    fecha_llegada: Optional[datetime]         # Fec Lle
    hora_llegada: Optional[time]          # Hr Lle (se combina con fecha_llegada)
    nivel: Optional[int]                      # Nivel
    duracion: Optional[int]
    distancia: Optional[int]
    velocidad: Optional[int]
    eq_ssr: Optional[str]
    nombre_origen:Optional[str]               # Nombre origen ZZZZ
    nombre_destino: Optional[str]             # Nombre destino ZZZZ
    fecha_registro: Optional[datetime]        # Fecha Registro