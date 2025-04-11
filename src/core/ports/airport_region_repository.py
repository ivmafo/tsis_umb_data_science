from abc import ABC, abstractmethod
from typing import List, Optional
from src.core.entities.airport_region import AirportRegion

class AirportRegionRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[AirportRegion]:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[AirportRegion]:
        pass

    @abstractmethod
    def get_by_icao(self, icao_code: str) -> List[AirportRegion]:
        pass

    @abstractmethod
    def create(self, airport_region_data: dict) -> AirportRegion:
        pass

    @abstractmethod
    def update(self, id: int, airport_region_data: dict) -> Optional[AirportRegion]:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass