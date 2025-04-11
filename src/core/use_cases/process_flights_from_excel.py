# src\core\use_cases\process_flights_from_excel.py
from src.infraestructure.adapters.excel_flight_transformer import ExcelFlightTransformer
from src.core.ports.flight_repository import FlightRepository
from src.core.ports.file_processing_control_repository import FileProcessingControlRepository
from src.core.use_cases.create_flight import CreateFlightUseCase
from src.core.entities.flight import Flight  # Importar la clase Flight

class ProcessFlightsFromExcelUseCase:
    def __init__(self, flight_repository: FlightRepository, file_repository: FileProcessingControlRepository):
        self.flight_repository = flight_repository
        self.file_repository = file_repository
        self._total_rows = 0
        self._processed_rows = 0
        self._current_file = None

    def get_total_rows(self, file_path):
        if self._current_file != file_path:
            transformer = ExcelFlightTransformer(file_path)
            self._total_rows = transformer.get_total_rows()
            self._current_file = file_path
        return self._total_rows

    def get_processed_rows(self):
        return self._processed_rows

    def execute(self, file_path):
        try:
            self._current_file = file_path
            transformer = ExcelFlightTransformer(file_path)
            self._total_rows = transformer.get_total_rows()
            self._processed_rows = 0
            
            flights = transformer.transform_flights()
            create_flight_uc = CreateFlightUseCase(self.flight_repository)
            
            for flight_data in flights:
                try:
                    create_flight_uc.execute(flight_data)
                    self._processed_rows += 1
                except Exception as e:
                    print(f"Error al guardar el vuelo: {str(e)}")
                    raise
                    
            self.file_repository.add_file(file_path)
            return True
        except Exception as e:
            print(f"Error in execute method: {str(e)}")
            raise