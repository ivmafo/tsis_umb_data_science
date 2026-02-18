import duckdb
import pandas as pd
import numpy as np
from typing import Dict, Any, List

class PredictPeakHours:
    def __init__(self, db_path: str = "data/metrics.duckdb"):
        self.db_path = db_path

    def execute(self, sector_id: str = None, airport: str = None, route: str = None, min_level: int = None, max_level: int = None, start_date: str = None, end_date: str = None, aggregation: str = "avg") -> Dict[str, Any]:
        conn = duckdb.connect(self.db_path, read_only=True)
        try:
            # 1. Build Filter Conditions
            conditions = ["hora_salida IS NOT NULL"]
            
            # Date Logic
            if start_date and end_date:
                # SEASONAL MODE: Filter by MM-DD range across all years
                 # Extract MM-DD from dates
                from datetime import datetime
                s = datetime.strptime(start_date, "%Y-%m-%d")
                e = datetime.strptime(end_date, "%Y-%m-%d")
                start_md = s.strftime("%m-%d")
                end_md = e.strftime("%m-%d")
                
                if start_md <= end_md:
                    date_filter = f"strftime(fecha, '%m-%d') BETWEEN '{start_md}' AND '{end_md}'"
                else:
                    date_filter = f"(strftime(fecha, '%m-%d') >= '{start_md}' OR strftime(fecha, '%m-%d') <= '{end_md}')"
                
                conditions.append(date_filter)
                is_seasonal = True
            else:
                # STANDARD MODE: Last 90 Days
                conditions.append("fecha >= CURRENT_DATE - INTERVAL '90 DAYS'")
                is_seasonal = False

            params = []

            # Sector Filter
            if sector_id:
                sector = conn.execute("SELECT definition FROM sectors WHERE id = ?", [sector_id]).fetchone()
                if sector and sector[0]:
                    import json
                    definition = json.loads(sector[0])
                    origins = definition.get("origins", [])
                    destinations = definition.get("destinations", [])
                    
                    if origins and destinations:
                        origins_str = "', '".join(origins)
                        destinations_str = "', '".join(destinations)
                        conditions.append(f"origen IN ('{origins_str}') AND destino IN ('{destinations_str}')")
                    else:
                        # STANDARD MODE: Last 90 Days
                        conditions.append("fecha >= CURRENT_DATE - INTERVAL '90 DAYS'")
                        is_seasonal = False
                        return {"error": "Sector definition is incomplete."}

            # Airport Filter
            if airport:
                conditions.append("(origen = ? OR destino = ?)")
                params.extend([airport, airport])

            # Route Filter
            if route:
                parts = route.split('-')
                if len(parts) == 2:
                    conditions.append("origen = ? AND destino = ?")
                    params.extend([parts[0], parts[1]])
            
            # Level Filter
            if min_level is not None:
                conditions.append("nivel >= ?")
                params.append(min_level)
            
            if max_level is not None:
                conditions.append("nivel <= ?")
                params.append(max_level)

            where_clause = " AND ".join(conditions)

            # 2. Fetch Data with Filters
            query_daily = f"""
                SELECT 
                    fecha,
                    EXTRACT(ISODOW FROM fecha) as dow,
                    EXTRACT(HOUR FROM hora_salida) as hour,
                    COUNT(*) as count
                FROM flights
                WHERE 
                    {where_clause}
                GROUP BY 1, 2, 3
            """
            
            if params:
                df = conn.execute(query_daily, params).fetchdf()
            else:
                df = conn.execute(query_daily).fetchdf()
            
            if df.empty:
                return {"error": "Insufficient data for peak hour prediction."}

            # 2. Aggregation: Average counts per (dow, hour)
            
            # Calculate exactly how many Mondays, Tuesdays etc are in the dataset range
            unique_dates_per_dow = df.groupby('dow')['fecha'].nunique().to_dict()
            total_flights = df['count'].sum()
            total_days_analyzed = df['fecha'].nunique()
            
            df_agg = df.groupby(['dow', 'hour'])['count'].sum().reset_index()
            
            heatmap_data = []
            
            # 1..7 (ISO DOW: Mon=1, Sun=7)
            for d in range(1, 8): 
                for h in range(24):
                    row = df_agg[(df_agg['dow'] == d) & (df_agg['hour'] == h)]
                    if not row.empty:
                        total_flights_slot = row.iloc[0]['count']
                        num_days = unique_dates_per_dow.get(d, 1)
                        avg = total_flights_slot / max(1, num_days)
                        # Always average for predictive/predictive-like view
                        val = avg
                    else:
                        val = 0
                    
                    heatmap_data.append({
                        "dow": int(d),
                        "hour": int(h),
                        "value": round(val, 1)
                    })
            
            # Format History for Table
            history_data = [
                {
                    "date": row['fecha'].strftime("%Y-%m-%d") if pd.notnull(row['fecha']) else None,
                    "dow": int(row['dow']),
                    "hour": int(row['hour']),
                    "count": int(row['count'])
                }
                for _, row in df.sort_values('fecha', ascending=False).head(1000).iterrows() # Limit to last 1000 records for performance
            ]

            # --- GENERATING PLAIN LANGUAGE EXPLANATION ---
            # 1. Find the Peak Slot
            if heatmap_data:
                peak_slot = max(heatmap_data, key=lambda x: x['value'])
                peak_day_name = ["", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][peak_slot['dow']]
                peak_hour_str = f"{peak_slot['hour']:02d}:00"
                peak_val = int(peak_slot['value'])
                
                # 2. Calculate average load to determinne intensity
                all_values = [x['value'] for x in heatmap_data]
                avg_val = np.mean(all_values)
                intensity_ratio = peak_val / avg_val if avg_val > 0 else 0
                
                intensity_text = "Moderada"
                if intensity_ratio > 2.0: intensity_text = "Muy Alta (Cuello de Botella)"
                elif intensity_ratio > 1.5: intensity_text = "Alta"
                
                description = (
                    f"El análisis de congestión identifica que el momento de mayor tráfico es el **{peak_day_name} a las {peak_hour_str}**, "
                    f"con un volumen promedio de **{peak_val} vuelos**. "
                    f"Esto representa una intensidad **{intensity_text}** ({round(intensity_ratio, 1)}x veces el promedio del sector). "
                    f"Se recomienda planificar recursos de soporte para este bloque horario."
                )

                peak_info = {
                    "day": peak_day_name,
                    "hour": peak_hour_str,
                    "volume": peak_val,
                    "intensity": intensity_text
                }
            else:
                description = "No hay datos suficientes para determinar patrones de congestión."
                peak_info = None

            # --- EXECUTIVE REPORT (STORYTELLING) ---
            intensity_text = peak_info['intensity'] if peak_info else "Baja"
            peak_day = peak_info['day'] if peak_info else "N/A"
            peak_hour = peak_info['hour'] if peak_info else "N/A"
            peak_vol = peak_info['volume'] if peak_info else 0
            
            executive_report = {
                "title": "Informe Ejecutivo de Congestión Horaria",
                "narrative": (
                    f"**Estimado Coordinador de Vuelo:**\n\n"
                    f"El análisis de los patrones horarios revela que la operación enfrenta un nivel de intensidad **{intensity_text.upper()}** en sus momentos críticos. "
                    f"Si tuviera que prestar atención a un solo momento de la semana, sería el **{peak_day} a las {peak_hour}**.\n\n"
                    f"**¿Qué significa esto para la operación?**\n"
                    f"Durante este pico, estamos manejando un volumen de **{peak_vol} vuelos**, lo cual ejerce una presión considerable sobre los recursos del sector. "
                    f"Este no es un evento aislado; es un comportamiento sistemático observado en los últimos {total_days_analyzed} días. "
                    f"Imagine este momento como la 'hora punta' de una autopista: si no regulamos la entrada (ATFM) o aumentamos la capacidad (más controladores/posiciones), la fluidez se detendrá.\n\n"
                    f"**Recomendación Estratégica:**\n"
                    f"Se sugiere programar los descansos del personal fuera de la ventana de {peak_hour} y considerar la activación de sectores colapsables si la intensidad persiste por más de 60 minutos.\n\n"
                    f"**Glosario:**\n"
                    f"- **Mapa de Calor**: Una radiografía visual de la semana. Los colores rojos indican peligro (saturación), los azules indican capacidad ociosa.\n"
                    f"- **Pico de Demanda**: El máximo estrés teórico al que se somete el sector. Diseñamos la capacidad para soportar esto, pero con márgenes estrechos."
                ),
                "key_highlights": [
                    {"label": "Día Crítico", "value": peak_day, "insight": "Mayor concentración semanal"},
                    {"label": "Hora Pico", "value": peak_hour, "insight": "Ventana de máxima carga"},
                    {"label": "Intensidad", "value": intensity_text, "insight": "Nivel de estrés operativo"}
                ]
            }

            return {
                "heatmap": heatmap_data,
                "history": history_data,
                "description": description,
                "metrics": {
                    "total_flights": int(total_flights),
                    "days_analyzed": int(total_days_analyzed),
                    "avg_daily_flights": round(total_flights / max(1, total_days_analyzed), 1),
                    "peak_info": peak_info
                },
                "executive_report": executive_report
            }

        except Exception as e:
            print(f"Error in PredictPeakHours: {e}")
            raise e
        finally:
            conn.close()
