# src\core\ports\config_repository.py
"""
Puerto que define el contrato para el repositorio de configuraciones,
siguiendo los principios de arquitectura hexagonal y clean architecture.

Este puerto actúa como una interfaz en el núcleo del dominio que define
las operaciones permitidas para la gestión de configuraciones, independiente
de la implementación específica en la capa de infraestructura.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from src.core.entities.config import Config

class ConfigRepository(ABC):
    """
    Puerto abstracto que define el contrato para el repositorio de configuraciones.

    Esta interfaz sigue el patrón de puertos y adaptadores de la arquitectura hexagonal,
    permitiendo que el dominio defina el contrato que deben implementar los adaptadores
    de persistencia.

    Methods:
        save(config: Config) -> Config:
            Guarda una nueva configuración en el repositorio.
            
        find_by_key(key: str) -> Optional[Config]:
            Busca una configuración por su clave.
            
        get_all() -> List[Config]:
            Obtiene todas las configuraciones almacenadas.
            
        update(config: Config) -> Config:
            Actualiza una configuración existente.
            
        delete_by_key(key: str) -> bool:
            Elimina una configuración por su clave.
    """

    @abstractmethod
    def save(self, config: Config) -> Config:
        """
        Guarda una nueva configuración.

        Args:
            config (Config): Configuración a guardar

        Returns:
            Config: Configuración guardada con datos actualizados
        """
        pass

    @abstractmethod
    def find_by_key(self, key: str) -> Optional[Config]:
        """
        Busca una configuración por su clave.

        Args:
            key (str): Clave de la configuración

        Returns:
            Optional[Config]: Configuración encontrada o None si no existe
        """
        pass

    @abstractmethod
    def get_all(self) -> List[Config]:
        """
        Obtiene todas las configuraciones.

        Returns:
            List[Config]: Lista de todas las configuraciones
        """
        pass

    @abstractmethod
    def update(self, config: Config) -> Config:
        """
        Actualiza una configuración existente.

        Args:
            config (Config): Configuración con datos actualizados

        Returns:
            Config: Configuración actualizada
        """
        pass

    @abstractmethod
    def delete_by_key(self, key: str) -> bool:
        """
        Elimina una configuración por su clave.

        Args:
            key (str): Clave de la configuración a eliminar

        Returns:
            bool: True si se eliminó correctamente, False si no
        """
        pass