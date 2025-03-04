# src\core\ports\config_repository.py
from abc import ABC, abstractmethod
from typing import Optional, List
from src.core.entities.config import Config

class ConfigRepository(ABC):
    @abstractmethod
    def save(self, config: Config) -> Config:
        pass

    @abstractmethod
    def find_by_key(self, key: str) -> Optional[Config]:
        pass

    @abstractmethod
    def get_all(self) -> List[Config]:
        pass

    @abstractmethod
    def update(self, config: Config) -> Config:
        pass

    @abstractmethod
    def delete_by_key(self, key: str) -> bool:
        pass