from datetime import datetime
from typing import List, Optional
from src.core.ports.sector_capacity_repository import SectorCapacityRepository
from src.core.entities.sector_capacity import SectorCapacityResponse

class GetSectorCapacityUseCase:
    def __init__(self, repository: SectorCapacityRepository):
        self._repository = repository

    def get_sectors(self) -> List[str]:
        return self._repository.get_sectors()

    def execute(self, sector: str, date: datetime) -> Optional[SectorCapacityResponse]:
        if not isinstance(date, datetime):
            raise ValueError("La fecha debe ser un objeto datetime válido")
        return self._repository.get_sector_capacity(sector, date)