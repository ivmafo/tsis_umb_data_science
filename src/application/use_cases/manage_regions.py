from typing import List, Optional
from src.domain.entities.region import Region
from src.domain.ports.region_repository import RegionRepository

class ManageRegions:
    def __init__(self, repository: RegionRepository):
        self.repository = repository

    def list_regions(self) -> List[Region]:
        return self.repository.get_all()

    def get_region(self, region_id: int) -> Optional[Region]:
        return self.repository.get_by_id(region_id)

    def create_region(self, region_data: dict) -> Region:
        region = Region(
            name=region_data['name'],
            code=region_data['code'],
            description=region_data.get('description', ''),
            nivel_min=region_data.get('nivel_min', 0)
        )
        return self.repository.create(region)

    def update_region(self, region_id: int, region_data: dict) -> Optional[Region]:
        region = self.repository.get_by_id(region_id)
        if not region:
            return None
        
        region.name = region_data.get('name', region.name)
        region.code = region_data.get('code', region.code)
        region.description = region_data.get('description', region.description)
        region.nivel_min = region_data.get('nivel_min', region.nivel_min)
        
        return self.repository.update(region)

    def delete_region(self, region_id: int) -> bool:
        return self.repository.delete(region_id)
