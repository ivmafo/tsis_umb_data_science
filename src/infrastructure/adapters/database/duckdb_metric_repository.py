"""DuckDB Metric Repository - Implements MetricRepository using DuckDB."""
import duckdb
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from decimal import Decimal

from ....domain.repositories.metric_repository import MetricRepository
from ....domain.value_objects.date_range import DateRange


class RepositoryError(Exception):
    """Exception raised for repository errors."""
    pass


class DuckDBMetricRepository(MetricRepository):
    """
    Concrete implementation of MetricRepository using DuckDB.
    """
    
    def __init__(self, database_path: str = "metrics.duckdb"):
        self._db_path = database_path
        self._ensure_table_exists()
    
    def _get_connection(self):
        """Get a DuckDB connection."""
        return duckdb.connect(self._db_path)
    
    def _ensure_table_exists(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    metric_id VARCHAR PRIMARY KEY,
                    metric_name VARCHAR NOT NULL,
                    value DECIMAL(18, 4) NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    category VARCHAR NOT NULL,
                    source_file VARCHAR NOT NULL,
                    metadata JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp 
                ON metrics(timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_category 
                ON metrics(category)
            """)
    
    async def save_metrics(self, metrics: List[Dict[str, Any]]) -> None:
        try:
            with self._get_connection() as conn:
                data = [
                    (
                        str(m.get('metric_id', '')),
                        str(m.get('metric_name', '')),
                        float(m.get('value', 0)),
                        m.get('timestamp', datetime.now()),
                        str(m.get('category', '')),
                        str(m.get('source_file', '')),
                        str(m.get('metadata')) if m.get('metadata') else None
                    )
                    for m in metrics
                ]
                
                conn.executemany("""
                    INSERT OR REPLACE INTO metrics 
                    (metric_id, metric_name, value, timestamp, category, source_file, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, data)
                
        except Exception as e:
            raise RepositoryError(f"Failed to save metrics: {str(e)}") from e
    
    async def get_all_metrics(self) -> List[Dict[str, Any]]:
        try:
            with self._get_connection() as conn:
                result = conn.execute("""
                    SELECT metric_id, metric_name, value, timestamp, 
                           category, source_file, metadata
                    FROM metrics
                    ORDER BY timestamp DESC
                """).fetchall()
                
                return [self._row_to_metric(row) for row in result]
                
        except Exception as e:
            raise RepositoryError(f"Failed to retrieve metrics: {str(e)}") from e
    
    async def get_by_date_range(self, date_range: DateRange) -> List[Dict[str, Any]]:
        try:
            with self._get_connection() as conn:
                result = conn.execute("""
                    SELECT metric_id, metric_name, value, timestamp, 
                           category, source_file, metadata
                    FROM metrics
                    WHERE timestamp BETWEEN ? AND ?
                    ORDER BY timestamp DESC
                """, [date_range.start_date, date_range.end_date]).fetchall()
                
                return [self._row_to_metric(row) for row in result]
                
        except Exception as e:
            raise RepositoryError(f"Failed to retrieve metrics by date range: {str(e)}") from e
    
    async def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        try:
            with self._get_connection() as conn:
                result = conn.execute("""
                    SELECT metric_id, metric_name, value, timestamp, 
                           category, source_file, metadata
                    FROM metrics
                    WHERE category = ?
                    ORDER BY timestamp DESC
                """, [category]).fetchall()
                
                return [self._row_to_metric(row) for row in result]
                
        except Exception as e:
            raise RepositoryError(f"Failed to retrieve metrics by category: {str(e)}") from e
    
    async def delete_all(self) -> None:
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM metrics")
        except Exception as e:
            raise RepositoryError(f"Failed to delete metrics: {str(e)}") from e
    
    def _row_to_metric(self, row: tuple) -> Dict[str, Any]:
        return {
            'metric_id': row[0],
            'metric_name': row[1],
            'value': Decimal(str(row[2])),
            'timestamp': row[3],
            'category': row[4],
            'source_file': row[5],
            'metadata': eval(row[6]) if row[6] else None
        }
