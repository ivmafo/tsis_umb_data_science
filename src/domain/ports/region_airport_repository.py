from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from src.domain.entities.region_airport import RegionAirport

class RegionAirportRepository(ABC):
    @abstractmethod
    def get_paginated(self, page: int, page_size: int, search: str = "") -> Tuple[List[RegionAirport], int]:
        pass

    @abstractmethod
    def create(self, region_airport: RegionAirport) -> RegionAirport:
        pass

    @abstractmethod
    def update(self, id: int, region_airport: RegionAirport) -> RegionAirport:
        pass

    @abstractmethod
    def delete(self, id: int) -> None:
        pass
