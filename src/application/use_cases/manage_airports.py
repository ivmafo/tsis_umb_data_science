from typing import List, Tuple, Optional
from src.domain.entities.airport import Airport
from src.domain.ports.airport_repository import AirportRepository

class ManageAirports:
    """
    Servicio de aplicación para la gestión del catálogo maestro de aeropuertos.
    Orquesta las operaciones CRUD entre la interfaz de usuario y el repositorio de persistencia.
    
    Attributes:
        repository (AirportRepository): El adaptador de persistencia inyectado (puerto).
    """
    def __init__(self, repository: AirportRepository):
        """
        Inicializa el caso de uso con un repositorio específico.
        
        Args:
            repository (AirportRepository): Implementación del puerto de aeropuertos (ej. DuckDB, Memoria).
        """
        self.repository = repository

    def get_airports(self, page: int = 1, page_size: int = 10, search: str = "") -> Tuple[List[Airport], int]:
        """
        Recupera una lista paginada de aeropuertos, permitiendo filtrar por término de búsqueda.
        
        Args:
            page (int): Número de página a recuperar (inicia en 1).
            page_size (int): Cantidad de registros por página.
            search (str): Filtro opcional para buscar por código OACI o nombre.
            
        Returns:
            Tuple[List[Airport], int]: Una tupla con (lista de entidades Airport, total global de registros).
        """
        return self.repository.get_paginated(page, page_size, search)

    def get_airport(self, airport_id: int) -> Optional[Airport]:
        """
        Obtiene la información de un único aeropuerto mediante su identificador numérico.
        
        Args:
            airport_id (int): El ID interno del aeropuerto en el sistema.
            
        Returns:
            Optional[Airport]: La entidad Airport si se encuentra; None en caso contrario.
        """
        return self.repository.get_by_id(airport_id)

    def create_airport(self, data: dict) -> Airport:
        """
        Crea un nuevo registro de aeropuerto a partir de un diccionario de datos.
        
        Args:
            data (dict): Diccionario con los atributos del aeropuerto (icao_code, name, etc.).
            
        Returns:
            Airport: La entidad Airport creada y persistida.
        """
        airport = Airport(**data)
        return self.repository.create(airport)

    def update_airport(self, airport_id: int, data: dict) -> Optional[Airport]:
        """
        Actualiza los datos de un aeropuerto existente.
        
        Args:
            airport_id (int): ID del aeropuerto a actualizar.
            data (dict): Diccionario con los campos a modificar.
            
        Returns:
            Optional[Airport]: El objeto Airport actualizado o None si el ID no existe.
        """
        curr = self.repository.get_by_id(airport_id)
        if not curr:
            return None
        
        # Update fields
        updated = curr.model_copy(update=data)
        updated.id = airport_id # Ensure ID is preserved
        return self.repository.update(updated)

    def delete_airport(self, airport_id: int) -> bool:
        """
        Elimina un aeropuerto del catálogo tras verificar su existencia.
        
        Args:
            airport_id (int): El ID del aeropuerto a remover.
            
        Returns:
            bool: True si la eliminación fue exitosa; False si el aeropuerto no existía.
        """
        if not self.repository.get_by_id(airport_id):
            return False
        return self.repository.delete(airport_id)
