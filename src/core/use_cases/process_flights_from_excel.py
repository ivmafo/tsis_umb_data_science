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
        self.update_progress = None

    def get_total_rows(self, file_path):
        try:
            transformer = ExcelFlightTransformer(file_path)
            total = transformer.get_total_rows()
            print(f"Total rows to process: {total}")
            return total
        except Exception as e:
            print(f"Error getting total rows: {str(e)}")
            raise

    def execute(self, file_path):
        try:
            if self.file_repository.is_file_processed(file_path):
                print(f"File {file_path} already processed")
                return {"processed": 0, "total": 0, "status": "already_processed"}

            transformer = ExcelFlightTransformer(file_path)
            flights = transformer.transform_flights()
            create_flight_uc = CreateFlightUseCase(self.flight_repository)
            
            total_flights = len(flights)
            processed = 0

            for flight_data in flights:
                try:
                    create_flight_uc.execute(flight_data)
                    processed += 1
                    if self.update_progress:
                        self.update_progress(processed)
                    #rint(f"Processed {processed}/{total_flights} flights")
                except Exception as e:
                    print(f"Error processing flight: {str(e)}")
                    raise

            self.file_repository.add_file(file_path)
            return {"processed": processed, "total": total_flights, "status": "completed"}

        except Exception as e:
            print(f"Error in execute method: {str(e)}")
            raise




