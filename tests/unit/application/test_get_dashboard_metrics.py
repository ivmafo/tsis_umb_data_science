"""Unit tests for GetDashboardMetrics use case."""
import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, Mock

from src.application.use_cases.get_dashboard_metrics import GetDashboardMetrics
from src.domain.entities.metric import Metric
from src.domain.value_objects.date_range import DateRange


@pytest.mark.asyncio
async def test_get_dashboard_metrics_all():
    """Test getting all metrics without filters."""
    # Arrange
    mock_metric_repo = AsyncMock()
    mock_data_source_repo = AsyncMock()
    
    sample_metrics = [
        Metric(
            metric_id="1",
            metric_name="test_metric",
            value=Decimal("100.50"),
            timestamp=datetime.now(),
            category="sales",
            source_file="test.csv"
        )
    ]
    
    mock_metric_repo.get_all_metrics.return_value = sample_metrics
    
    use_case = GetDashboardMetrics(
        metric_repository=mock_metric_repo,
        data_source_repository=mock_data_source_repo
    )
    
    # Act
    result = await use_case.execute()
    
    # Assert
    assert len(result) == 1
    assert result[0].metric_id == "1"
    mock_metric_repo.get_all_metrics.assert_called_once()


@pytest.mark.asyncio
async def test_get_dashboard_metrics_by_category():
    """Test getting metrics filtered by category."""
    # Arrange
    mock_metric_repo = AsyncMock()
    mock_data_source_repo = AsyncMock()
    
    sample_metrics = [
        Metric(
            metric_id="1",
            metric_name="test_metric",
            value=Decimal("100.50"),
            timestamp=datetime.now(),
            category="sales",
            source_file="test.csv"
        )
    ]
    
    mock_metric_repo.get_by_category.return_value = sample_metrics
    
    use_case = GetDashboardMetrics(
        metric_repository=mock_metric_repo,
        data_source_repository=mock_data_source_repo
    )
    
    # Act
    result = await use_case.execute(category="sales")
    
    # Assert
    assert len(result) == 1
    assert result[0].category == "sales"
    mock_metric_repo.get_by_category.assert_called_once_with("sales")


@pytest.mark.asyncio
async def test_get_summary_stats():
    """Test getting summary statistics."""
    # Arrange
    mock_metric_repo = AsyncMock()
    mock_data_source_repo = AsyncMock()
    
    now = datetime.now()
    sample_metrics = [
        Metric(
            metric_id="1",
            metric_name="metric1",
            value=Decimal("100"),
            timestamp=now,
            category="sales",
            source_file="test.csv"
        ),
        Metric(
            metric_id="2",
            metric_name="metric2",
            value=Decimal("200"),
            timestamp=now,
            category="marketing",
            source_file="test.csv"
        )
    ]
    
    mock_metric_repo.get_all_metrics.return_value = sample_metrics
    
    use_case = GetDashboardMetrics(
        metric_repository=mock_metric_repo,
        data_source_repository=mock_data_source_repo
    )
    
    # Act
    result = await use_case.get_summary_stats()
    
    # Assert
    assert result["total_metrics"] == 2
    assert len(result["categories"]) == 2
    assert "sales" in result["categories"]
    assert "marketing" in result["categories"]
