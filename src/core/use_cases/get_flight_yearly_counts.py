from typing import List, Dict
from src.core.ports.flight_repository import FlightRepository
from src.core.dtos.flight_dtos import DateRangeDTO

class GetFlightYearlyCountsUseCase:
    """
    Caso de uso para obtener el conteo anual de vuelos
    """
    
    def __init__(self, flight_repository: FlightRepository):
        self.flight_repository = flight_repository

    def execute(self, date_ranges: List[DateRangeDTO], analysis_type: str) -> List[Dict]:
        """
        Ejecuta el análisis anual de vuelos
        
        Args:
            date_ranges: Lista de rangos de fechas para analizar
            analysis_type: Tipo de análisis ('origin' o 'destination')
            
        Returns:
            Lista de diccionarios con los conteos anuales
        """
        return self.flight_repository.get_yearly_counts_by_date_ranges(
            date_ranges,
            analysis_type
        )