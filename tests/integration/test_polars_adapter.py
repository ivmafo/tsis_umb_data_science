"""Integration tests for Polars adapter."""
import pytest
import polars as pl
from pathlib import Path
from datetime import datetime
from decimal import Decimal

from src.infrastructure.adapters.polars.polars_data_source import PolarsDataSource


@pytest.mark.asyncio
async def test_polars_read_csv_file(sample_data_dir):
    """Test reading a CSV file with Polars adapter."""
    # Arrange
    csv_file = sample_data_dir / "test.csv"
    
    # Create sample CSV
    df = pl.DataFrame({
        "id": ["1", "2"],
        "metric_name": ["metric1", "metric2"],
        "value": [100.0, 200.0],
        "timestamp": [datetime.now(), datetime.now()],
        "category": ["sales", "marketing"]
    })
    df.write_csv(csv_file)
    
    adapter = PolarsDataSource()
    
    # Act
    metrics = await adapter.read_files([csv_file])
    
    # Assert
    assert len(metrics) == 2
    assert metrics[0].metric_name == "metric1"
    assert metrics[1].metric_name == "metric2"


@pytest.mark.asyncio
async def test_polars_get_file_stats(sample_data_dir):
    """Test getting file statistics."""
    # Arrange
    csv_file = sample_data_dir / "test.csv"
    
    df = pl.DataFrame({
        "id": ["1", "2", "3"],
        "value": [100.0, 200.0, 300.0]
    })
    df.write_csv(csv_file)
    
    adapter = PolarsDataSource()
    
    # Act
    stats = await adapter.get_file_stats(csv_file)
    
    # Assert
    assert stats["row_count"] == 3
    assert stats["column_count"] == 2
    assert "id" in stats["columns"]
    assert "value" in stats["columns"]
