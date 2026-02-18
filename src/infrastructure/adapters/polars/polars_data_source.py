"""Polars Data Source Adapter - Implements DataSourceRepository using Polars."""
import polars as pl
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import uuid

from ....domain.repositories.data_source_repository import DataSourceRepository


class DataSourceError(Exception):
    """Exception raised for data source errors."""
    pass


class PolarsDataSource(DataSourceRepository):
    """
    Concrete implementation of DataSourceRepository using Polars.
    """
    
    def __init__(self, config=None):
        self._config = config
    
    async def read_files(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        try:
            all_metrics = []
            
            for file_path in file_paths:
                if file_path.suffix.lower() == '.parquet':
                    lazy_df = pl.scan_parquet(str(file_path))
                elif file_path.suffix.lower() == '.csv':
                    lazy_df = pl.scan_csv(str(file_path))
                else:
                    raise DataSourceError(f"Unsupported file type: {file_path.suffix}")
                
                df = lazy_df.collect()
                
                for row in df.iter_rows(named=True):
                    # Simply return dict
                    all_metrics.append(row)
            
            return all_metrics
            
        except Exception as e:
            raise DataSourceError(f"Failed to read files: {str(e)}") from e
    
    async def aggregate_metrics(
        self,
        file_paths: List[Path],
        group_by: List[str]
    ) -> List[Dict[str, Any]]:
        try:
            csv_files = [f for f in file_paths if f.suffix.lower() == '.csv']
            parquet_files = [f for f in file_paths if f.suffix.lower() == '.parquet']
            
            lazy_frames = []
            
            if csv_files:
                csv_paths = [str(f) for f in csv_files]
                lazy_frames.append(pl.scan_csv(csv_paths))
            
            if parquet_files:
                parquet_paths = [str(f) for f in parquet_files]
                lazy_frames.append(pl.scan_parquet(parquet_paths))
            
            if not lazy_frames:
                return []
            
            if len(lazy_frames) > 1:
                combined = pl.concat(lazy_frames)
            else:
                combined = lazy_frames[0]
            
            aggregated = (
                combined
                .group_by(group_by + ["category"])
                .agg([
                    pl.col("value").sum().alias("total_value"),
                    pl.col("value").mean().alias("avg_value"),
                    pl.col("value").count().alias("count"),
                    pl.col("timestamp").max().alias("latest_timestamp")
                ])
                .collect()
            )
            
            return aggregated.to_dicts()
            
        except Exception as e:
            raise DataSourceError(f"Failed to aggregate metrics: {str(e)}") from e
    
    async def get_file_stats(self, file_path: Path) -> dict:
        try:
            if file_path.suffix.lower() == '.parquet':
                lazy_df = pl.scan_parquet(str(file_path))
            elif file_path.suffix.lower() == '.csv':
                lazy_df = pl.scan_csv(str(file_path))
            else:
                raise DataSourceError(f"Unsupported file type: {file_path.suffix}")
            
            schema = lazy_df.collect_schema()
            row_count = lazy_df.select(pl.len()).collect().item()
            file_size = file_path.stat().st_size
            
            return {
                "row_count": row_count,
                "column_count": len(schema),
                "columns": list(schema.names()),
                "file_size_bytes": file_size,
                "file_size_mb": round(file_size / (1024 * 1024), 2),
                "file_type": file_path.suffix.lower()
            }
            
        except Exception as e:
            raise DataSourceError(f"Failed to get file stats: {str(e)}") from e
