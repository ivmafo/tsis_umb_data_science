"""
Módulo que implementa los casos de uso relacionados con los rangos de niveles,
siguiendo los principios de arquitectura hexagonal y clean architecture.

Este módulo contiene la lógica de negocio para la gestión completa de rangos
de niveles, manteniendo la independencia de los detalles de implementación.
"""

from src.core.ports.level_range_repository import LevelRangeRepository
from src.core.entities.level_range import LevelRange
from datetime import datetime

class CreateLevelRangeUseCase:
    """
    Caso de uso para crear un nuevo rango de niveles.

    Esta clase implementa la lógica de negocio para la creación de rangos
    de niveles, siguiendo el principio de responsabilidad única.

    Attributes:
        level_range_repository (LevelRangeRepository): Repositorio de rangos de niveles
    """

    def __init__(self, level_range_repository: LevelRangeRepository):
        self.level_range_repository = level_range_repository

    def execute(self, level_range_data: dict):
        """
        Ejecuta la creación de un nuevo rango de niveles.

        Args:
            level_range_data (dict): Datos del rango de niveles a crear

        Returns:
            LevelRange: Rango de niveles creado
        """
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
    """
    Caso de uso para actualizar un rango de niveles existente.

    Attributes:
        level_range_repository (LevelRangeRepository): Repositorio de rangos de niveles
    """

    def __init__(self, level_range_repository: LevelRangeRepository):
        self.level_range_repository = level_range_repository

    def execute(self, id: int, level_range_data: dict) -> LevelRange:
        """
        Ejecuta la actualización de un rango de niveles.

        Args:
            id (int): Identificador del rango de niveles
            level_range_data (dict): Nuevos datos del rango de niveles

        Returns:
            LevelRange: Rango de niveles actualizado

        Raises:
            ValueError: Si el rango de niveles no existe
        """
        level_range = self.level_range_repository.find_by_id(id)
        if not level_range:
            raise ValueError(f"Rango de niveles con ID '{id}' no encontrado")
        
        level_range.origen = level_range_data.get('origen', level_range.origen)
        level_range.destino = level_range_data.get('destino', level_range.destino)
        level_range.nivel_min = level_range_data.get('nivel_min', level_range.nivel_min)
        level_range.nivel_max = level_range_data.get('nivel_max', level_range.nivel_max)
        level_range.ruta = level_range_data.get('ruta', level_range.ruta)
        level_range.zona = level_range_data.get('zona', level_range.zona)
        
        return self.level_range_repository.update(level_range)

class GetLevelRangeUseCase:
    """
    Caso de uso para obtener un rango de niveles por su ID.

    Attributes:
        level_range_repository (LevelRangeRepository): Repositorio de rangos de niveles
    """

    def __init__(self, level_range_repository: LevelRangeRepository):
        self.level_range_repository = level_range_repository

    def execute(self, id: int) -> LevelRange:
        """
        Ejecuta la búsqueda de un rango de niveles por ID.

        Args:
            id (int): Identificador del rango de niveles

        Returns:
            LevelRange: Rango de niveles encontrado

        Raises:
            ValueError: Si el rango de niveles no existe
        """
        level_range = self.level_range_repository.find_by_id(id)
        if not level_range:
            raise ValueError(f"Rango de niveles con ID '{id}' no encontrado")
        return level_range

class GetLevelRangeByRouteUseCase:
    """
    Caso de uso para obtener un rango de niveles por ruta.

    Attributes:
        level_range_repository (LevelRangeRepository): Repositorio de rangos de niveles
    """

    def __init__(self, level_range_repository: LevelRangeRepository):
        self.level_range_repository = level_range_repository

    def execute(self, origen: str, destino: str) -> LevelRange:
        """
        Ejecuta la búsqueda de un rango de niveles por ruta.

        Args:
            origen (str): Punto de origen de la ruta
            destino (str): Punto de destino de la ruta

        Returns:
            LevelRange: Rango de niveles encontrado

        Raises:
            ValueError: Si no se encuentra el rango de niveles para la ruta
        """
        level_range = self.level_range_repository.find_by_route(origen, destino)
        if not level_range:
            raise ValueError(f"Rango de niveles para ruta {origen}-{destino} no encontrado")
        return level_range

class GetLevelRangesByZoneUseCase:
    """
    Caso de uso para obtener rangos de niveles por zona.

    Attributes:
        level_range_repository (LevelRangeRepository): Repositorio de rangos de niveles
    """

    def __init__(self, level_range_repository: LevelRangeRepository):
        self.level_range_repository = level_range_repository

    def execute(self, zona: str) -> list[LevelRange]:
        """
        Ejecuta la búsqueda de rangos de niveles por zona.

        Args:
            zona (str): Identificador de la zona

        Returns:
            list[LevelRange]: Lista de rangos de niveles en la zona
        """
        return self.level_range_repository.find_by_zone(zona)

class GetAllLevelRangesUseCase:
    """
    Caso de uso para obtener todos los rangos de niveles.

    Attributes:
        level_range_repository (LevelRangeRepository): Repositorio de rangos de niveles
    """

    def __init__(self, level_range_repository: LevelRangeRepository):
        self.level_range_repository = level_range_repository

    def execute(self):
        """
        Ejecuta la obtención de todos los rangos de niveles.

        Returns:
            List[LevelRange]: Lista de todos los rangos de niveles
        """
        return self.level_range_repository.get_all()

class DeleteLevelRangeUseCase:
    """
    Caso de uso para eliminar un rango de niveles.

    Attributes:
        level_range_repository (LevelRangeRepository): Repositorio de rangos de niveles
    """

    def __init__(self, level_range_repository: LevelRangeRepository):
        self.level_range_repository = level_range_repository

    def execute(self, id: int) -> bool:
        """
        Ejecuta la eliminación de un rango de niveles.

        Args:
            id (int): Identificador del rango de niveles a eliminar

        Returns:
            bool: True si se eliminó correctamente, False si no
        """
        return self.level_range_repository.delete_by_id(id)