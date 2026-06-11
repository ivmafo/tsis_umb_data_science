from typing import Dict, Any
from src.domain.entities.airport import Airport

class Physicist:
    """
    Agente de Performance (The Physicist)
    
    Calcula cómo la altitud, temperatura y tipo de avión afectan el 
    ROT (Runway Occupancy Time) y el TPS.
    Implementa la validación nacional del 15% de incremento en separación.
    """
    
    def __init__(self, airport: Airport):
        self.airport = airport
        
    def calculate_dynamic_tfc(self, base_tfc: float, base_separation: float) -> tuple[float, float]:
        """
        Calcula el Tiempo de Funciones de Control (TFC) y Separación dinámico.
        Aplica penalizaciones por factores geofísicos e infraestructura.
        Base Normativa: OACI Doc 4444 (PANS-ATM) - Separación Mínima.
        
        Args:
            base_tfc: TFC estándar
            base_separation: Tiempo de separación base (Doc 4444)
            
        Returns:
            Tuple (tfc_ajustado, separacion_ajustada)
        """
        adjusted_separation = base_separation
        adjusted_tfc = base_tfc
        
        # Validación Nacional: > 5000 pies aplica +15% separación (Densidad del aire / True Airspeed)
        if self.airport.is_high_altitude:
            # Si el tiempo base es > 0, lo incrementamos
            if adjusted_separation > 0:
                 increment = adjusted_separation * 0.15
                 adjusted_separation += increment
                 adjusted_tfc += increment # Impacta directamente el TFC
                 
        return adjusted_tfc, adjusted_separation
        
    def estimate_dynamic_rot(self) -> float:
        """
        Estima el Runway Occupancy Time (ROT) basado en la infraestructura del aeropuerto.
        Usado para limitar la Capacidad Horaria (CH) por la pista.
        Base Normativa: OACI Doc 9157 (Manual de Diseño de Aeródromos) y RAC 14 Cap. C.
        """
        base_rot = 50.0  # Segundos base para un aeropuerto optimizado
        
        if self.airport.requires_backtrack:
            base_rot += 120.0  # El backtrack destruye la eficiencia sumando ~2 minutos
            
        if not self.airport.has_rapid_exit_taxiway:
            base_rot += 15.0   # Sin salidas rápidas, rodaje a 90 grados toma más.
            
        if self.airport.is_high_altitude:
            base_rot *= 1.10   # Aterrizaje más rápido por TAS, mayor distancia de frenado = más ROT
            
        return base_rot
