from abc import ABC, abstractmethod
from typing import List

class FileSystemRepository(ABC):
    @abstractmethod
    def copy_files_to_processing_directory(self, source_dir: str, file_types: tuple) -> List[str]:
        pass

    @abstractmethod
    def get_processing_directory(self) -> str:
        pass