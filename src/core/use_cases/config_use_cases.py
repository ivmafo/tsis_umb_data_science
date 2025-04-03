"""
Módulo que implementa los casos de uso relacionados con la configuración del sistema,
siguiendo los principios de arquitectura hexagonal y clean architecture.

Este módulo contiene los casos de uso que definen las operaciones de negocio
para la gestión de configuraciones, manteniendo la lógica de negocio independiente
de los detalles de implementación.
"""

from src.core.ports.config_repository import ConfigRepository
from src.core.entities.config import Config
from datetime import datetime

class CreateConfigUseCase:
    """
    Caso de uso para crear una nueva configuración en el sistema.

    Esta clase implementa la lógica de negocio para crear nuevas configuraciones,
    siguiendo el principio de responsabilidad única.

    Attributes:
        config_repository (ConfigRepository): Repositorio de configuraciones
    """

    def __init__(self, config_repository):
        self.config_repository = config_repository

    def execute(self, config_data: dict):
        """
        Ejecuta la creación de una nueva configuración.

        Args:
            config_data (dict): Diccionario con los datos de la configuración

        Returns:
            Config: Configuración creada y almacenada
        """
        config = Config(
            key=config_data['key'],
            value=config_data['value']
        )
        return self.config_repository.save(config)

class UpdateConfigUseCase:
    """
    Caso de uso para actualizar una configuración existente.

    Esta clase maneja la lógica de actualización de configuraciones,
    validando la existencia de la configuración antes de actualizarla.

    Attributes:
        config_repository (ConfigRepository): Repositorio de configuraciones
    """

    def __init__(self, config_repository: ConfigRepository):
        self.config_repository = config_repository

    def execute(self, key: str, new_value: str) -> Config:
        """
        Ejecuta la actualización de una configuración.

        Args:
            key (str): Clave de la configuración a actualizar
            new_value (str): Nuevo valor para la configuración

        Returns:
            Config: Configuración actualizada

        Raises:
            ValueError: Si la configuración no existe
        """
        config = self.config_repository.find_by_key(key)
        if not config:
            raise ValueError(f"Configuración con clave '{key}' no encontrada")
        
        config.value = new_value
        return self.config_repository.update(config)

class GetConfigUseCase:
    """
    Caso de uso para obtener una configuración específica.

    Esta clase implementa la lógica para recuperar una configuración
    específica del sistema.

    Attributes:
        config_repository (ConfigRepository): Repositorio de configuraciones
    """

    def __init__(self, config_repository: ConfigRepository):
        self.config_repository = config_repository

    def execute(self, key: str) -> Config:
        """
        Ejecuta la búsqueda de una configuración.

        Args:
            key (str): Clave de la configuración a buscar

        Returns:
            Config: Configuración encontrada

        Raises:
            ValueError: Si la configuración no existe
        """
        config = self.config_repository.find_by_key(key)
        if not config:
            raise ValueError(f"Configuración con clave '{key}' no encontrada")
        return config

class GetAllConfigsUseCase:
    """
    Caso de uso para obtener todas las configuraciones del sistema.

    Esta clase implementa la lógica para recuperar todas las
    configuraciones almacenadas.

    Attributes:
        config_repository (ConfigRepository): Repositorio de configuraciones
    """

    def __init__(self, config_repository: ConfigRepository):
        self.config_repository = config_repository

    def execute(self):
        """
        Ejecuta la obtención de todas las configuraciones.

        Returns:
            List[Config]: Lista de todas las configuraciones
        """
        return self.config_repository.get_all()

class DeleteConfigUseCase:
    """
    Caso de uso para eliminar una configuración del sistema.

    Esta clase implementa la lógica para eliminar una configuración
    específica del sistema.

    Attributes:
        config_repository (ConfigRepository): Repositorio de configuraciones
    """

    def __init__(self, config_repository: ConfigRepository):
        self.config_repository = config_repository

    def execute(self, key: str) -> bool:
        """
        Ejecuta la eliminación de una configuración.

        Args:
            key (str): Clave de la configuración a eliminar

        Returns:
            bool: True si se eliminó correctamente, False si no
        """
        return self.config_repository.delete_by_key(key)