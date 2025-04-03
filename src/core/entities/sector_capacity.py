"""
Módulo que define la entidad de capacidad de sectores aéreos,
siguiendo los principios de arquitectura hexagonal y clean architecture.

Esta entidad forma parte del núcleo del dominio y representa los cálculos
y métricas relacionados con la capacidad operativa de un sector aéreo.
"""

from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import Optional

class SectorCapacityResponse(BaseModel):
    """
    Entidad que representa la respuesta del análisis de capacidad de un sector aéreo.

    Esta clase es una entidad de dominio pura que encapsula los resultados
    del análisis de capacidad de un sector, siguiendo los principios de Clean Architecture.
    No contiene dependencias externas ni lógica de infraestructura.

    Attributes:
        sector (str): Identificador del sector aéreo analizado
        hora (datetime): Hora específica del análisis
        tps (Decimal): Tasa de procesamiento del sector
        tfc (Decimal): Tiempo de comunicaciones
        tm (Decimal): Tiempo de monitoreo
        tc (Decimal): Tiempo de coordinación
        tt (Decimal): Tiempo total
        scv_value (Decimal): Valor del Sistema de Control Vectorial
        capacidad_horaria_base (int): Capacidad horaria en condiciones normales
        capacidad_horaria_alta (int): Capacidad horaria en alta demanda
        capacidad_horaria_baja (int): Capacidad horaria en baja demanda
        carga_trabajo_total_base (Decimal): Carga de trabajo en condiciones normales
        carga_trabajo_total_alta (Decimal): Carga de trabajo en alta demanda
        carga_trabajo_total_baja (Decimal): Carga de trabajo en baja demanda

    Note:
        Esta entidad es crucial para la evaluación y gestión de la
        capacidad operativa de los sectores aéreos.
    """
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
    