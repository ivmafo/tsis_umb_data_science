"""
Módulo que define la entidad de análisis detallado de sectores aéreos,
siguiendo los principios de arquitectura hexagonal y clean architecture.

Esta entidad forma parte del núcleo del dominio y encapsula toda la información
relacionada con el análisis de capacidad y complejidad de sectores aéreos.
"""

from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class SectorDetailedAnalysis(BaseModel):
    """
    Entidad que representa el análisis detallado de un sector aéreo.

    Esta clase es una entidad de dominio pura que encapsula los datos
    y métricas relacionadas con el análisis de un sector aéreo específico,
    siguiendo los principios de Clean Architecture.

    Attributes:
        sector (str): Identificador del sector aéreo analizado
        hora (datetime): Hora específica del análisis
        num_vuelos (int): Número total de vuelos en el sector
        tps (Decimal): Tasa de procesamiento del sector (Tasks Per Second)
        tipos_aeronaves (int): Cantidad de diferentes tipos de aeronaves
        aerolineas (int): Cantidad de aerolíneas operando en el sector
        tipos_vuelo (int): Cantidad de diferentes tipos de vuelo
        tiempo_total_comunicaciones (Decimal): Tiempo total dedicado a comunicaciones
        tiempo_total_coordinacion (Decimal): Tiempo total dedicado a coordinación
        tiempo_tareas_observables (Decimal): Tiempo total de tareas observables
        factor_complejidad (Decimal): Factor calculado de complejidad del sector

    Note:
        Esta entidad es fundamental para el análisis de capacidad y
        eficiencia de los sectores aéreos, y forma parte del núcleo
        del dominio de la aplicación.
    """
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