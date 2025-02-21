from src.core.ports.flight_repository import FlightRepository
from src.core.ports.file_processing_control_repository import FileProcessingControlRepository
from src.core.ports.file_system_repository import FileSystemRepository
from src.core.use_cases.process_flights_from_excel import ProcessFlightsFromExcelUseCase
from typing import Dict, List, Any
import os

class ProcessDirectoryFlightsUseCase:
    def __init__(
        self, 
        flight_repository: FlightRepository,
        file_repository: FileProcessingControlRepository,
        file_system_repository: FileSystemRepository
    ):
        self._flight_repository = flight_repository
        self._file_repository = file_repository
        self._file_system_repository = file_system_repository
        self._process_flights_uc = ProcessFlightsFromExcelUseCase(flight_repository, file_repository)

    def _process_single_file(self, file_path: str) -> bool:
        """Process a single file and return success status"""
        if not self._file_repository.is_file_processed(file_path):
            self._process_flights_uc.execute(file_path)
            return True
        return False

    def execute(self, directory_path: str) -> Dict[str, List[Any]]:
        if not directory_path:
            raise ValueError("Directory path cannot be empty")

        processed_files = []
        errors = []

        try:
            copied_files = self._file_system_repository.copy_files_to_processing_directory(
                directory_path, 
                ('.xlsx', '.xls')
            )

            if not copied_files:
                return {
                    "processed_files": [],
                    "errors": [{"file": directory_path, "error": "No Excel files found in directory"}]
                }

            for file_path in copied_files:
                try:
                    if self._process_single_file(file_path):
                        processed_files.append(os.path.basename(file_path))
                except Exception as e:
                    errors.append({
                        "file": os.path.basename(file_path),
                        "error": str(e)
                    })

        except Exception as e:
            raise ValueError(f"Error processing directory: {str(e)}")

        return {
            "processed_files": processed_files,
            "errors": errors
        }
        