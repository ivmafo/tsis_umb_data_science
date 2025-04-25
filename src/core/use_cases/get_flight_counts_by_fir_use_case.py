from typing import List, Dict
from src.core.ports.flight_repository import FlightRepository
from src.core.dtos.flight_dtos import DateRangeDTO

class GetFlightCountsByFirUseCase:
    """
    Use case for getting flight counts grouped by FIR (Flight Information Region)
    with geographical coordinates for origin and destination airports.
    """

    def __init__(self, flight_repository: FlightRepository):
        self.flight_repository = flight_repository


    def execute(self, date_ranges: List[DateRangeDTO]) -> List[Dict]:
        """
        Execute the use case to get flight counts by FIR.

        Args:
            date_ranges (List[DateRangeDTO]): List of date range criteria including:
                - id: Identifier for the date range
                - label: Label for the date range
                - start_date: Start date for analysis
                - end_date: End date for analysis
                - origin_airport: Origin airport code
                - nivel_min: Minimum flight level
                - nivel_max: Maximum flight level

        Returns:
            List[Dict]: List of dictionaries containing:
                - label: Date range label
                - origin: Origin airport code
                - destination: Destination airport code
                - fir: Flight Information Region name
                - longitude_origin: Origin airport longitude
                - latitude_origin: Origin airport latitude
                - longitude_destination: Destination airport longitude
                - latitude_destination: Destination airport latitude
                - count: Number of flights
        """
        return self.flight_repository.get_flight_counts_by_fir(date_ranges)
