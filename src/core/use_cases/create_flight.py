# src/application/use_cases/create_flight.py
from src.domain.ports.flight_repository import FlightRepository
from src.domain.entities.flight import Flight

class CreateFlightUseCase:
    def __init__(self, flight_repository: FlightRepository):
        self.flight_repository = flight_repository

    def execute(self, flight_data: dict) -> Flight:
        # Validar y convertir fechas/horas
        flight = Flight(**flight_data)
        return self.flight_repository.save(flight)

