#src\core\ports\file_processing_control_repository.py
from abc import ABC, abstractmethod

class FileProcessingControlRepository(ABC):
    @abstractmethod
    def add_file(self, file_name: str) -> None:
        pass

    @abstractmethod
    def is_file_processed(self, file_name: str) -> bool:
        pass

