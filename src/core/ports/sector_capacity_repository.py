from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from src.core.entities.sector_capacity import SectorCapacityResponse

class SectorCapacityRepository(ABC):
    @abstractmethod
    def get_sectors(self) -> List[str]:
        pass

    @abstractmethod
    def get_sector_capacity(self, sector: str, date: datetime) -> Optional[SectorCapacityResponse]:
        pass