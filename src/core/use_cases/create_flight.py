# src\core\use_cases\create_flight.py
"""
Módulo que implementa el caso de uso para la creación de vuelos,
siguiendo los principios de arquitectura hexagonal y clean architecture.

Este módulo contiene la lógica de negocio para la creación de nuevos
vuelos en el sistema, manteniendo la independencia de los detalles
de implementación.
"""

from src.core.ports.flight_repository import FlightRepository
from src.core.entities.flight import Flight

class CreateFlightUseCase:
    """
    Caso de uso para crear un nuevo vuelo en el sistema.

    Esta clase implementa la lógica de negocio para la creación de vuelos,
    siguiendo el principio de responsabilidad única y manteniéndose
    independiente de los detalles de infraestructura.

    Attributes:
        flight_repository (FlightRepository): Repositorio de vuelos
    """

    def __init__(self, flight_repository: FlightRepository):
        self.flight_repository = flight_repository

    def execute(self, flight_data: dict) -> Flight:
        """
        Ejecuta la creación de un nuevo vuelo.

        Este método implementa la lógica principal del caso de uso,
        validando los datos recibidos y delegando el almacenamiento
        al repositorio correspondiente.

        Args:
            flight_data (dict): Diccionario con los datos del vuelo

        Returns:
            Flight: Vuelo creado y almacenado en el sistema
        """
        # Validar y convertir fechas/horas
        flight = Flight(**flight_data)
        return self.flight_repository.save(flight)

