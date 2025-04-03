# src\core\ports\level_range_repository.py
"""
Puerto que define el contrato para el repositorio de rangos de niveles,
siguiendo los principios de arquitectura hexagonal y clean architecture.

Este puerto actúa como una interfaz en el núcleo del dominio que establece
las operaciones necesarias para la gestión de rangos de niveles de vuelo,
manteniendo la independencia de la implementación específica de persistencia.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from src.core.entities.level_range import LevelRange

class LevelRangeRepository(ABC):
    """
    Puerto abstracto que define el contrato para el repositorio de rangos de niveles.

    Esta interfaz sigue el patrón de puertos y adaptadores de la arquitectura hexagonal,
    permitiendo que el dominio defina las operaciones necesarias para la gestión de
    rangos de niveles sin acoplarse a una implementación específica.

    Methods:
        save(level_range: LevelRange) -> LevelRange:
            Guarda un nuevo rango de nivel.
            
        find_by_id(id: int) -> Optional[LevelRange]:
            Busca un rango de nivel por su identificador.
            
        find_by_route(origen: str, destino: str) -> Optional[LevelRange]:
            Busca un rango de nivel por ruta específica.
            
        find_by_zone(zona: str) -> List[LevelRange]:
            Obtiene todos los rangos de nivel de una zona.
            
        find_by_level_range(nivel_min: int, nivel_max: int) -> List[LevelRange]:
            Busca rangos de nivel dentro de un intervalo específico.
            
        get_all() -> List[LevelRange]:
            Obtiene todos los rangos de nivel.
            
        update(level_range: LevelRange) -> LevelRange:
            Actualiza un rango de nivel existente.
            
        delete_by_id(id: int) -> bool:
            Elimina un rango de nivel por su identificador.
    """

    @abstractmethod
    def save(self, level_range: LevelRange) -> LevelRange:
        """
        Guarda un nuevo rango de nivel.

        Args:
            level_range (LevelRange): Rango de nivel a guardar

        Returns:
            LevelRange: Rango de nivel guardado con datos actualizados
        """
        pass

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[LevelRange]:
        """
        Busca un rango de nivel por su identificador.

        Args:
            id (int): Identificador del rango de nivel

        Returns:
            Optional[LevelRange]: Rango de nivel encontrado o None si no existe
        """
        pass

    @abstractmethod
    def find_by_route(self, origen: str, destino: str) -> Optional[LevelRange]:
        """
        Busca un rango de nivel por ruta específica.

        Args:
            origen (str): Punto de origen de la ruta
            destino (str): Punto de destino de la ruta

        Returns:
            Optional[LevelRange]: Rango de nivel encontrado o None si no existe
        """
        pass

    @abstractmethod
    def find_by_zone(self, zona: str) -> List[LevelRange]:
        """
        Obtiene todos los rangos de nivel de una zona.

        Args:
            zona (str): Identificador de la zona

        Returns:
            List[LevelRange]: Lista de rangos de nivel en la zona
        """
        pass

    @abstractmethod
    def find_by_level_range(self, nivel_min: int, nivel_max: int) -> List[LevelRange]:
        """
        Busca rangos de nivel dentro de un intervalo específico.

        Args:
            nivel_min (int): Nivel mínimo del rango
            nivel_max (int): Nivel máximo del rango

        Returns:
            List[LevelRange]: Lista de rangos de nivel que cumplen el criterio
        """
        pass

    @abstractmethod
    def get_all(self) -> List[LevelRange]:
        """
        Obtiene todos los rangos de nivel.

        Returns:
            List[LevelRange]: Lista de todos los rangos de nivel
        """
        pass

    @abstractmethod
    def update(self, level_range: LevelRange) -> LevelRange:
        """
        Actualiza un rango de nivel existente.

        Args:
            level_range (LevelRange): Rango de nivel con datos actualizados

        Returns:
            LevelRange: Rango de nivel actualizado
        """
        pass

    @abstractmethod
    def delete_by_id(self, id: int) -> bool:
        """
        Elimina un rango de nivel por su identificador.

        Args:
            id (int): Identificador del rango de nivel a eliminar

        Returns:
            bool: True si se eliminó correctamente, False si no
        """
        pass