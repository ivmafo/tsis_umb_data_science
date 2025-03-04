from src.core.ports.config_repository import ConfigRepository
from src.core.entities.config import Config
from datetime import datetime

class CreateConfigUseCase:
    def __init__(self, config_repository):
        self.config_repository = config_repository

    def execute(self, config_data: dict):
        config = Config(
            key=config_data['key'],
            value=config_data['value']
        )
        return self.config_repository.save(config)

class UpdateConfigUseCase:
    def __init__(self, config_repository: ConfigRepository):
        self.config_repository = config_repository

    def execute(self, key: str, new_value: str) -> Config:
        config = self.config_repository.find_by_key(key)
        if not config:
            raise ValueError(f"Configuración con clave '{key}' no encontrada")
        
        config.value = new_value
        return self.config_repository.update(config)

class GetConfigUseCase:
    def __init__(self, config_repository: ConfigRepository):
        self.config_repository = config_repository

    def execute(self, key: str) -> Config:
        config = self.config_repository.find_by_key(key)
        if not config:
            raise ValueError(f"Configuración con clave '{key}' no encontrada")
        return config

class GetAllConfigsUseCase:
    def __init__(self, config_repository: ConfigRepository):
        self.config_repository = config_repository

    def execute(self):
        return self.config_repository.get_all()
class DeleteConfigUseCase:
    def __init__(self, config_repository: ConfigRepository):
        self.config_repository = config_repository

    def execute(self, key: str) -> bool:
        return self.config_repository.delete_by_key(key)