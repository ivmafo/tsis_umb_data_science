from src.core.ports.flight_repository import FlightRepository
from src.core.dtos.flight_dtos import FlightFilterDTO, FlightOriginCountDTO
from typing import List

class GetFlightOriginsCountUseCase:
    def __init__(self, flight_repository: FlightRepository):
        self._flight_repository = flight_repository

    def execute(self, filters: FlightFilterDTO) -> List[FlightOriginCountDTO]:
        return self._flight_repository.get_origins_count(filters)