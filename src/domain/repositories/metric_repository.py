"""MetricRepository interface (Port)."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from ..value_objects.date_range import DateRange


class MetricRepository(ABC):
    """
    Abstract repository interface for Metric persistence.
    """
    
    @abstractmethod
    async def save_metrics(self, metrics: List[Dict[str, Any]]) -> None:
        """
        Persist a list of metrics.
        """
        pass
    
    @abstractmethod
    async def get_all_metrics(self) -> List[Dict[str, Any]]:
        """
        Retrieve all metrics from storage.
        """
        pass
    
    @abstractmethod
    async def get_by_date_range(self, date_range: DateRange) -> List[Dict[str, Any]]:
        """
        Retrieve metrics within a specific date range.
        """
        pass
    
    @abstractmethod
    async def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Retrieve metrics by category.
        """
        pass
    
    @abstractmethod
    async def delete_all(self) -> None:
        """
        Delete all metrics.
        """
        pass
