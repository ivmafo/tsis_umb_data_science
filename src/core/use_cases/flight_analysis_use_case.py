from typing import List
from src.core.dtos.flight_dtos import (
    DateRangesAnalysisRequestDTO,
    FlightMonthlyCountDTO,
    DateRangeDTO
)
from src.core.ports.outbound.flight_repository import FlightRepository

class FlightAnalysisUseCase:
    def __init__(self, flight_repository: FlightRepository):
        self.flight_repository = flight_repository

    # ... existing methods ...

    def get_monthly_counts(self, request: DateRangesAnalysisRequestDTO) -> List[FlightMonthlyCountDTO]:
        """
        Get monthly flight counts for the specified date ranges.
        
        Args:
            request: The analysis request containing date ranges and analysis type
            
        Returns:
            List of monthly counts for each date range
        """
        try:
            if request.type == 'origin':
                return self.flight_repository.get_monthly_counts_by_date_ranges(
                    date_ranges=request.date_ranges,
                    analysis_type=request.type
                )
            elif request.type == 'destination':
                return self.flight_repository.get_monthly_counts_by_date_ranges_destination(
                    date_ranges=request.date_ranges
                )
            else:
                raise ValueError(f"Invalid analysis type: {request.type}")
                
        except Exception as e:
            raise Exception(f"Error getting monthly counts: {str(e)}")