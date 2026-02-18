from typing import List, Tuple
from src.domain.entities.region_airport import RegionAirport
from src.domain.ports.region_airport_repository import RegionAirportRepository
from src.domain.ports.airport_repository import AirportRepository
from src.domain.ports.region_repository import RegionRepository

class ManageRegionAirports:
    def __init__(self, repository: RegionAirportRepository, airport_repository: AirportRepository, region_repository: RegionRepository):
        self.repository = repository
        self.airport_repository = airport_repository
        self.region_repository = region_repository

    def get_region_airports(self, page: int = 1, page_size: int = 10, search: str = "") -> Tuple[List[RegionAirport], int]:
        return self.repository.get_paginated(page, page_size, search)

    def create_region_airport(self, region_airport: RegionAirport) -> RegionAirport:
        # Validate existence
        airport = self.airport_repository.get_by_icao(region_airport.icao_code)
        if not airport:
            raise ValueError(f"El aeropuerto con código ICAO '{region_airport.icao_code}' no existe.")
            
        region = self.region_repository.get_by_id(region_airport.region_id)
        if not region:
            raise ValueError(f"La región con ID '{region_airport.region_id}' no existe.")

        return self.repository.create(region_airport)

    def update_region_airport(self, id: int, region_airport: RegionAirport) -> RegionAirport:
        # Validate existence
        airport = self.airport_repository.get_by_icao(region_airport.icao_code)
        if not airport:
            raise ValueError(f"El aeropuerto con código ICAO '{region_airport.icao_code}' no existe.")

        region = self.region_repository.get_by_id(region_airport.region_id)
        if not region:
            raise ValueError(f"La región con ID '{region_airport.region_id}' no existe.")

        return self.repository.update(id, region_airport)

    def delete_region_airport(self, id: int) -> None:
        self.repository.delete(id)
