from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime

class FileProcessingControlRepository(ABC):
    @abstractmethod
    def add_file(self, file_name: str) -> None:
        pass

    @abstractmethod
    def is_file_processed(self, file_name: str) -> bool:
        pass
