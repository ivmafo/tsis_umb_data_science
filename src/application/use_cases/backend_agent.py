from typing import Dict, Any, List
from src.application.use_cases.manage_sectors import ManageSectors
from src.application.use_cases.manage_airports import ManageAirports
from src.application.use_cases.calculate_sector_capacity import CalculateSectorCapacity
from src.domain.agents.compliance_officer import ComplianceOfficer
from src.domain.agents.physicist import Physicist
from src.domain.agents.risk_manager import RiskManager
from src.domain.entities.airport import Airport

class BackendAgent:
    """
    Agente Integrador (The Integrator) - Application Layer
    
    Orquesta los tres agentes núcleo (Normativo, Performance y Riesgo).
    Interconecta la capa de Controladores de FastAPI con la capa de Persistencia,
    despachando las consultas históricas, ejecutando las validaciones y resolviendo 
    la simulación estocástica para emitir el pronóstico final de Capacidad RAC 14.
    """
    def __init__(
        self, 
        manage_sectors: ManageSectors, 
        manage_airports: ManageAirports,
        calculate_capacity: CalculateSectorCapacity
    ):
        self.manage_sectors = manage_sectors
        self.manage_airports = manage_airports
        self.calculate_capacity = calculate_capacity

    def execute_dynamic_capacity_calculation(self, sector_id: str, filters: Dict[str, Any], utilization_factor: float = 0.8) -> Dict[str, Any]:
        """
        Ejecuta el cálculo Dinámico Estocástico de RAC 14.
        
        Args:
            sector_id (str): ID del sector a analizar.
            filters (Dict): Filtros para calcular el TPS histórico nominal.
            utilization_factor (float): Factor Ashford (0.1 a 1.0) para estrés probabilístico.
            
        Returns:
            Dict: Objeto JSON estructurado con la capacidad y rangos de confianza.
        """
        # 1. Recuperar la configuración del Sector y su capacidad nominal base
        # Usamos el legacy CalculateSectorCapacity como base "teórica circular 006"
        sector_data = self.manage_sectors.get_by_id(sector_id)
        if not sector_data:
            raise ValueError(f"Sector {sector_id} no encontrado")
            
        # Load empirical Ashford Factor assigned to this specific sector
        sector_util_factor = sector_data.get("utilization_factor", utilization_factor)
            
        nominal_result = self.calculate_capacity.execute(sector_id, filters)
        
        if "error" in nominal_result:
            return nominal_result  # Retorna el error temprano (eje. no hay datos TPS)
            
        nominal_tfc = nominal_result["TFC_Total"]
        base_separation = nominal_result["TFC_Breakdown"]["t_separation"]
        tps = nominal_result["TPS"]
        
        # 2. Obtener lista de Aeropuertos implicados en el sector
        sector_def = sector_data.get('definition', {})
        origins = sector_def.get('origins', [])
        destinations = sector_def.get('destinations', [])
        all_icao_codes = set(origins + destinations)
        
        airports_entities: List[Airport] = []
        for icao in all_icao_codes:
            # Reutiliza el repositorio de aeropuertos para buscar por ICAO
            ap = self.manage_airports.repository.get_by_icao(icao)
            if ap:
                airports_entities.append(ap)
                
        # 3. Orquestar Agentes RAC 14
        compliance_observations = []
        worst_tfc = nominal_tfc
        worst_rot = 50.0 # Default base
        
        for ap in airports_entities:
            # Agente 1: Compliance Officer
            officer = ComplianceOfficer(airport=ap)
            compliance = officer.validate_rac14_compliance()
            compliance_observations.extend(compliance["observations"])
            
            # Agente 2: Physicist
            phys = Physicist(airport=ap)
            ap_tfc, ap_sep = phys.calculate_dynamic_tfc(base_tfc=nominal_tfc, base_separation=base_separation)
            ap_rot = phys.estimate_dynamic_rot()
            
            # En un entorno sectorizado, tomamos el "peor caso" de cuello de botella aeródromo
            if ap_tfc > worst_tfc:
                worst_tfc = ap_tfc
            if ap_rot > worst_rot:
                worst_rot = ap_rot
                
        # Recálculo nominal de SCV y CH con el TFC dictado por the Physicist
        buffer_factor = 1.3
        rac14_scv = tps / (worst_tfc * buffer_factor)
        rac14_ch = (3600 * rac14_scv) / tps if tps > 0 else 0
        
        # Capacidad de pista es 3600 / (ROT)
        runway_capacity = 3600 / worst_rot if worst_rot > 0 else float('inf')
        
        # El cuello de botella es el mínimo entre el TMA (CH radar) y la Pista (ROT CH)
        bottleneck_ch = min(rac14_ch, runway_capacity)
        
        # Agente 3: Risk Manager (Simulación Estocástica)
        risk_manager = RiskManager(utilization_factor=sector_util_factor)
        stochastic_report = risk_manager.simulate_stochastic_capacity(nominal_ch=bottleneck_ch)
        
        # Consolidar el Reporte JSON
        return {
            "sector_name": sector_data['name'],
            "compliance_warnings": list(set(compliance_observations)), # Elimina duplicados
            "physicist_metrics": {
                "dynamic_tfc": round(worst_tfc, 2),
                "dynamic_rot": round(worst_rot, 2),
                "bottleneck_source": "Runway ROT" if runway_capacity < rac14_ch else "Radar TMA (TFC)"
            },
            "stochastic_capacity_report": stochastic_report,
            "legacy_nominal_comparison": {
                "ch_theoretical": nominal_result.get("CH_Theoretical", 0),
                "ch_adjusted": nominal_result.get("CH_Adjusted", 0),
                "tps_seconds": nominal_result.get("TPS", 0),
                "scv_aircraft": nominal_result.get("SCV", 0),
                "total_flights_analyzed": nominal_result.get("total_flights_analyzed", 0),
                "r_factor": nominal_result.get("R_Factor", 1.0),
                "tfc_breakdown": nominal_result.get("TFC_Breakdown", {})
            }
        }
