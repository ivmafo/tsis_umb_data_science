from src.core.ports.level_range_repository import LevelRangeRepository
from src.core.entities.level_range import LevelRange
from datetime import datetime

class CreateLevelRangeUseCase:
    def __init__(self, level_range_repository: LevelRangeRepository):
        self.level_range_repository = level_range_repository

    def execute(self, level_range_data: dict):
        level_range = LevelRange(
            min_level=level_range_data['min_level'],
            max_level=level_range_data['max_level'],
            alias=level_range_data['alias']
        )
        return self.level_range_repository.save(level_range)

class UpdateLevelRangeUseCase:
    def __init__(self, level_range_repository: LevelRangeRepository):
        self.level_range_repository = level_range_repository

    def execute(self, id: int, level_range_data: dict) -> LevelRange:
        level_range = self.level_range_repository.find_by_id(id)
        if not level_range:
            raise ValueError(f"Rango de nivel con ID '{id}' no encontrado")
        
        level_range.min_level = level_range_data['min_level']
        level_range.max_level = level_range_data['max_level']
        level_range.alias = level_range_data['alias']
        return self.level_range_repository.update(level_range)

class GetLevelRangeUseCase:
    def __init__(self, level_range_repository: LevelRangeRepository):
        self.level_range_repository = level_range_repository

    def execute(self, id: int) -> LevelRange:
        level_range = self.level_range_repository.find_by_id(id)
        if not level_range:
            raise ValueError(f"Rango de nivel con ID '{id}' no encontrado")
        return level_range

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