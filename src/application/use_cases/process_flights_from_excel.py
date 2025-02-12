from infrastructure.adapters.excel_flight_transformer import ExcelFlightTransformer
from domain.ports.flight_repository import FlightRepository
from application.use_cases.create_flight import CreateFlightUseCase

class ProcessFlightsFromExcelUseCase:
    def __init__(self, flight_repository: FlightRepository):
        self.flight_repository = flight_repository

    def execute(self, file_path):
        transformer = ExcelFlightTransformer(file_path)
        flights = transformer.transform_flights()
        create_flight_uc = CreateFlightUseCase(self.flight_repository)

        for flight_data in flights:
            create_flight_uc.execute(flight_data)
