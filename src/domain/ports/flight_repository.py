from abc import ABC, abstractmethod
from domain.entities.flight import Flight

class FlightRepository(ABC):
    @abstractmethod
    def save(self, flight: Flight) -> Flight:
        pass

    @abstractmethod
    def find_by_id(self, flight_id: str) -> Flight | None:
        pass