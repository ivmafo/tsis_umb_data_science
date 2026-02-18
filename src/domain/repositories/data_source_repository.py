"""DataSourceRepository interface (Port)."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any


class DataSourceRepository(ABC):
    """
    Abstract repository interface for reading and processing data files.
    """
    
    @abstractmethod
    async def read_files(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """
        Read and parse data files.
        """
        pass
    
    @abstractmethod
    async def aggregate_metrics(
        self, 
        file_paths: List[Path],
        group_by: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Read files and compute aggregated metrics.
        """
        pass
    
    @abstractmethod
    async def get_file_stats(self, file_path: Path) -> dict:
        """
        Get statistics about a data file.
        """
        pass
