from abc import ABC, abstractmethod
from typing import Optional
from src.core.entities.flight import Flight


class FlightRepository(ABC):
    @abstractmethod
    def save(self, flight: Flight) -> Flight:
        pass

    @abstractmethod
    def find_by_id(self, flight_id: str) -> Optional[Flight]:
        pass

    def find_by_callsign(self, callsign: str) -> Optional[Flight]:
        pass

