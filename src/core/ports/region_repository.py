from abc import ABC, abstractmethod
from typing import List, Optional
from src.core.entities.region import Region

class RegionRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Region]:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Region]:
        pass

    @abstractmethod
    def create(self, region_data: dict) -> Region:
        pass

    @abstractmethod
    def update(self, id: int, region_data: dict) -> Optional[Region]:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass