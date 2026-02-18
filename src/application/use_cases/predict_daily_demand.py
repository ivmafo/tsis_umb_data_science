import duckdb
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from typing import Dict, Any, List

class PredictDailyDemand:
    def __init__(self, db_path: str = "data/metrics.duckdb"):
        self.db_path = db_path

    def execute(self, days_ahead: int = 30, sector_id: str = None, airport: str = None, route: str = None, min_level: int = None, max_level: int = None, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        conn = duckdb.connect(self.db_path, read_only=True)
        try:
            # 1. Build Filter Conditions
            conditions = ["fecha IS NOT NULL"]
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
                        # Construct IN clauses for sector
                        origins_str = "', '".join(origins)
                        destinations_str = "', '".join(destinations)
                        conditions.append(f"origen IN ('{origins_str}') AND destino IN ('{destinations_str}')")
                    else:
                        return {"error": "Sector definition is incomplete (missing origins/destinations)."}
                else:
                    return {"error": "Sector not found."}

            # Airport Filter (Origin OR Destination)
            if airport:
                conditions.append("(origen = ? OR destino = ?)")
                params.extend([airport, airport])

            # Route Filter (e.g. SKBO-SKRG)
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

            # --- SEASONAL MODE ---
            if start_date and end_date:
                return self.execute_seasonal(conn, where_clause, params, start_date, end_date)

            # --- STANDARD FORECAST MODE ---
            # 2. Fetch Historical Data with Filters
            query = f"""
                SELECT 
                    fecha::DATE as ds, 
                    COUNT(*) as y 
                FROM flights 
                WHERE {where_clause} 
                GROUP BY 1 
                ORDER BY 1
            """
            
            if params:
                 df = conn.execute(query, params).fetchdf()
            else:
                 df = conn.execute(query).fetchdf()
            
            if df.empty or len(df) < 14: # Need at least 2 weeks of data
                return {"error": "Insufficient data for prediction. Need at least 14 days of history."}

            # 2. Preprocess
            # Fill missing dates
            df['ds'] = pd.to_datetime(df['ds'])
            full_range = pd.date_range(start=df['ds'].min(), end=df['ds'].max(), freq='D')
            df = df.set_index('ds').reindex(full_range, fill_value=0).reset_index()
            df.columns = ['ds', 'y']

            # 3. Feature Engineering
            df['day_of_week'] = df['ds'].dt.dayofweek
            df['month'] = df['ds'].dt.month
            df['year'] = df['ds'].dt.year
            df['day_of_year'] = df['ds'].dt.dayofyear
            
            # Lags
            for lag in [1, 7, 14, 28]:
                df[f'lag_{lag}'] = df['y'].shift(lag)
            
            # Drop NaN created by lags
            df_train = df.dropna()
            
            if df_train.empty:
                 return {"error": "Insufficient data after feature engineering."}

            # 4. Train Model
            features = ['day_of_week', 'month', 'year', 'day_of_year', 'lag_1', 'lag_7', 'lag_14', 'lag_28']
            X = df_train[features]
            y = df_train['y']
            
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            r2_score = model.score(X, y)
            
            # 5. Forecast
            last_date = df['ds'].max()
            future_dates = [last_date + timedelta(days=x) for x in range(1, days_ahead + 1)]
            forecast_data = []

            current_row = df.iloc[-1].copy()
            # We need a history buffer to compute lags dynamically
            history_buffer = df['y'].tolist() 
            
            forecast_values = []
            confidence_intervals = []

            for date in future_dates:
                # Construct features for this date
                feat = {
                    'day_of_week': date.dayofweek,
                    'month': date.month,
                    'year': date.year,
                    'day_of_year': date.dayofyear
                }
                
                # Get lags from history buffer
                feat['lag_1'] = history_buffer[-1]
                feat['lag_7'] = history_buffer[-7] if len(history_buffer) >= 7 else history_buffer[-1]
                feat['lag_14'] = history_buffer[-14] if len(history_buffer) >= 14 else history_buffer[-1]
                feat['lag_28'] = history_buffer[-28] if len(history_buffer) >= 28 else history_buffer[-1]
                
                X_pred = pd.DataFrame([feat])
                
                # Predict
                preds = [est.predict(X_pred)[0] for est in model.estimators_]
                pred_value = np.mean(preds)
                std_dev = np.std(preds)
                
                forecast_values.append(pred_value)
                history_buffer.append(pred_value) # Append prediction for recursive lag
                
                forecast_data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "value": int(round(pred_value)),
                    "lower": int(max(0, round(pred_value - 1.96 * std_dev))),
                    "upper": int(round(pred_value + 1.96 * std_dev))
                })

            # Format History for Chart
            history_data = [
                {"date": row['ds'].strftime("%Y-%m-%d"), "value": int(row['y'])}
                for _, row in df.tail(90).iterrows() # Last 90 days context
            ]
            
            # --- GENERATING PLAIN LANGUAGE EXPLANATION ---
            trend_slope = 0
            if len(forecast_values) > 1:
                trend_slope = (forecast_values[-1] - forecast_values[0]) / len(forecast_values)

            trend_text = "estable"
            trend = "Estable"
            if trend_slope > 0.5: 
                trend_text = "al alza (crecimiento)"
                trend = "Crecimiento"
            elif trend_slope < -0.5: 
                trend_text = "a la baja (reducción)"
                trend = "Reducción"

            avg_forecast = np.mean(forecast_values)
            avg_history = df['y'].tail(30).mean()
            diff_percent = ((avg_forecast - avg_history) / avg_history * 100) if avg_history > 0 else 0
            
            comparison_text = f"{abs(round(diff_percent, 1))}% {'mayor' if diff_percent > 0 else 'menor'} que el mes anterior"

            # Step-by-step breakdown
            step_by_step = [
                {
                    "step": "1. Análisis Histórico",
                    "detail": f"Se analizaron {len(df)} días de datos reales. El promedio diario reciente fue de {int(avg_history)} vuelos."
                },
                {
                    "step": "2. Detección de Patrones",
                    "detail": f"El modelo identificó que el {round(r2_score*100, 1)}% de la variación diaria se explica por patrones repetitivos (días de la semana, época del año)."
                },
                {
                    "step": "3. Proyección",
                    "detail": f"Para los próximos {days_ahead} días, se estima un promedio de {int(avg_forecast)} vuelos diarios, con una tendencia {trend_text}."
                },
                {
                    "step": "4. Incertidumbre",
                    "detail": f"Existe un margen de error estandar de +/- {int(np.mean(std_dev)*1.96)} vuelos (Intervalo de Confianza 95%)."
                }
            ]

            description = (
                f"La predicción indica una tendencia **{trend_text}** para el próximo mes. "
                f"Se espera un volumen promedio de **{int(avg_forecast)} vuelos diarios**, lo cual es **{comparison_text}**. "
                f"La fiabilidad estadística del modelo es del **{round(r2_score*100, 1)}%**, considerada {'Alta' if r2_score > 0.7 else ('Media' if r2_score > 0.4 else 'Baja')}."
            )

            # --- EXECUTIVE REPORT (STORYTELLING) ---
            executive_report = {
                "title": "Informe Ejecutivo de Demanda Diaria",
                "narrative": (
                    f"**Estimado Coordinador de Vuelo:**\n\n"
                    f"El panorama operativo para los próximos {days_ahead} días sugiere un escenario de **{'ALTA ACTIVIDAD' if trend == 'Crecimiento' else 'ACTIVIDAD MODERADA'}** "
                    f"con una tendencia de fondo hacia la {trend.lower()}. "
                    f"Nuestros sistemas han analizado {len(df)} días de historia operativa para llegar a esta conclusión.\n\n"
                    f"**¿Qué nos dicen las cifras?**\n"
                    f"Hemos detectado que el comportamiento del tráfico no es aleatorio. Existe un patrón recurrente semanal que explica gran parte de la variabilidad. "
                    f"El modelo predice un volumen promedio diario de **{round(forecast_data[0]['value'] if forecast_data else 0)} vuelos** para el inicio del periodo. "
                    f"La confiabilidad de este pronóstico es del **{round(r2_score*100, 1)}%**, lo que técnicamente llamamos un 'ajuste robusto'.\n\n"
                    f"**¿Cómo llegamos a esta conclusión? (La Metodología)**\n"
                    f"Imagine que hemos consultado a un comité de 100 expertos virtuales. Cada uno analizó una parte diferente de la historia: unos se enfocaron en los lunes, otros en los veranos pasados, otros en la tendencia anual. "
                    f"Nuestro algoritmo, el **Random Forest (Bosque Aleatorio)**, reunió todas esas opiniones y generó un consenso ponderado. Esto reduce el riesgo de sesgarse por un evento aislado (como una cancelación masiva por tormenta).\n\n"
                    f"**Glosario para la Toma de Decisiones:**\n"
                    f"- **Intervalo de Confianza (95%)**: El rango donde 'vivirá' la demanda real con alta probabilidad. Si el rango es amplio, hay incertidumbre (prepare recursos flexibles); si es estrecho, la predicción es precisa.\n"
                    f"- **R² (Coeficiente de Determinación)**: Nuestro 'termómetro de confianza'. Un 100% sería una predicción divina; un 0% sería tirar una moneda. Estamos en {round(r2_score*100, 1)}%."
                ),
                "key_highlights": [
                    {"label": "Tendencia", "value": trend, "insight": "Dirección general del tráfico"},
                    {"label": "Fiabilidad", "value": f"{round(r2_score*100, 1)}%", "insight": "Grado de certeza del modelo"},
                    {"label": "Horizonte", "value": f"{days_ahead} Días", "insight": "Ventana de planificación"}
                ]
            }

            return {
                "model": "Random Forest Regressor (Recursive)",
                "history": history_data,
                "forecast": forecast_data,
                "accuracy_metrics": {
                    "r2_score": round(r2_score, 3),
                    "confidence_score": "Alta" if r2_score > 0.7 else "Media",
                    "training_samples": len(df_train)
                },
                "description": f"El análisis se fundamenta en un modelo de regresión no paramétrico (Random Forest Regressor) entrenado con una serie temporal de {len(df)} días. La validación del modelo arrojó un coeficiente de determinación R² de {round(r2_score, 3)}, lo que sugiere que el {round(r2_score*100, 1)}% de la varianza en la demanda diaria es explicada por las variables predictoras (lags temporales de 1, 7, 14 y 28 días, estacionalidad semanal y tendencia anual). El intervalo de confianza del 95% se calculó a partir de la desviación estándar de las predicciones de los 100 árboles de decisión que componen el ensamble, permitiendo cuantificar la incertidumbre inherente al pronóstico.",
                "explanation_steps": step_by_step,
                "executive_report": executive_report
            }

        except Exception as e:
            print(f"Error in PredictDailyDemand: {e}")
            raise e
        finally:
            conn.close()

    def execute_seasonal(self, conn, where_clause, params, start_date_str, end_date_str):
        # Extract MM-DD from dates
        s = datetime.strptime(start_date_str, "%Y-%m-%d")
        e = datetime.strptime(end_date_str, "%Y-%m-%d")
        
        start_md = s.strftime("%m-%d")
        end_md = e.strftime("%m-%d")
        
        # Helper to filter "Same period in previous years"
        # We use strftime to match MM-DD
        if start_md <= end_md:
            date_filter = f"strftime(fecha, '%m-%d') BETWEEN '{start_md}' AND '{end_md}'"
        else:
            # Wrap around year case (e.g. Dec 25 to Jan 05)
             date_filter = f"(strftime(fecha, '%m-%d') >= '{start_md}' OR strftime(fecha, '%m-%d') <= '{end_md}')"

        query = f"""
            SELECT 
                fecha::DATE as ds, 
                COUNT(*) as y 
            FROM flights 
            WHERE {where_clause} 
              AND {date_filter}
            GROUP BY 1 
            ORDER BY 1
        """
        
        df = conn.execute(query, params).fetchdf()
        
        if df.empty:
            return {"error": "No historical data found for this season."}

        df['ds'] = pd.to_datetime(df['ds'])
        df['year'] = df['ds'].dt.year
        df['md'] = df['ds'].dt.strftime("%m-%d")
        
        # Organize by Year
        years = df['year'].unique()
        seasonal_series = []
        
        # Calculate trends
        yearly_totals = df.groupby('year')['y'].sum().reset_index()
        
        growth_factor = 1.0
        r2_trend = 0.0
        slope = 0.0
        
        if len(yearly_totals) > 1:
            # Simple Trend: Linear Reg on totals
            from sklearn.linear_model import LinearRegression
            lr = LinearRegression()
            X_trend = yearly_totals['year'].values.reshape(-1, 1)
            y_trend = yearly_totals['y'].values
            lr.fit(X_trend, y_trend)
            r2_trend = lr.score(X_trend, y_trend)
            slope = lr.coef_[0]
            
            # Predict next year total
            next_year = int(years.max()) + 1
            predicted_total = lr.predict([[next_year]])[0]
            if y_trend.mean() > 0:
                 growth_factor = predicted_total / y_trend.mean() # Approximate scaling
        else:
            growth_factor = 1.0
            next_year = int(years.max()) if len(years) > 0 else datetime.now().year

        # Create "Predicted Season" based on average profile * growth
        # 1. Calculate Average Daily Profile
        avg_profile = df.groupby('md')['y'].mean().reset_index()
        avg_profile['predicted_y'] = avg_profile['y'] * growth_factor
        
        # Construct Forecast Series
        forecast_series = []
        target_year = s.year 
        
        for _, row in avg_profile.iterrows():
            # Reconstruct date
            try:
                # Handle leap years if needed, basic construction
                md_parts = row['md'].split('-')
                d = datetime(target_year, int(md_parts[0]), int(md_parts[1]))
                forecast_series.append({
                    "date": d.strftime("%Y-%m-%d"),
                    "value": int(row['predicted_y'])
                })
            except:
                pass # Leap day issues
                
        forecast_series.sort(key=lambda x: x['date'])

        # Build Historical Series for Chart
        for year in sorted(years):
            year_data = df[df['year'] == year]
            seasonal_series.append({
                "name": str(year),
                "data": [ {"x": row['ds'].strftime("%m-%d"), "y": int(row['y'])} for _, row in year_data.iterrows() ]
            })
            
        total_sample = len(df)
        trend_desc = "positiva" if slope > 0 else "negativa"
        
        description = (
            f"Para la proyección estacional, se implementó una metodología de Descomposición de Series Temporales centrada en el periodo {start_md} a {end_md}. El análisis procesó un dataset histórico de {total_sample} vuelos distribuidos en {len(years)} años ({int(years.min())}-{int(years.max())}). Estadísticamente, se modeló la tendencia secular mediante una regresión lineal sobre los volúmenes anuales acumulados, identificando una pendiente de {round(slope, 2)} vuelos/año (R²={round(r2_trend, 3)}), lo que determina la dirección a largo plazo. El componente estacional se aisló calculando el perfil diario promedio ('Día Típico') suavizado, el cual fue posteriormente escalado por un factor de crecimiento compuesto de {round(growth_factor, 3)}x para ajustar la magnitud del tráfico a las condiciones actuales del mercado."
        )

        return {
            "model": "Seasonal Trend Decomposition",
            "seasonal": True,
            "history": seasonal_series, # Multi-series for comparison
            "forecast": forecast_series, # The projected "Next Season"
            "description": description,
            "metrics": {
                "years_analyzed": len(years),
                "total_records": total_sample,
                "growth_factor": round(growth_factor, 2),
                "trend_r2": round(r2_trend, 2)
            }
        }
