from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from src.domain.entities.region_airport import RegionAirport

class RegionAirportRepository(ABC):
    """
    Interface para gestionar la asignación de aeropuertos a regiones.
    """
    @abstractmethod
    def get_paginated(self, page: int, page_size: int, search: str = "") -> Tuple[List[RegionAirport], int]:
        """Obtiene el listado paginado de asignaciones aeropuerto-región."""
        pass

    @abstractmethod
    def create(self, region_airport: RegionAirport) -> RegionAirport:
        """Registra la pertenencia de un aeropuerto a una región."""
        pass

    @abstractmethod
    def update(self, id: int, region_airport: RegionAirport) -> RegionAirport:
        """Actualiza una asignación existente."""
        pass

    @abstractmethod
    def delete(self, id: int) -> None:
        """Elimina la relación entre un aeropuerto y su región."""
        pass
