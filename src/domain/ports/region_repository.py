from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.region import Region

class RegionRepository(ABC):
    """
    Interface (Puerto) para la gestión de Regiones Aeronáuticas.
    
    Define las operaciones permitidas sobre las regiones que agrupan sectores y aeropuertos.
    """
    @abstractmethod
    def get_all(self) -> List[Region]:
        """Recupera el listado completo de regiones registradas."""
        pass

    @abstractmethod
    def get_by_id(self, region_id: int) -> Optional[Region]:
        """Obtiene el detalle de una región por su ID."""
        pass

    @abstractmethod
    def create(self, region: Region) -> Region:
        """Crea una nueva región en el sistema."""
        pass

    @abstractmethod
    def update(self, region: Region) -> Optional[Region]:
        """Modifica los datos de una región existente."""
        pass

    @abstractmethod
    def delete(self, region_id: int) -> bool:
        """Elimina una región del sistema."""
        pass
