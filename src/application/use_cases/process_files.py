"""ProcessFiles use case."""
from pathlib import Path
from typing import List

from ...domain.repositories.metric_repository import MetricRepository
from ...domain.repositories.data_source_repository import DataSourceRepository
from ...domain.entities.metric import Metric


class ProcessFiles:
    """
    Use case for processing data files and persisting metrics.
    
    This use case coordinates reading files (potentially 100+ files),
    aggregating metrics, and persisting them for later retrieval.
    """
    
    def __init__(
        self,
        metric_repository: MetricRepository,
        data_source_repository: DataSourceRepository
    ):
        """
        Initialize use case with dependencies.
        
        Args:
            metric_repository: Repository for persisting metrics
            data_source_repository: Repository for reading data files
        """
        self._metric_repo = metric_repository
        self._data_source_repo = data_source_repository
    
    async def execute(
        self,
        file_paths: List[Path],
        group_by: List[str] = None,
        clear_existing: bool = False
    ) -> int:
        """
        Process files and persist aggregated metrics.
        
        Args:
            file_paths: List of file paths to process
            group_by: Optional list of columns to group by for aggregation
            clear_existing: If True, clear existing metrics before saving new ones
            
        Returns:
            Number of metrics processed and saved
        """
        # Clear existing metrics if requested
        if clear_existing:
            await self._metric_repo.delete_all()
        
        # Process files using the data source repository
        # This will use Polars lazy evaluation and streaming
        if group_by:
            metrics = await self._data_source_repo.aggregate_metrics(
                file_paths=file_paths,
                group_by=group_by
            )
        else:
            metrics = await self._data_source_repo.read_files(file_paths)
        
        # Persist metrics
        await self._metric_repo.save_metrics(metrics)
        
        return len(metrics)
    
    async def get_file_info(self, file_paths: List[Path]) -> List[dict]:
        """
        Get information about files without processing them.
        
        Args:
            file_paths: List of file paths to inspect
            
        Returns:
            List of dictionaries with file statistics
        """
        file_stats = []
        for file_path in file_paths:
            stats = await self._data_source_repo.get_file_stats(file_path)
            file_stats.append({
                "file_path": str(file_path),
                **stats
            })
        return file_stats
