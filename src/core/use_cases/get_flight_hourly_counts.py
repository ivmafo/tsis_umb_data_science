from typing import List
from src.core.ports.flight_repository import FlightRepository
from src.core.dtos.flight_dtos import DateRangesAnalysisRequestDTO, FlightHourlyCountDTO

class GetFlightHourlyCountsUseCase:
    def __init__(self, flight_repository: FlightRepository):
        self._flight_repository = flight_repository

    def execute(self, request: DateRangesAnalysisRequestDTO) -> List[FlightHourlyCountDTO]:
        return self._flight_repository.get_hourly_counts_by_date_ranges(request.date_ranges)