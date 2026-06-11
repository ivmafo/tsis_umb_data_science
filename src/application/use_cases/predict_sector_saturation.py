import duckdb
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List
from .manage_sectors import ManageSectors
from .predict_daily_demand import PredictDailyDemand

class PredictSectorSaturation:
    """
    Analizador de riesgo de saturación técnica.
    Cruza los modelos de demanda predictiva con la capacidad técnica calculada 
    para identificar momentos exactos de sobrecarga operativa en el futuro.
    """
    def __init__(self, db_path: str = "data/metrics.duckdb", backend_agent=None):
        """
        Inicializa el analizador inyectando sus dependencias.
        """
        self.db_path = db_path
        self.manage_sectors = ManageSectors(db_path)
        self.demand_predictor = PredictDailyDemand(db_path)
        self.backend_agent = backend_agent

    def execute(self, sector_id: str = None, days_ahead: int = 30,  start_date: str = None, end_date: str = None, **kwargs) -> Dict[str, Any]:
        """
        Calcula el índice de saturación proyectado.
        
        Deriva la carga horaria máxima estimada (pico) y la compara con la 
        Capacidad Declarada del sector para emitir estados de alerta (Normal/Alerta/Crítico).
        
        Args:
            sector_id (str): UUID del sector (Obligatorio).
            days_ahead (int): Horizonte de proyección.
            start_date/end_date: Rango para análisis estacional si aplica.
            
        Returns:
            Dict: Reporte ejecutivo de saturación y series históricas/proyectadas.
        """
        # Support kwargs for other filters if passed, though Sector Saturation primarily needs SectorID
        # The API controller might pass other filters in kwargs or we explicitly add them.
        # But for Saturation, SectorID is mandatory.
        
        if not sector_id:
             # Try to find sector_id in kwargs if not passed directly? 
             # The controller passes filters.sector_id
             sector_id = kwargs.get('sector_id')
        
        if not sector_id:
            return {"error": "Sector ID is required for saturation prediction"}

        # 1. Get Sector Details
        sector = self.manage_sectors.get_by_id(sector_id)
        if not sector:
            return {"error": f"Sector {sector_id} not found"}

        # 2. Calculate Capacity (CH) via BackendAgent stochastics instead of manual formula
        if not self.backend_agent:
            return {"error": "System not configured with RAC 14 BackendAgent"}
            
        try:
            # filters pass empty initially since demand is handled later
            cap_report = self.backend_agent.execute_dynamic_capacity_calculation(sector_id, {})
        except ValueError as e:
            return {"error": str(e)}
            
        if "error" in cap_report:
            return cap_report
            
        # Extraemos la capacidad determinista estocástica del Backend Agent
        stochastic_data = cap_report.get("stochastic_capacity_report", {})
        physicist_data = cap_report.get("physicist_metrics", {})
        
        # En vez de CH_Adjusted, usamos la capacidad simulada segura
        # que incorpora el Factor Ashford y penalidades por altitud/infraestructura
        CH_Adjusted = stochastic_data.get("stochastic_simulated_capacity", 0)
        
        # Guardamos TFC calculado por el físico para el reporte
        TFC_dynamic = physicist_data.get("dynamic_tfc", 0)

        # 3. Forecast Demand (Delegate)
        # Pass all compatible arguments
        # We pass sector_id explicitly. Other filters (airport, route) might effectively subset the sector demand?
        # Usually Sector Saturation is about TOTAL sector traffic.
        # So we should probably NOT filter by airport/route unless the user specifically wants "Saturation contribution from Route X".
        # But usually we want total load.
        # Let's pass the filters if provided, assuming the user knows what they are doing (analyzing a subset).
        
        demand_result = self.demand_predictor.execute(
            days_ahead=days_ahead,
            sector_id=sector_id,
            start_date=start_date,
            end_date=end_date,
            **kwargs # airport, route, level
        )
        
        if "error" in demand_result:
            return demand_result

        # 4. Enhance Forecast with Saturation Metrics
        forecast_data = demand_result.get("forecast", [])
        enhanced_forecast = []
        
        for item in forecast_data:
            val = item.get("value", 0)
            
            # Estimate Peak Hour Load (10% rule or from history?)
            # 10% rule is standard simple heuristic
            estimated_peak_hour_load = val * 0.10
            
            saturation_index = (estimated_peak_hour_load / CH_Adjusted) * 100 if CH_Adjusted > 0 else 0
            
            enhanced_item = item.copy()
            enhanced_item.update({
                "predicted_daily_flights": val,
                "estimated_peak_hour_load": round(estimated_peak_hour_load, 1),
                "saturation_index": round(saturation_index, 1),
                "capacity_hourly": round(CH_Adjusted, 1),
                "status": "Critical" if saturation_index > 100 else ("Warning" if saturation_index > 80 else "Normal")
            })
            enhanced_forecast.append(enhanced_item)

        # 5. Return Result
        max_saturation = float(max([x['saturation_index'] for x in enhanced_forecast])) if enhanced_forecast else 0.0
        avg_saturation = float(np.mean([x['saturation_index'] for x in enhanced_forecast])) if enhanced_forecast else 0.0
        
        status_text = "Normal"
        if max_saturation > 100: status_text = "CRÍTICO (Sobrecarga)"
        elif max_saturation > 80: status_text = "ALERTA (Riesgo de Saturación)"
        
        # Plain Language Description
        description = (
            f"El sector **{sector['name']}** opera con un estado **{status_text}**. "
            f"Su Capacidad Declarada Ajustada es de **{round(CH_Adjusted, 1)} vuelos/hora**. "
            f"Se prevé que la demanda máxima alcance el **{round(max_saturation, 1)}%** de esta capacidad. "
            f"{'Se requieren medidas de gestión de flujo (ATFM).' if max_saturation > 80 else 'La operación se mantiene dentro de los márgenes seguros.'}"
        )
        
        # Calculation Breakdown
        calculation_steps = [
            {"step": "1. Análisis Normativo (Compliance)", "detail": f"Advertencias RAC 14 detectadas: {len(cap_report.get('compliance_warnings', []))}."},
            {"step": "2. Performance Física (The Physicist)", "detail": f"TFC Dinámico: {float(round(TFC_dynamic, 1))}s. Origen Cuello de Botella: {physicist_data.get('bottleneck_source')}."},
            {"step": "3. Capacidad Estocástica (Risk Manager)", "detail": f"Capacidad Asegurada Base: {float(round(stochastic_data.get('ashford_baseline_capacity', 0), 1))} / Capacidad Simulada Final: {float(round(CH_Adjusted, 1))} vuelos/hr."},
            {"step": "4. Índice de Riesgo Futuro (Predicción AI)", "detail": "(Demanda Pico AI / Capacidad Simulada Final) * 100."}
        ]



        # --- EXECUTIVE REPORT (STORYTELLING) ---
        executive_report = {
            "title": "Informe Ejecutivo de Riesgo y Saturación Estocástica",
            "narrative": (
                f"**Estimado Coordinador de Vuelo:**\n\n"
                f"La salud operativa proyectada del sector **{sector['name']}** se clasifica como **{status_text}**.\n"
                f"En el momento de mayor estrés de la ventana analizada, la demanda ocupará el **{round(max_saturation, 1)}%** de la capacidad probabilística segura.\n\n"
                f"**Performance Dinámica (RAC 14):**\n"
                f"Bajo el escrutinio de los agentes físicos y de riesgo, el sector tiene un TFC de cuello de botella de {round(TFC_dynamic)}s. "
                f"Al someter esta red a un Factor de Utilización Ashford de {stochastic_data.get('applied_utilization_factor', 0.8)}, confirmamos "
                f"que su equipo puede manejar con un 95% de confianza hasta **{round(CH_Adjusted, 1)} vuelos por hora**.\n\n"
                f"**Veredicto Analítico:**\n"
                f"{'✅ Operación Verde: El sector tiene holgura estocástica. Tienen control total sobre el flujo.' if max_saturation <= 80 else ('⚠️ Alerta Amarilla: Nos aproximamos a la banda de incertidumbre. Preparar tácticas ATFM visuales.' if max_saturation <= 100 else '❌ Alerta Roja: Límite estocástico superado. ACTIVAR MEDIDAS ATFM (Slots/Ruteo) para no romper los límites seguros de PANS-ATM.')}\n\n"
            ),
            "key_highlights": [
                {"label": "Estado de Simulador", "value": status_text, "insight": "Condición operativa de riesgo"},
                {"label": "Saturación Proyectada", "value": f"{round(max_saturation, 1)}%", "insight": "% de Capacidad Estocástica usada"},
                {"label": "Capacidad Asegurada", "value": f"{round(CH_Adjusted, 1)}/hr", "insight": "Dentro del 95% de confianza (Ashford)"}
            ]
        }
        
        return {
            "sector_name": sector['name'],
            "description": description,
            "seasonal": demand_result.get("seasonal", False),
            "history": demand_result.get("history", []),
            "forecast": enhanced_forecast,
            "metrics": {
                "dynamic_tfc": float(round(TFC_dynamic, 2)),
                "CH_Adjusted": float(round(CH_Adjusted, 2)),
                "stochastic_range": {
                    "lower": float(stochastic_data.get("uncertainty_range", {}).get("lower", 0)),
                    "upper": float(stochastic_data.get("uncertainty_range", {}).get("upper", 0))
                },
                "Max_Saturation": float(round(max_saturation, 1)),
                "Status": status_text
            },
            "calculation_steps": calculation_steps,
            "executive_report": executive_report
        }
