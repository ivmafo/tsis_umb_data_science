import duckdb
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List
from .manage_sectors import ManageSectors
from .predict_daily_demand import PredictDailyDemand

class PredictSectorSaturation:
    def __init__(self, db_path: str = "data/metrics.duckdb"):
        self.db_path = db_path
        self.manage_sectors = ManageSectors(db_path)
        self.demand_predictor = PredictDailyDemand(db_path)

    def execute(self, sector_id: str = None, days_ahead: int = 30,  start_date: str = None, end_date: str = None, **kwargs) -> Dict[str, Any]:
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

        # 2. Calculate Capacity (CH)
        t_transfer = sector.get('t_transfer', 0) or 0
        t_comm_ag = sector.get('t_comm_ag', 0) or 0
        t_separation = sector.get('t_separation', 0) or 0
        t_coordination = sector.get('t_coordination', 0) or 0
        TFC = t_transfer + t_comm_ag + t_separation + t_coordination
        
        if TFC <= 0:
            # Fallback or error?
            # return {"error": "Sector TFC is zero. Cannot calculate capacity."}
             TFC = 1 # Avoid div by zero, but warn
        
        buffer_factor = 1.3
        CH = 3600 / (TFC * buffer_factor)
        
        R = sector.get('adjustment_factor_r', 0.8) or 0.8
        CH_Adjusted = CH * R

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
        max_saturation = max([x['saturation_index'] for x in enhanced_forecast]) if enhanced_forecast else 0
        avg_saturation = np.mean([x['saturation_index'] for x in enhanced_forecast]) if enhanced_forecast else 0
        
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
            {"step": "1. Tiempo de Ocupación (TFC)", "detail": f"Suma de tiempos promedios (Transferencia, Comms, etc): {TFC} segundos por vuelo."},
            {"step": "2. Capacidad Teórica", "detail": f"3600s / (TFC * 1.3 Buffer) = {round(CH, 1)} vuelos/hora."},
            {"step": "3. Ajuste por Complejidad", "detail": f"Capacidad Teórica * Factor R ({R}) = {round(CH_Adjusted, 1)} vuelos/hora (Capacidad Final)."},
            {"step": "4. Índice de Saturación", "detail": f"(Demanda Pico Estimada / Capacidad Final) * 100."}
        ]



        # --- EXECUTIVE REPORT (STORYTELLING) ---
        executive_report = {
            "title": "Informe Ejecutivo de Saturación de Sector",
            "narrative": (
                f"**Estimado Coordinador de Vuelo:**\n\n"
                f"La salud operativa del sector **{sector['name']}** se clasifica actualmente como **{status_text}**.\n"
                f"Nuestros cálculos indican que, en el momento de mayor estrés, la demanda ocupará el **{round(max_saturation, 1)}%** de la capacidad segura disponible.\n\n"
                f"**La Ciencia de la Capacidad:**\n"
                f"No todos los vuelos 'pesan' lo mismo. Hemos calculado un **Tiempo de Ocupación (TFC)** de {round(TFC)} segundos por aeronave. "
                f"Esto significa que cada avión 'consume' esa cantidad de tiempo de atención exclusiva del controlador. "
                f"Considerando el factor de complejidad R={R}, su equipo puede manejar de manera segura **{round(CH_Adjusted, 1)} vuelos por hora**.\n\n"
                f"**Veredicto Operativo:**\n"
                f"{'✅ Operación Verde: El sector tiene holgura suficiente. No se requieren medidas.' if max_saturation <= 80 else ('⚠️ Alerta Amarilla: Estamos cerca del límite. Se recomienda vigilancia activa.' if max_saturation <= 100 else '❌ Alerta Roja: La demanda excede la capacidad. ES IMPERATIVO aplicar medidas de gestión de flujo (slots/retrasos) para garantizar la seguridad.')}\n\n"
                f"**Glosario:**\n"
                f"- **Capacidad Declarada**: El número máximo de aviones que entran en el sector antes de que la seguridad se vea comprometida.\n"
                f"- **Saturación**: El porcentaje del 'tanque de combustible' del controlador que se está utilizando."
            ),
            "key_highlights": [
                {"label": "Estado", "value": status_text, "insight": "Condición operativa"},
                {"label": "Saturación Máx", "value": f"{round(max_saturation, 1)}%", "insight": "% de capacidad utilizada"},
                {"label": "Capacidad Real", "value": f"{round(CH_Adjusted, 1)}/hr", "insight": "Límite seguro de flujo"}
            ]
        }
        
        return {
            "sector_name": sector['name'],
            "description": description,
            "seasonal": demand_result.get("seasonal", False),
            "history": demand_result.get("history", []),
            "forecast": enhanced_forecast,
            "metrics": {
                "TFC": round(TFC, 2),
                "CH_Adjusted": round(CH_Adjusted, 2),
                "R_Factor": R,
                "Max_Saturation": round(max_saturation, 1),
                "Status": status_text
            },
            "calculation_steps": calculation_steps,
            "executive_report": executive_report
        }
