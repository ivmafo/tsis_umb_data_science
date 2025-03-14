from src.core.ports.level_range_repository import LevelRangeRepository
from src.core.entities.level_range import LevelRange
from datetime import datetime

class CreateLevelRangeUseCase:
    def __init__(self, level_range_repository: LevelRangeRepository):
        self.level_range_repository = level_range_repository

    def execute(self, level_range_data: dict):
        level_range = LevelRange(
            origen=level_range_data['origen'],
            destino=level_range_data['destino'],
            nivel_min=level_range_data['nivel_min'],
            nivel_max=level_range_data['nivel_max'],
            ruta=level_range_data['ruta'],
            zona=level_range_data['zona']
        )
        return self.level_range_repository.save(level_range)

class UpdateLevelRangeUseCase:
    def __init__(self, level_range_repository: LevelRangeRepository):
        self.level_range_repository = level_range_repository

    def execute(self, id: int, level_range_data: dict) -> LevelRange:
        level_range = self.level_range_repository.find_by_id(id)
        if not level_range:
            raise ValueError(f"Level range with ID '{id}' not found")
        
        level_range.origen = level_range_data.get('origen', level_range.origen)
        level_range.destino = level_range_data.get('destino', level_range.destino)
        level_range.nivel_min = level_range_data.get('nivel_min', level_range.nivel_min)
        level_range.nivel_max = level_range_data.get('nivel_max', level_range.nivel_max)
        level_range.ruta = level_range_data.get('ruta', level_range.ruta)
        level_range.zona = level_range_data.get('zona', level_range.zona)
        
        return self.level_range_repository.update(level_range)

class GetLevelRangeUseCase:
    def __init__(self, level_range_repository: LevelRangeRepository):
        self.level_range_repository = level_range_repository

    def execute(self, id: int) -> LevelRange:
        level_range = self.level_range_repository.find_by_id(id)
        if not level_range:
            raise ValueError(f"Level range with ID '{id}' not found")
        return level_range

class GetLevelRangeByRouteUseCase:
    def __init__(self, level_range_repository: LevelRangeRepository):
        self.level_range_repository = level_range_repository

    def execute(self, origen: str, destino: str) -> LevelRange:
        level_range = self.level_range_repository.find_by_route(origen, destino)
        if not level_range:
            raise ValueError(f"Level range for route {origen}-{destino} not found")
        return level_range

class GetLevelRangesByZoneUseCase:
    def __init__(self, level_range_repository: LevelRangeRepository):
        self.level_range_repository = level_range_repository

    def execute(self, zona: str) -> list[LevelRange]:
        return self.level_range_repository.find_by_zone(zona)

class GetAllLevelRangesUseCase:
    def __init__(self, level_range_repository: LevelRangeRepository):
        self.level_range_repository = level_range_repository

    def execute(self):
        return self.level_range_repository.get_all()

class DeleteLevelRangeUseCase:
    def __init__(self, level_range_repository: LevelRangeRepository):
        self.level_range_repository = level_range_repository

    def execute(self, id: int) -> bool:
        return self.level_range_repository.delete_by_id(id)