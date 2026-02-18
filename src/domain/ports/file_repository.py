from abc import ABC, abstractmethod
from typing import List, BinaryIO
from src.domain.entities.file_info import FileInfo

class FileRepository(ABC):
    """
    Interface para el manejo de archivos físicos y control de ingesta.
    """
    @abstractmethod
    def list_files(self) -> List[FileInfo]:
        """Lista todos los archivos de datos disponibles en el almacenamiento."""
        pass

    @abstractmethod
    def save_file(self, filename: str, content: BinaryIO) -> FileInfo:
        """Guarda un nuevo archivo en el sistema y retorna su estado de validación inicial."""
        pass
