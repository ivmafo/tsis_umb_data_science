"""
Puerto que define el contrato para el repositorio de capacidad de sectores,
siguiendo los principios de arquitectura hexagonal y clean architecture.

Este puerto actúa como una interfaz en el núcleo del dominio que establece
las operaciones necesarias para consultar la capacidad de los sectores aéreos,
manteniendo la independencia de la implementación específica de persistencia.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from src.core.entities.sector_capacity import SectorCapacityResponse

class SectorCapacityRepository(ABC):
    """
    Puerto abstracto que define el contrato para el repositorio de capacidad de sectores.

    Esta interfaz sigue el patrón de puertos y adaptadores de la arquitectura hexagonal,
    permitiendo que el dominio defina las operaciones necesarias para consultar
    la capacidad de los sectores sin acoplarse a una implementación específica.

    Methods:
        get_sectors() -> List[str]:
            Obtiene la lista de todos los sectores disponibles.
            
        get_sector_capacity(sector: str, date: datetime) -> Optional[SectorCapacityResponse]:
            Obtiene la capacidad de un sector para una fecha específica.
    """

    @abstractmethod
    def get_sectors(self) -> List[str]:
        """
        Obtiene la lista de todos los sectores disponibles.

        Returns:
            List[str]: Lista de identificadores de sectores
        """
        pass

    @abstractmethod
    def get_sector_capacity(self, sector: str, date: datetime) -> Optional[SectorCapacityResponse]:
        """
        Obtiene la capacidad de un sector para una fecha específica.

        Args:
            sector (str): Identificador del sector
            date (datetime): Fecha para la cual se requiere la capacidad

        Returns:
            Optional[SectorCapacityResponse]: Respuesta con la capacidad del sector o None si no existe
        """
        pass