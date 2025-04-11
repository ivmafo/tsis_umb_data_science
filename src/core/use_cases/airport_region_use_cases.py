from typing import List, Optional
from src.core.entities.airport_region import AirportRegion
from src.core.ports.airport_region_repository import AirportRegionRepository

class GetAllAirportRegionsUseCase:
    def __init__(self, airport_region_repository: AirportRegionRepository):
        self.airport_region_repository = airport_region_repository

    def execute(self) -> List[AirportRegion]:
        return self.airport_region_repository.get_all()

class GetAirportRegionByIdUseCase:
    def __init__(self, airport_region_repository: AirportRegionRepository):
        self.airport_region_repository = airport_region_repository

    def execute(self, id: int) -> Optional[AirportRegion]:
        return self.airport_region_repository.get_by_id(id)

class GetAirportRegionsByIcaoUseCase:
    def __init__(self, airport_region_repository: AirportRegionRepository):
        self.airport_region_repository = airport_region_repository

    def execute(self, icao_code: str) -> List[AirportRegion]:
        return self.airport_region_repository.get_by_icao(icao_code)

class CreateAirportRegionUseCase:
    def __init__(self, airport_region_repository: AirportRegionRepository):
        self.airport_region_repository = airport_region_repository

    def execute(self, airport_region_data: dict) -> AirportRegion:
        return self.airport_region_repository.create(airport_region_data)

class UpdateAirportRegionUseCase:
    def __init__(self, airport_region_repository: AirportRegionRepository):
        self.airport_region_repository = airport_region_repository

    def execute(self, id: int, airport_region_data: dict) -> Optional[AirportRegion]:
        return self.airport_region_repository.update(id, airport_region_data)

class DeleteAirportRegionUseCase:
    def __init__(self, airport_region_repository: AirportRegionRepository):
        self.airport_region_repository = airport_region_repository

    def execute(self, id: int) -> bool:
        return self.airport_region_repository.delete(id)