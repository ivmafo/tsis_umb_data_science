"""
Módulo que implementa el caso de uso para obtener el conteo de vuelos por origen,
siguiendo los principios de arquitectura hexagonal y clean architecture.

Este módulo contiene la lógica de negocio para obtener estadísticas
de vuelos agrupados por origen, manteniendo la independencia de los
detalles de implementación.
"""

from src.core.ports.flight_repository import FlightRepository
from src.core.dtos.flight_dtos import FlightFilterDTO, FlightOriginCountDTO
from typing import List

class GetFlightOriginsCountUseCase:
    """
    Caso de uso para obtener el conteo de vuelos por origen.

    Esta clase implementa la lógica de negocio para obtener estadísticas
    de vuelos agrupados por aeropuerto de origen, siguiendo el principio
    de responsabilidad única y manteniéndose independiente de los detalles
    de infraestructura.

    Attributes:
        _flight_repository (FlightRepository): Repositorio de vuelos
    """

    def __init__(self, flight_repository: FlightRepository):
        self._flight_repository = flight_repository

    def execute(self, filters: FlightFilterDTO) -> List[FlightOriginCountDTO]:
        """
        Ejecuta la obtención del conteo de vuelos por origen.

        Este método implementa la lógica principal del caso de uso,
        aplicando los filtros especificados y delegando la consulta
        al repositorio correspondiente.

        Args:
            filters (FlightFilterDTO): DTO con los criterios de filtrado

        Returns:
            List[FlightOriginCountDTO]: Lista de conteos de vuelos por origen
        """
        return self._flight_repository.get_origins_count(filters)