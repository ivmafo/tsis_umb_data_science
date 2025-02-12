from abc import ABC, abstractmethod
from tsis_umb_data_science.src.core.entities.flight import Flight

class FlightRepository(ABC):
    @abstractmethod
    def save(self, flight: Flight) -> Flight:
        pass

    @abstractmethod
    def find_by_id(self, flight_id: str) -> Flight | None:
        pass

    