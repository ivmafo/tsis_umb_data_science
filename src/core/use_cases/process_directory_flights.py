"""
Módulo que implementa el caso de uso para procesar vuelos desde un directorio,
siguiendo los principios de arquitectura hexagonal y clean architecture.

Este módulo contiene la lógica de negocio para procesar archivos Excel con
información de vuelos desde un directorio específico, manteniendo la independencia
de los detalles de implementación.
"""

from src.core.ports.flight_repository import FlightRepository
from src.core.ports.file_processing_control_repository import FileProcessingControlRepository
from src.core.ports.file_system_repository import FileSystemRepository
from src.core.use_cases.process_flights_from_excel import ProcessFlightsFromExcelUseCase
from typing import Dict, List, Any
import os

class ProcessDirectoryFlightsUseCase:
    """
    Caso de uso para procesar archivos de vuelos desde un directorio.

    Esta clase implementa la lógica de negocio para procesar múltiples archivos
    Excel que contienen información de vuelos, siguiendo el principio de
    responsabilidad única y manteniendo la independencia de la infraestructura.

    Attributes:
        _flight_repository (FlightRepository): Repositorio de vuelos
        _file_repository (FileProcessingControlRepository): Repositorio de control de archivos
        _file_system_repository (FileSystemRepository): Repositorio del sistema de archivos
        _process_flights_uc (ProcessFlightsFromExcelUseCase): Caso de uso para procesar Excel
    """

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
        """
        Procesa un único archivo Excel.

        Args:
            file_path (str): Ruta del archivo a procesar

        Returns:
            bool: True si el archivo fue procesado, False si ya estaba procesado
        """
        if not self._file_repository.is_file_processed(file_path):
            self._process_flights_uc.execute(file_path)
            return True
        return False

    def execute(self, directory_path: str) -> Dict[str, List[Any]]:
        """
        Ejecuta el procesamiento de todos los archivos Excel en un directorio.

        Este método implementa la lógica principal del caso de uso, procesando
        todos los archivos Excel encontrados en el directorio especificado y
        manteniendo un registro de éxitos y errores.

        Args:
            directory_path (str): Ruta del directorio a procesar

        Returns:
            Dict[str, List[Any]]: Diccionario con archivos procesados y errores

        Raises:
            ValueError: Si la ruta del directorio está vacía o hay error en el procesamiento
        """
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
        