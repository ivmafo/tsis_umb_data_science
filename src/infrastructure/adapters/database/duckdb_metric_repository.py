"""Repositorio de Métricas en DuckDB - Implementa MetricRepository utilizando DuckDB."""
import duckdb
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from decimal import Decimal

from ....domain.repositories.metric_repository import MetricRepository
from ....domain.value_objects.date_range import DateRange


class RepositoryError(Exception):
    """Excepción lanzada para errores específicos del repositorio."""
    pass


class DuckDBMetricRepository(MetricRepository):
    """
    Implementación concreta de MetricRepository utilizando DuckDB.
    
    Esta clase gestiona la persistencia de métricas calculadas en una base de datos
    analítica embebida, permitiendo consultas rápidas sobre grandes volúmenes de datos.
    """
    
    def __init__(self, database_path: str = "metrics.duckdb"):
        """
        Inicializa el repositorio y asegura que la estructura de tablas exista.
        
        Args:
            database_path: Ruta al archivo de base de datos DuckDB.
        """
        self._db_path = database_path
        self._ensure_table_exists()
    
    def _get_connection(self):
        """Obtiene una conexión activa a DuckDB."""
        return duckdb.connect(self._db_path)
    
    def _ensure_table_exists(self):
        """
        Crea la tabla de métricas e índices si no existen en la base de datos.
        """
        with self._get_connection() as conn:
            # Creación de la tabla principal de métricas
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
            # Índices para optimizar búsquedas temporales y por categoría
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp 
                ON metrics(timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_category 
                ON metrics(category)
            """)
    
    async def save_metrics(self, metrics: List[Dict[str, Any]]) -> None:
        """
        Guarda o reemplaza una lista de métricas en la base de datos.
        """
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
            raise RepositoryError(f"Error al guardar métricas: {str(e)}") from e
    
    async def get_all_metrics(self) -> List[Dict[str, Any]]:
        """Recupera todas las métricas ordenadas por fecha descendente."""
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
            raise RepositoryError(f"Error al recuperar métricas: {str(e)}") from e
    
    async def get_by_date_range(self, date_range: DateRange) -> List[Dict[str, Any]]:
        """Recupera métricas dentro de un rango de fechas específico."""
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
            raise RepositoryError(f"Error al recuperar métricas por rango: {str(e)}") from e
    
    async def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Recupera métricas filtradas por una categoría específica."""
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
            raise RepositoryError(f"Error al recuperar métricas por categoría: {str(e)}") from e
    
    async def delete_all(self) -> None:
        """Limpia completamente la tabla de métricas."""
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM metrics")
        except Exception as e:
            raise RepositoryError(f"Error al eliminar métricas: {str(e)}") from e
    
    def _row_to_metric(self, row: tuple) -> Dict[str, Any]:
        """Convierte una fila de la base de datos a un diccionario de métrica."""
        return {
            'metric_id': row[0],
            'metric_name': row[1],
            'value': Decimal(str(row[2])),
            'timestamp': row[3],
            'category': row[4],
            'source_file': row[5],
            'metadata': eval(row[6]) if row[6] else None
        }
