"""
Módulo que define la entidad principal de Vuelo (Flight) siguiendo los principios de
arquitectura hexagonal y clean architecture.

Esta entidad representa el objeto de dominio central para el manejo de información
de vuelos, encapsulando toda la lógica y reglas de negocio relacionadas con los vuelos.
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime, time, date
from typing import Optional

class Flight(BaseModel):
    """
    Entidad que representa un vuelo en el sistema.

    Esta clase es una entidad de dominio pura que encapsula los atributos y comportamientos
    esenciales de un vuelo, siguiendo los principios de Clean Architecture.
    No depende de frameworks externos ni de la capa de infraestructura.

    Attributes:
        fecha (datetime, optional): Fecha general del vuelo
        sid (int, optional): Identificador único del vuelo en el sistema
        ssr (str, optional): Código de radar secundario de vigilancia
        callsign (str, optional): Señal distintiva de la aeronave
        matricula (str, optional): Matrícula de identificación de la aeronave
        tipo_aeronave (str, optional): Tipo o modelo de la aeronave
        empresa (str, optional): Compañía aérea operadora del vuelo
        numero_vuelo (int, optional): Número identificador del vuelo
        tipo_vuelo (str, optional): Clasificación del tipo de vuelo
        tiempo_inicial (datetime, optional): Tiempo de inicio del vuelo
        origen (str, optional): Aeropuerto o lugar de origen
        fecha_salida (datetime, optional): Fecha programada de salida
        hora_salida (time, optional): Hora específica de salida
        hora_pv (time, optional): Hora de plan de vuelo
        destino (str, optional): Aeropuerto o lugar de destino
        fecha_llegada (datetime, optional): Fecha programada de llegada
        hora_llegada (time, optional): Hora específica de llegada
        nivel (int, optional): Nivel de vuelo
        duracion (int, optional): Duración del vuelo en minutos
        distancia (int, optional): Distancia del vuelo en millas náuticas
        velocidad (int, optional): Velocidad de la aeronave
        eq_ssr (str, optional): Equipamiento SSR de la aeronave
        nombre_origen (str, optional): Nombre completo del lugar de origen
        nombre_destino (str, optional): Nombre completo del lugar de destino
        fecha_registro (datetime, optional): Fecha de registro en el sistema

    Note:
        Esta entidad forma parte del núcleo de dominio y no debe contener
        lógica de infraestructura o frameworks externos.
    """
    fecha: Optional[datetime]                 # Fecha
    sid: Optional[int]                        # SID (db) /  ID Excel
    ssr: Optional[str]                        # SSR
    callsign: Optional[str]                   # Callsign
    matricula: Optional[str]                  # Matrícula
    tipo_aeronave: Optional[str]              # Tip Aer
    empresa: Optional[str]                    # Empresa
    numero_vuelo: Optional[int]               # Vuelo
    tipo_vuelo: Optional[str]                 # Tip Vuel
    tiempo_inicial: Optional[datetime]        # Tiempo Inicial
    origen: Optional[str]                     # Origen
    fecha_salida: Optional[datetime]          # Fec Sal
    hora_salida: Optional[time]               # Hr Sal (se combina con fecha_salida)
    hora_pv: Optional[time]                   # hora pv  
    destino: Optional[str]                    # Pista (Destino)
    fecha_llegada: Optional[datetime]         # Fec Lle
    hora_llegada: Optional[time]              # Hr Lle (se combina con fecha_llegada)
    nivel: Optional[int]                      # Nivel
    duracion: Optional[int]
    distancia: Optional[int]
    velocidad: Optional[int]
    eq_ssr: Optional[str]
    nombre_origen: Optional[str]              # Nombre origen ZZZZ
    nombre_destino: Optional[str]             # Nombre destino ZZZZ
    fecha_registro: Optional[datetime]        # Fecha Registro