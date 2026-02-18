import duckdb
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from typing import Dict, Any, List
from datetime import datetime

class PredictAirlineGrowth:
    """
    Monitor de evolución de mercado y crecimiento de aerolíneas.
    Calcula la tasa de crecimiento mensual/anual de los operadores principales
    utilizando regresión lineal para identificar tendencias de expansión o contracción.
    """
    def __init__(self, db_path: str = "data/metrics.duckdb"):
        """
        Inicializa el monitor.
        """
        self.db_path = db_path

    def execute(self, months_history: int = 12, sector_id: str = None, airport: str = None, route: str = None, min_level: int = None, max_level: int = None, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        Calcula las métricas de crecimiento para las 10 aerolíneas líderes.
        
        Args:
            months_history (int): Cantidad de meses hacia atrás para el análisis.
            sector_id (str): Filtro espacial por sector.
            airport (str): Filtro por aeropuerto clave.
            route (str): Filtro por ruta comercial.
            min_level/max_level: Filtros de niveles de vuelo.
            start_date/end_date: Modo estacional si se proveen.
            
        Returns:
            Dict: Ranking de crecimiento, reporte ejecutivo y series temporales por operador.
        """
        conn = duckdb.connect(self.db_path, read_only=True)
        try:
            # 1. Build Base Filter
            conditions = []
            params = []
            
            # Date Logic
            if start_date and end_date:
                # SEASONAL MODE
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
                # STANDARD MODE
                conditions.append("fecha >= CURRENT_DATE - INTERVAL '1 YEAR'")
                is_seasonal = False

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

            if airport:
                conditions.append("(origen = ? OR destino = ?)")
                params.extend([airport, airport])

            if route:
                parts = route.split('-')
                if len(parts) == 2:
                    conditions.append("origen = ? AND destino = ?")
                    params.extend([parts[0], parts[1]])
            
            if min_level is not None:
                conditions.append("nivel >= ?")
                params.append(min_level)
            
            if max_level is not None:
                conditions.append("nivel <= ?")
                params.append(max_level)

            where_clause = " AND ".join(conditions) if conditions else "1=1"

            # 2. Fetch Top 10 Airlines filtered
            query_top = f"""
                SELECT empresa, COUNT(*) as total 
                FROM flights 
                WHERE {where_clause}
                GROUP BY 1 
                ORDER BY 2 DESC 
                LIMIT 10
            """
            
            if params:
                top_airlines_df = conn.execute(query_top, params).fetchdf()
            else:
                top_airlines_df = conn.execute(query_top).fetchdf()

            # Filter out None/NaN and ensure strings
            top_airlines = [str(x) for x in top_airlines_df['empresa'].tolist() if x and str(x).lower() != 'nan']
            
            if not top_airlines:
                return {"results": [], "seasonal": is_seasonal, "description": "No data found"}

            # 3. Fetch Data for Top Airlines
            placeholders = ','.join(['?::VARCHAR'] * len(top_airlines))
            all_params = params + top_airlines

            if is_seasonal:
                # Group by Year
                query_data = f"""
                    SELECT 
                        empresa,
                        EXTRACT(YEAR FROM fecha) as year_val,
                        COUNT(*) as count
                    FROM flights
                    WHERE 
                        {where_clause}
                        AND empresa IN ({placeholders})
                    GROUP BY 1, 2
                    ORDER BY 1, 2
                """
            else:
                # Group by Month
                query_data = f"""
                    SELECT 
                        empresa,
                        strftime(fecha, '%Y-%m') as time_step,
                        COUNT(*) as count
                    FROM flights
                    WHERE 
                        {where_clause}
                        AND empresa IN ({placeholders})
                    GROUP BY 1, 2
                    ORDER BY 1, 2
                """
            
            df = conn.execute(query_data, all_params).fetchdf()
            results = []
            
            total_history_points = 0
            
            for airline in top_airlines:
                airline_df = df[df['empresa'] == airline].copy()
                if len(airline_df) < 2: 
                    continue
                    
                total_history_points += len(airline_df)
                
                if is_seasonal:
                    # Seasonal Trend (Yearly)
                    X = airline_df['year_val'].values.reshape(-1, 1)
                    y = airline_df['count'].values
                    time_labels = airline_df['year_val'].astype(int).astype(str).tolist()
                else:
                    # Monthly Trend
                    airline_df['month_idx'] = range(len(airline_df))
                    X = airline_df[['month_idx']]
                    y = airline_df['count']
                    time_labels = airline_df['time_step'].tolist()

                if len(X) > 1:
                    model = LinearRegression()
                    model.fit(X, y)
                    slope = model.coef_[0]
                    # Forecast next step
                    next_step = X.iloc[-1, 0] + 1 if hasattr(X, 'iloc') else X[-1][0] + 1
                    
                    # Prepare input for prediction with correct feature names if X was a DataFrame
                    if hasattr(X, 'columns'):
                         import pandas as pd
                         next_step_input = pd.DataFrame([[next_step]], columns=X.columns)
                    else:
                         next_step_input = [[next_step]]
                         
                    prediction = model.predict(next_step_input)[0]
                    r2 = model.score(X, y)
                else:
                    slope = 0
                    prediction = y[0]
                    r2 = 0
                
                results.append({
                    "airline": airline,
                    "growth_rate": round(slope, 2), 
                    "current_volume": int(airline_df.iloc[-1]['count']),
                    "forecast_next": int(max(0, round(prediction))),
                    "trend_direction": "Positive" if slope > 0.5 else ("Negative" if slope < -0.5 else "Stable"),
                    "reliability": round(r2, 2),
                    "history": [
                        {"label": str(t), "value": int(v)} 
                        for t, v in zip(time_labels, y)
                    ]
                })
            
            results.sort(key=lambda x: x['growth_rate'], reverse=True)
            
            total_airlines_analyzed = len(results)
            top_grower = results[0]['airline'] if results else "N/A"
            top_growth = results[0]['growth_rate'] if results else 0
            
            # --- GENERATING PLAIN LANGUAGE EXPLANATION ---
            # Identify noteworthy airlines
            growing_airlines = [r for r in results if r['trend_direction'] == 'Positive']
            declining_airlines = [r for r in results if r['trend_direction'] == 'Negative']
            stable_airlines = [r for r in results if r['trend_direction'] == 'Stable']
            
            market_summary = ""
            if len(growing_airlines) > len(declining_airlines):
                market_summary = "un mercado en expansión"
            elif len(declining_airlines) > len(growing_airlines):
                market_summary = "una contracción general"
            else:
                market_summary = "estabilidad en el mercado"

            if is_seasonal:
                 min_year = int(df['year_val'].min()) if not df.empty else "N/A"
                 max_year = int(df['year_val'].max()) if not df.empty else "N/A"
                 
                 description = (
                    f"El análisis estacional del periodo {min_year}-{max_year} sugiere **{market_summary}**. "
                    f"**{top_grower}** lidera el crecimiento, sumando aproximadamente **{round(top_growth, 1)} vuelos adicionales por temporada**. "
                 )
            else:
                 description = (
                    f"El análisis de los últimos 12 meses muestra **{market_summary}**. "
                    f"La aerolínea destacada es **{top_grower}**, con una tendencia de crecimiento de **{top_growth} vuelos/mes**. "
                    f"De las {total_airlines_analyzed} aerolíneas analizadas, {len(growing_airlines)} muestran crecimiento y {len(declining_airlines)} reducción."
                 )

            # --- EXECUTIVE REPORT (STORYTELLING) ---
            market_state = "EXPANSIÓN" if market_summary == "un mercado en expansión" else ("CONTRACCIÓN" if "contracción" in market_summary else "ESTABILIDAD")
            
            executive_report = {
                "title": "Informe Ejecutivo de Evolución de Mercado",
                "narrative": (
                    f"**Estimado Coordinador de Vuelo:**\n\n"
                    f"El ecosistema de aerolíneas se encuentra actualmente en una fase de **{market_state}**.\n"
                    f"Al analizar el comportamiento de los operadores en el último periodo, observamos que **{len(growing_airlines)} compañías están aumentando su oferta**, "
                    f"mientras que {len(declining_airlines)} están reduciendo frecuencias.\n\n"
                    f"**El Protagonista del Mercado:**\n"
                    f"La aerolínea **{top_grower}** se destaca como el actor más dinámico, inyectando **{round(top_growth, 1)} vuelos adicionales** por ciclo. "
                    f"Esto no es solo un dato estadístico; implica que veremos más aeronaves de este operador en nuestros sectores, lo cual podría requerir ajustes en las asignaciones de slots o posiciones en plataforma.\n\n"
                    f"**Glosario:**\n"
                    f"- **Tendencia (Slope)**: La velocidad de cambio. Una pendiente positiva significa que la aerolínea está 'acelerando' su presencia; negativa significa que se está retirando.\n"
                    f"- **Regresión Lineal**: Trazamos una línea recta que mejor representa el caos de los datos mensuales para entender la dirección real del mercado."
                ),
                "key_highlights": [
                    {"label": "Estado del Mercado", "value": market_state, "insight": "Dinámica global"},
                    {"label": "Líder de Crecimiento", "value": top_grower, "insight": "Operador principal"},
                    {"label": "Tasa de Crecimiento", "value": f"+{round(top_growth, 1)}/mes", "insight": "Velocidad de expansión"}
                ]
            }

            return {
                "results": results,
                "seasonal": is_seasonal,
                "description": description,
                "metrics": {
                    "total_airlines": total_airlines_analyzed,
                    "total_data_points": total_history_points,
                    "top_airline": top_grower,
                    "top_growth_rate": top_growth,
                    "growing_count": len(growing_airlines),
                    "declining_count": len(declining_airlines)
                },
                "executive_report": executive_report
            }

        except Exception as e:
            print(f"Error in PredictAirlineGrowth: {e}")
            raise e
        finally:
            conn.close()
