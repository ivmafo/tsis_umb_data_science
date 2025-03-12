from abc import ABC, abstractmethod
from typing import Optional, List
from src.core.entities.level_range import LevelRange

class LevelRangeRepository(ABC):
    @abstractmethod
    def save(self, level_range: LevelRange) -> LevelRange:
        pass

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[LevelRange]:
        pass

    @abstractmethod
    def get_all(self) -> List[LevelRange]:
        pass

    @abstractmethod
    def update(self, level_range: LevelRange) -> LevelRange:
        pass

    @abstractmethod
    def delete_by_id(self, id: int) -> bool:
        pass