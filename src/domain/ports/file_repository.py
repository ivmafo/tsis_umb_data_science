from abc import ABC, abstractmethod
from typing import List, BinaryIO
from src.domain.entities.file_info import FileInfo

class FileRepository(ABC):
    @abstractmethod
    def list_files(self) -> List[FileInfo]:
        """List all available data files."""
        pass

    @abstractmethod
    def save_file(self, filename: str, content: BinaryIO) -> FileInfo:
        """Save a new file and validate it."""
        pass
