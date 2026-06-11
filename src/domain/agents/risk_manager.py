import random
from typing import Dict, Any

class RiskManager:
    """
    Agente de Simulación (The Risk Manager)
    
    Aplica el "Factor Ashford" (utilization_factor) para estresar 
    el modelo logrando una Simulación Estocástica requerida por RAC 14.
    """
    
    def __init__(self, utilization_factor: float = 0.8):
        """
        Args:
           utilization_factor: Factor empírico que penaliza el cálculo óptimo 
                               teórico (e.g. 0.8 de Ashford/FAA)
        """
        # Asegurar límites lógicos del factor
        self.utilization_factor = max(0.1, min(1.0, utilization_factor))
        
    def simulate_stochastic_capacity(self, nominal_ch: float) -> dict[str, Any]:
        """
        Simulación MonteCarlo ligera o estocástica determinística a partir de la Capacidad Nominal.
        Inyecta variables aleatorias dentro de una desviación esperada (clima/fallas de radar).
        
        Args:
            nominal_ch: Capacidad Horaria Teórica (vuelos/hora) calculada por el Physicist.
            
        Returns:
            Dict con métricas estresadas y bandas de incertidumbre.
        """
        # Aplica el factor de carga empírico primario (Ajuste RAC/Ashford)
        baseline_capacity = nominal_ch * self.utilization_factor
        
        # Inyecta estocastisidad: en la vida real, una tormenta reduce la CH, un día perfecto la maximiza (límite nominal).
        # Generamos una desviación típica empírica (ej. 10% del baseline)
        std_dev = baseline_capacity * 0.10
        
        # Banda inferior (Día complejo con LVP o fallas)
        lower_bound = baseline_capacity - (std_dev * 1.5)
        
        # Banda superior (Día perfecto, nunca superior al 100% nominal)
        upper_bound = min(nominal_ch, baseline_capacity + (std_dev * 1.5))
        
        # Simulación de un escenario estocástico puntual
        simulated_ch = random.gauss(baseline_capacity, std_dev)
        simulated_ch = max(0, min(nominal_ch, simulated_ch))
        
        return {
            "nominal_theoretical_capacity": round(nominal_ch, 2),
            "ashford_baseline_capacity": round(baseline_capacity, 2),
            "stochastic_simulated_capacity": round(simulated_ch, 2),
            "uncertainty_range": {
                "lower": round(lower_bound, 2),
                "upper": round(upper_bound, 2)
            },
            "applied_utilization_factor": self.utilization_factor,
            "status": "Estocástico"
        }
