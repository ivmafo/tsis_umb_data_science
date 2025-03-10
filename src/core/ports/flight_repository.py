# src\core\ports\flight_repository.py
from abc import ABC, abstractmethod
from typing import Optional, List
from src.core.entities.flight import Flight
from src.core.dtos.flight_dtos import FlightFilterDTO, FlightOriginCountDTO


class FlightRepository(ABC):
    @abstractmethod
    def save(self, flight: Flight) -> Flight:
        pass

    @abstractmethod
    def find_by_id(self, flight_id: str) -> Optional[Flight]:
        pass

    def find_by_callsign(self, callsign: str) -> Optional[Flight]:
        pass

    @abstractmethod
    def get_origins_count(self, filters: FlightFilterDTO) -> List[FlightOriginCountDTO]:
        pass

