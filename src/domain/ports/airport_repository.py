from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from src.domain.entities.airport import Airport

class AirportRepository(ABC):
    """
    Interface (Puerto) para el repositorio de Aeropuertos.
    
    Define los métodos necesarios para la persistencia y recuperación de datos de aeropuertos,
    independientemente de la implementación técnica (SQL, NoSQL, memoria).
    """
    @abstractmethod
    def get_paginated(self, page: int, page_size: int, search: str = "") -> Tuple[List[Airport], int]:
        """
        Obtiene una lista paginada de aeropuertos.
        
        Args:
            page: El número de página a recuperar.
            page_size: Cantidad de elementos por página.
            search: Término de búsqueda para filtrar por nombre o código.
            
        Returns:
            Una tupla que contiene (lista_de_aeropuertos, total_de_registros).
        """
        pass

    @abstractmethod
    def get_by_id(self, airport_id: int) -> Optional[Airport]:
        """Recupera un aeropuerto específico por su identificador numérico interno."""
        pass

    @abstractmethod
    def get_by_icao(self, icao_code: str) -> Optional[Airport]:
        """Recupera un aeropuerto por su código único internacional OACI (ej. SKBO)."""
        pass

    @abstractmethod
    def create(self, airport: Airport) -> Airport:
        """Registra un nuevo aeropuerto en el sistema."""
        pass

    @abstractmethod
    def update(self, airport: Airport) -> Optional[Airport]:
        """Actualiza la información de un aeropuerto existente."""
        pass

    @abstractmethod
    def delete(self, airport_id: int) -> bool:
        """Elimina un aeropuerto del sistema por su ID."""
        pass
