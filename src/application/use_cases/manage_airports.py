from typing import List, Tuple, Optional
from src.domain.entities.airport import Airport
from src.domain.ports.airport_repository import AirportRepository

class ManageAirports:
    def __init__(self, repository: AirportRepository):
        self.repository = repository

    def get_airports(self, page: int = 1, page_size: int = 10, search: str = "") -> Tuple[List[Airport], int]:
        return self.repository.get_paginated(page, page_size, search)

    def get_airport(self, airport_id: int) -> Optional[Airport]:
        return self.repository.get_by_id(airport_id)

    def create_airport(self, data: dict) -> Airport:
        airport = Airport(**data)
        return self.repository.create(airport)

    def update_airport(self, airport_id: int, data: dict) -> Optional[Airport]:
        curr = self.repository.get_by_id(airport_id)
        if not curr:
            return None
        
        # Update fields
        updated = curr.model_copy(update=data)
        updated.id = airport_id # Ensure ID is preserved
        return self.repository.update(updated)

    def delete_airport(self, airport_id: int) -> bool:
        if not self.repository.get_by_id(airport_id):
            return False
        return self.repository.delete(airport_id)
