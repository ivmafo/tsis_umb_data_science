# src\core\use_cases\process_flights_from_excel.py
from src.infraestructure.adapters.excel_flight_transformer import ExcelFlightTransformer
from src.core.ports.flight_repository import FlightRepository
from src.core.ports.file_processing_control_repository import FileProcessingControlRepository
from src.core.use_cases.create_flight import CreateFlightUseCase

class ProcessFlightsFromExcelUseCase:
    def __init__(self, flight_repository: FlightRepository, file_repository: FileProcessingControlRepository):
        self.flight_repository = flight_repository
        self.file_repository = file_repository


    def execute(self, file_path):
        # verificar si archivo ya ha sido procesado
        if self.file_repository.is_file_processed(file_path):
            print(f"El archivo {file_path} ya ha sido procesado")
            return

        # tranformacion de los datos de archivo excel
        transformer = ExcelFlightTransformer(file_path)
        flights = transformer.transform_flights()
        create_flight_uc = CreateFlightUseCase(self.flight_repository)

        # procesar los datos y guardarlos en la base de datos 
        for flight_data in flights:
            create_flight_uc.execute(flight_data)

        # Registrar archivo como procesado
        self.file_repository.add_file(file_path)




