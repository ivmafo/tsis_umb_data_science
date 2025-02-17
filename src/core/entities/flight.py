# src/domain/entities/flight.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Flight(BaseModel):
    fecha: Optional[datetime]                 # Fecha
    sid: Optional[int]                        # SID (db) /  ID Excel
    callsign: Optional[str]                   # Callsign
    matricula: Optional[str]                  # Matrícula
    tipo_aeronave: Optional[str]              # Tip Aer
    empresa: Optional[str]                    # Empresa
    numero_vuelo: Optional[int]               # Vuelo
    tipo_vuelo: Optional[str]                 # Tip Vuel
    tiempo_inicial: Optional[datetime]        # Tiempo Inicial
    origen: Optional[str]                     # Origen
    pista_origen: Optional[str]               # Pista (Origen)    
    fecha_salida: Optional[datetime]          # Fec Sal
    hora_salida: Optional[datetime]           # Hr Sal (se combina con fecha_salida)
    destino: Optional[str]                    # Destino
    pista_destino: Optional[str]              # Pista (Destino)
    fecha_llegada: Optional[datetime]         # Fec Lle
    hora_llegada: Optional[datetime]          # Hr Lle (se combina con fecha_llegada)
    nivel: Optional[int]                      # Nivel
    ambito: Optional[str]                     # Ambito
    nombre_origen:Optional[str]               # Nombre origen ZZZZ
    nombre_destino: Optional[str]             # Nombre destino ZZZZ
    fecha_registro: Optional[datetime]        # Fecha Registro