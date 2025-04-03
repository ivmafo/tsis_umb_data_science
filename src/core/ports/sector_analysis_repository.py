"""
Puerto que define el contrato para el repositorio de análisis de sectores,
siguiendo los principios de arquitectura hexagonal y clean architecture.

Este puerto actúa como una interfaz en el núcleo del dominio que establece
las operaciones necesarias para la gestión y consulta de análisis de sectores aéreos,
manteniendo la independencia de la implementación específica de persistencia.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from src.core.entities.sector_analysis import SectorDetailedAnalysis

class SectorAnalysisRepository(ABC):
    """
    Puerto abstracto que define el contrato para el repositorio de análisis de sectores.

    Esta interfaz sigue el patrón de puertos y adaptadores de la arquitectura hexagonal,
    permitiendo que el dominio defina las operaciones necesarias para la gestión de
    análisis de sectores sin acoplarse a una implementación específica.

    Methods:
        get_by_sector_and_date(sector: str, date: datetime) -> Optional[SectorDetailedAnalysis]:
            Obtiene el análisis de un sector para una fecha específica.
            
        get_by_sector(sector: str) -> List[SectorDetailedAnalysis]:
            Obtiene todos los análisis de un sector específico.
            
        get_all_sectors() -> List[str]:
            Obtiene la lista de todos los sectores disponibles.
            
        get_analysis_by_date_range(sector: str, start_date: datetime, end_date: datetime) -> List[SectorDetailedAnalysis]:
            Obtiene los análisis de un sector en un rango de fechas.
    """

    @abstractmethod
    def get_by_sector_and_date(self, sector: str, date: datetime) -> Optional[SectorDetailedAnalysis]:
        """
        Obtiene el análisis de un sector para una fecha específica.

        Args:
            sector (str): Identificador del sector
            date (datetime): Fecha del análisis

        Returns:
            Optional[SectorDetailedAnalysis]: Análisis detallado del sector o None si no existe
        """
        pass

    @abstractmethod
    def get_by_sector(self, sector: str) -> List[SectorDetailedAnalysis]:
        """
        Obtiene todos los análisis de un sector específico.

        Args:
            sector (str): Identificador del sector

        Returns:
            List[SectorDetailedAnalysis]: Lista de análisis detallados del sector
        """
        pass

    @abstractmethod
    def get_all_sectors(self) -> List[str]:
        """
        Obtiene la lista de todos los sectores disponibles.

        Returns:
            List[str]: Lista de identificadores de sectores
        """
        pass

    @abstractmethod
    def get_analysis_by_date_range(self, sector: str, start_date: datetime, end_date: datetime) -> List[SectorDetailedAnalysis]:
        """
        Obtiene los análisis de un sector en un rango de fechas.

        Args:
            sector (str): Identificador del sector
            start_date (datetime): Fecha inicial del rango
            end_date (datetime): Fecha final del rango

        Returns:
            List[SectorDetailedAnalysis]: Lista de análisis detallados en el rango de fechas
        """
        pass