from typing import List, Optional
from src.core.entities.region import Region
from src.core.ports.region_repository import RegionRepository

class GetAllRegionsUseCase:
    def __init__(self, region_repository: RegionRepository):
        self.region_repository = region_repository

    def execute(self) -> List[Region]:
        return self.region_repository.get_all()

class GetRegionByIdUseCase:
    def __init__(self, region_repository: RegionRepository):
        self.region_repository = region_repository

    def execute(self, id: int) -> Optional[Region]:
        return self.region_repository.get_by_id(id)

class CreateRegionUseCase:
    def __init__(self, region_repository: RegionRepository):
        self.region_repository = region_repository

    def execute(self, region_data: dict) -> Region:
        return self.region_repository.create(region_data)

class UpdateRegionUseCase:
    def __init__(self, region_repository: RegionRepository):
        self.region_repository = region_repository

    def execute(self, id: int, region_data: dict) -> Optional[Region]:
        return self.region_repository.update(id, region_data)

class DeleteRegionUseCase:
    def __init__(self, region_repository: RegionRepository):
        self.region_repository = region_repository

    def execute(self, id: int) -> bool:
        return self.region_repository.delete(id)