"""
Módulo que implementa el caso de uso para obtener conteos horarios de vuelos,
siguiendo los principios de arquitectura hexagonal y clean architecture.

Este módulo contiene la lógica de negocio para obtener estadísticas
de vuelos por hora, manteniendo la independencia de los detalles de
implementación de infraestructura.
"""

from typing import List
from src.core.ports.flight_repository import FlightRepository
from src.core.dtos.flight_dtos import DateRangesAnalysisRequestDTO, FlightHourlyCountDTO

class GetFlightHourlyCountsUseCase:
    """
    Caso de uso para obtener conteos horarios de vuelos.

    Esta clase implementa la lógica de negocio para obtener estadísticas
    de vuelos agrupados por hora, siguiendo el principio de responsabilidad
    única y manteniéndose independiente de los detalles de infraestructura.

    Attributes:
        _flight_repository (FlightRepository): Repositorio de vuelos
    """

    def __init__(self, flight_repository: FlightRepository):
        self._flight_repository = flight_repository

    def execute(self, request: DateRangesAnalysisRequestDTO) -> List[FlightHourlyCountDTO]:
        """
        Ejecuta la obtención de conteos horarios de vuelos.

        Este método implementa la lógica principal del caso de uso,
        delegando la consulta al repositorio y procesando los resultados
        según los rangos de fechas especificados.

        Args:
            request (DateRangesAnalysisRequestDTO): DTO con los rangos de fechas a analizar

        Returns:
            List[FlightHourlyCountDTO]: Lista de conteos de vuelos por hora
        """
        return self._flight_repository.get_hourly_counts_by_date_ranges(request.date_ranges)