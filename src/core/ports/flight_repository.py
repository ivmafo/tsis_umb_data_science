# src\core\ports\flight_repository.py
"""
Puerto que define el contrato para el repositorio de vuelos,
siguiendo los principios de arquitectura hexagonal y clean architecture.

Este puerto actúa como una interfaz principal en el núcleo del dominio
que establece las operaciones necesarias para la gestión de vuelos,
manteniendo la independencia de la implementación específica de la base de datos.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from src.core.entities.flight import Flight
from src.core.dtos.flight_dtos import (
    FlightFilterDTO,
    FlightOriginCountDTO,
    FlightDestinationCountDTO,
    FlightAirlineCountDTO,
    FlightTypeCountDTO,
    FlightHourlyCountDTO,
    DateRangeDTO
)

class FlightRepository(ABC):
    """
    Puerto abstracto que define el contrato para el repositorio de vuelos.

    Esta interfaz sigue el patrón de puertos y adaptadores de la arquitectura hexagonal,
    permitiendo que el dominio defina las operaciones necesarias para la gestión de
    vuelos sin acoplarse a una implementación específica de persistencia.

    Methods:
        save(flight: Flight) -> Flight:
            Guarda un nuevo vuelo en el repositorio.
            
        find_by_id(flight_id: str) -> Optional[Flight]:
            Busca un vuelo por su identificador.
            
        find_by_callsign(callsign: str) -> Optional[Flight]:
            Busca un vuelo por su señal distintiva.
            
        get_origins_count(filters: FlightFilterDTO) -> List[FlightOriginCountDTO]:
            Obtiene el conteo de vuelos por origen aplicando filtros.
            
        get_hourly_counts_by_date_ranges(date_ranges: List[DateRangeDTO]) -> List[FlightHourlyCountDTO]:
            Obtiene el conteo de vuelos por hora para rangos de fechas específicos.
    """

    @abstractmethod
    def save(self, flight: Flight) -> Flight:
        """
        Guarda un nuevo vuelo.

        Args:
            flight (Flight): Vuelo a guardar

        Returns:
            Flight: Vuelo guardado con datos actualizados
        """
        pass

    @abstractmethod
    def find_by_id(self, flight_id: str) -> Optional[Flight]:
        """
        Busca un vuelo por su identificador.

        Args:
            flight_id (str): Identificador del vuelo

        Returns:
            Optional[Flight]: Vuelo encontrado o None si no existe
        """
        pass

    def find_by_callsign(self, callsign: str) -> Optional[Flight]:
        """
        Busca un vuelo por su señal distintiva.

        Args:
            callsign (str): Señal distintiva del vuelo

        Returns:
            Optional[Flight]: Vuelo encontrado o None si no existe
        """
        pass

    @abstractmethod
    def get_origins_count(self, filters: FlightFilterDTO) -> List[FlightOriginCountDTO]:
        """
        Obtiene el conteo de vuelos por origen.

        Args:
            filters (FlightFilterDTO): Filtros a aplicar en la búsqueda

        Returns:
            List[FlightOriginCountDTO]: Lista de conteos por origen
        """
        pass

    @abstractmethod
    def get_hourly_counts_by_date_ranges(self, date_ranges: List[DateRangeDTO]) -> List[FlightHourlyCountDTO]:
        """
        Obtiene el conteo de vuelos por hora para rangos de fechas.

        Args:
            date_ranges (List[DateRangeDTO]): Lista de rangos de fechas a analizar

        Returns:
            List[FlightHourlyCountDTO]: Lista de conteos por hora
        """
        pass

    @abstractmethod
    def get_distinct_months(self) -> List[str]:
        """Gets distinct months from flights"""
        pass

    @abstractmethod
    def get_distinct_destinations(self) -> List[str]:
        """Gets distinct destinations from flights"""
        pass

    @abstractmethod
    def get_distinct_origins(self) -> List[str]:
        """Gets distinct origins from flights"""
        pass

    @abstractmethod
    def get_distinct_aircraft_types(self) -> List[str]:
        """Gets distinct aircraft types from flights"""
        pass

    @abstractmethod
    def get_distinct_airlines(self) -> List[str]:
        """Gets distinct airlines from flights"""
        pass

    @abstractmethod
    def get_distinct_flight_types(self) -> List[str]:
        """Gets distinct flight types from flights"""
        pass

    @abstractmethod
    def get_distinct_years(self) -> List[str]:
        """
        Gets distinct years from flight records.

        Returns:
            List[str]: List of distinct years
        """
        pass

    @abstractmethod
    def get_destinations_count(self, filters: Optional[FlightFilterDTO] = None) -> List[FlightDestinationCountDTO]:
        """Gets count of flights by destination"""
        pass

    @abstractmethod
    def get_airlines_count(self, filters: Optional[FlightFilterDTO] = None) -> List[FlightAirlineCountDTO]:
        """Gets count of flights by airline"""
        pass

    @abstractmethod
    def get_flight_types_count(self, filters: Optional[FlightFilterDTO] = None) -> List[FlightTypeCountDTO]:
        """Gets count of flights by type"""
        pass

