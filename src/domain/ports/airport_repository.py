from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from src.domain.entities.airport import Airport

class AirportRepository(ABC):
    @abstractmethod
    def get_paginated(self, page: int, page_size: int, search: str = "") -> Tuple[List[Airport], int]:
        """Returns a tuple of (items, total_count)"""
        pass

    @abstractmethod
    def get_by_id(self, airport_id: int) -> Optional[Airport]:
        pass

    @abstractmethod
    def get_by_icao(self, icao_code: str) -> Optional[Airport]:
        pass

    @abstractmethod
    def create(self, airport: Airport) -> Airport:
        pass

    @abstractmethod
    def update(self, airport: Airport) -> Optional[Airport]:
        pass

    @abstractmethod
    def delete(self, airport_id: int) -> bool:
        pass
