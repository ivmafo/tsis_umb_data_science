from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.region import Region

class RegionRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Region]:
        pass

    @abstractmethod
    def get_by_id(self, region_id: int) -> Optional[Region]:
        pass

    @abstractmethod
    def create(self, region: Region) -> Region:
        pass

    @abstractmethod
    def update(self, region: Region) -> Optional[Region]:
        pass

    @abstractmethod
    def delete(self, region_id: int) -> bool:
        pass
