from pydantic import BaseModel, root_validator
from typing import Optional
from src.domain.entities.airport import Airport

class ComplianceOfficer(BaseModel):
    """
    Agente Normativo (The Compliance Officer)
    
    Conoce el RAC 14 y la Circular 006. 
    Su función es validar que los parámetros de entrada referidos a 
    la infraestructura del aeropuerto cumplan con la normativa operacional.
    """
    airport: Airport
    
    def validate_rac14_compliance(self) -> dict:
        """
        Realiza validaciones lógicas según RAC 14 / PANS-Aerodromes y Doc 9157.
        Devuelve un diccionario de warnings u observaciones normativas.
        """
        warnings = []
        
        # Validación de Código de Referencia OACI vs Infraestructura
        code_letter = self.airport.reference_code[-1] if self.airport.reference_code else ""
        
        if code_letter in ["E", "F"] and not self.airport.has_rapid_exit_taxiway:
            warnings.append(
                f"RAC-14 Observación: Aeropuertos Categoría {code_letter} (aviones pesados) "
                "deberían idealmente contar con Calles de Salida Rápida para no degradar la capacidad de pista."
            )
            
        if self.airport.requires_backtrack:
            warnings.append(
                "RAC-14 Restricción: La operación con Backtrack limita severamente "
                "la Capacidad Declarada por el aumento drástico en el Runway Occupancy Time (ROT)."
            )
            
        if self.airport.is_high_altitude:
             warnings.append(
                "RAC-14 Performance: Elevación superior a 5000ft detectada. "
                "Se aplicará penalización obligatoria del 15% en separación por altitud."
            )
            
        return {
            "compliant": True,
            "observations": warnings
        }

