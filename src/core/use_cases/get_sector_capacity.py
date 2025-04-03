"""
Módulo que implementa el caso de uso para obtener la capacidad de sectores aéreos,
siguiendo los principios de arquitectura hexagonal y clean architecture.

Este módulo contiene la lógica de negocio para consultar la capacidad
operativa de los sectores aéreos, manteniendo la independencia de los
detalles de implementación.
"""

from datetime import datetime
from typing import List, Optional
from src.core.ports.sector_capacity_repository import SectorCapacityRepository
from src.core.entities.sector_capacity import SectorCapacityResponse

class GetSectorCapacityUseCase:
    """
    Caso de uso para obtener la capacidad de sectores aéreos.

    Esta clase implementa la lógica de negocio para consultar la capacidad
    de los sectores aéreos, siguiendo el principio de responsabilidad única
    y manteniéndose independiente de los detalles de infraestructura.

    Attributes:
        _repository (SectorCapacityRepository): Repositorio de capacidad de sectores
    """

    def __init__(self, repository: SectorCapacityRepository):
        self._repository = repository

    def get_sectors(self) -> List[str]:
        """
        Obtiene la lista de todos los sectores disponibles.

        Returns:
            List[str]: Lista de identificadores de sectores
        """
        return self._repository.get_sectors()

    def execute(self, sector: str, date: datetime) -> Optional[SectorCapacityResponse]:
        """
        Ejecuta la consulta de capacidad de un sector.

        Este método implementa la lógica principal del caso de uso,
        validando los parámetros de entrada y delegando la consulta
        al repositorio correspondiente.

        Args:
            sector (str): Identificador del sector
            date (datetime): Fecha para la cual se requiere la capacidad

        Returns:
            Optional[SectorCapacityResponse]: Capacidad del sector o None si no existe

        Raises:
            ValueError: Si la fecha proporcionada no es un objeto datetime válido
        """
        if not isinstance(date, datetime):
            raise ValueError("La fecha debe ser un objeto datetime válido")
        return self._repository.get_sector_capacity(sector, date)