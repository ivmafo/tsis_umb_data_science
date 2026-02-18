import duckdb
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any, List

class PredictSeasonalTrend:
    """
    Caso de uso para la generación de pronósticos de tendencia estacional a largo plazo.
    
    Utiliza un modelo híbrido basado en Análisis de Fourier para capturar ciclos anuales/semanales
    y Regresión Lineal para proyectar la tendencia de fondo.
    """
    def __init__(self, db_path: str = "data/metrics.duckdb"):
        self.db_path = db_path

    def execute(self, start_date: str, end_date: str, sector_id: str = None, airport: str = None, route: str = None, min_level: int = None, max_level: int = None) -> Dict[str, Any]:
        """
        Genera un pronóstico detallado descomponiendo la serie temporal en patrones cíclicos.
        
        Args:
            start_date: Fecha de inicio del pronóstico (YYYY-MM-DD).
            end_date: Fecha de fin del pronóstico (YYYY-MM-DD).
            sector_id: ID opcional del sector para filtrar.
            airport: Código de aeropuerto opcional para filtrar.
            route: Ruta opcional (ej. SKBO-SKRG) para filtrar.
            min_level/max_level: Rangos de niveles de vuelo opcionales.
            
        Returns:
            Dict: Reporte ejecutivo, historial y proyección futura con intervalos de confianza.
        """
        conn = duckdb.connect(self.db_path, read_only=True)
        try:
            # 1. Construcción de la Consulta con filtros dinámicos
            conditions = ["fecha IS NOT NULL"]
            params = []

            # Filtrado por definición de sector (orígenes/destinos)
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

            # Filtros por aeropuerto único (origen o destino)
            if airport:
                conditions.append("(origen = ? OR destino = ?)")
                params.extend([airport, airport])

            # Filtros por ruta específica
            if route:
                parts = route.split('-')
                if len(parts) == 2:
                    conditions.append("origen = ? AND destino = ?")
                    params.extend([parts[0], parts[1]])
            
            # Filtros de niveles de vuelo
            if min_level is not None:
                conditions.append("nivel >= ?")
                params.append(min_level)
            
            if max_level is not None:
                conditions.append("nivel <= ?")
                params.append(max_level)

            where_clause = " AND ".join(conditions)

            # Obtener historial completo de vuelos para el entrenamiento
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

            # Validar suficiencia de datos históricos
            if df.empty or len(df) < 30:
                return {"error": "Datos históricos insuficientes para la descomposición estacional (mínimo 30 días)."}

            # 2. Preprocesamiento e Ingeniería de Características (Términos de Fourier)
            df['ds'] = pd.to_datetime(df['ds'])
            
            # Rellenar huecos de días sin vuelos con cero para mantener la continuidad matemática
            full_range = pd.date_range(start=df['ds'].min(), end=df['ds'].max(), freq='D')
            df = df.set_index('ds').reindex(full_range, fill_value=0).reset_index()
            df.columns = ['ds', 'y']

            def add_fourier_terms(data, date_col='ds'):
                """
                Genera términos de seno y coseno para modelar la estacionalidad periódica.
                """
                # Ciclo Anual (365.25 días). Orden 10 para capturar picos complejos.
                t_year = data[date_col].dt.dayofyear
                for k in range(1, 11):
                    data[f'sin_year_{k}'] = np.sin(2 * np.pi * k * t_year / 365.25)
                    data[f'cos_year_{k}'] = np.cos(2 * np.pi * k * t_year / 365.25)
                
                # Ciclo Semanal (7 días). Orden 3 para diferencias entre fin de semana y semana.
                t_week = data[date_col].dt.dayofweek
                for k in range(1, 4):
                    data[f'sin_week_{k}'] = np.sin(2 * np.pi * k * t_week / 7)
                    data[f'cos_week_{k}'] = np.cos(2 * np.pi * k * t_week / 7)
                
                # Índice de Tendencia (Ordinal temporal)
                data['trend_index'] = data[date_col].map(datetime.toordinal)
                
                return data

            df_train = add_fourier_terms(df.copy())
            
            feature_cols = [c for c in df_train.columns if c.startswith('sin_') or c.startswith('cos_') or c == 'trend_index']
            X = df_train[feature_cols]
            y = df_train['y']

            # 3. Entrenamiento del Modelo (Regresión Lineal Escalada)
            model = make_pipeline(StandardScaler(), LinearRegression())
            model.fit(X, y)
            
            # Cálculo de métricas de precisión
            y_pred_train = model.predict(X)
            r2 = model.score(X, y) # Coeficiente de determinación
            rmse = np.sqrt(np.mean((y - y_pred_train)**2)) # Error cuadrático medio
            
            # Desviación estándar de los residuales para intervalos de confianza (95%)
            residuals = y - y_pred_train
            std_resid = np.std(residuals)

            # 4. Proyección Futura
            req_start = datetime.strptime(start_date, "%Y-%m-%d")
            req_end = datetime.strptime(end_date, "%Y-%m-%d")
            
            forecast_dates = pd.date_range(start=req_start, end=req_end, freq='D')
            df_future = pd.DataFrame({'ds': forecast_dates})
            df_future = add_fourier_terms(df_future)
            
            X_future = df_future[feature_cols]
            y_future = model.predict(X_future)
            
            # Asegurar que no existan valores negativos en la demanda
            y_future = np.maximum(y_future, 0)

            # 5. Construcción de la Respuesta detallada
            forecast_data = []
            for d, val in zip(forecast_dates, y_future):
                forecast_data.append({
                    "date": d.strftime("%Y-%m-%d"),
                    "value": int(round(val)),
                    "lower": int(max(0, round(val - 1.96 * std_resid))),
                    "upper": int(round(val + 1.96 * std_resid))
                })

            # Retornar los últimos 2 años de historia para contexto visual
            history_data = [
                {"date": row['ds'].strftime("%Y-%m-%d"), "value": int(row['y'])}
                for _, row in df.tail(365 * 2).iterrows() 
            ]

            # Análisis de Tendencia y Estacionalidad para Reporte Ejecutivo
            years_analyzed = (df['ds'].max() - df['ds'].min()).days / 365.25
            trend_direction = "Creciente" if model.named_steps['linearregression'].coef_[0] > 0 else "Decreciente"
            
            # Identificación del mes pico basado en promedios históricos
            df['month'] = df['ds'].dt.month_name()
            monthly_avg = df.groupby('month')['y'].mean().sort_values(ascending=False)
            peak_month = monthly_avg.index[0]

            description = (
                f"El análisis de largo plazo revela una tendencia estructural **{trend_direction}**. "
                f"Históricamente, el mes de mayor actividad es **{peak_month}**. "
                f"El modelo descompuso la serie en patrones anuales y semanales con una fiabilidad del **{round(r2*100, 1)}%**."
            )
            
            step_by_step = [
                {"step": "1. Descomposición", "detail": "La serie temporal se separó en tres componentes: Tendencia (Largo Plazo), Estacionalidad Anual (Ciclos de 12 meses) y Estacionalidad Semanal (Días de la semana)."},
                {"step": "2. Ajuste del Modelo", "detail": f"Se utilizó regresión lineal armónica (Fourier) sobre {round(years_analyzed, 1)} años de datos."},
                {"step": "3. Proyección", "detail": "Se extendieron los patrones cíclicos detectados hacia el futuro, sumando la tendencia de fondo."}
            ]

            # --- REPORTE EJECUTIVO (Storytelling) ---
            executive_report = {
                "title": "Informe Ejecutivo de Tendencia Estacional",
                "narrative": (
                    f"**Estimado Coordinador de Vuelo:**\n\n"
                    f"Al elevar la vista hacia el horizonte estratégico ({round(years_analyzed, 1)} años de historia), identificamos una tendencia estructural **{trend_direction}**.\n"
                    f"Esto significa que, más allá de los altibajos diarios, el tráfico de fondo está {'aumentando' if trend_direction == 'Creciente' else 'disminuyendo'}.\n\n"
                    f"**El Ciclo de Vida Anual:**\n"
                    f"Su operación tiene un 'ritmo cardíaco' predecible. El mes de **{peak_month}** actúa consistentemente como el pico de actividad anual. "
                    f"Este patrón se ha repetido con una fidelidad del **{round(r2*100, 1)}%** en los últimos años. "
                    f"Saber esto nos permite salir del modo reactivo ('apagar fuegos') y pasar al preventivo: sabemos cuándo vendrá la ola, así que podemos preparar la tabla de surf con meses de antelación.\n\n"
                    f"**Descomposición del Caos:**\n"
                    f"Hemos separado la señal del ruido. Lo que parece un gráfico caótico es en realidad la suma de tres fuerzas limpias: el crecimiento a largo plazo + el ciclo anual + la rutina semanal. "
                    f"Nuestra proyección extiende estas fuerzas hacia el futuro para darle el mejor mapa de ruta posible."
                ),
                "key_highlights": [
                    {"label": "Tendencia", "value": trend_direction, "insight": "Dirección a largo plazo"},
                    {"label": "Mes Pico", "value": peak_month, "insight": "Máxima actividad anual"},
                    {"label": "Predictibilidad", "value": f"{round(r2*100, 1)}%", "insight": "Fuerza del patrón"}
                ]
            }
            
            return {
                "model": "Descomposición de Fourier (Regresión Lineal)",
                "history": history_data,
                "forecast": forecast_data,
                "metrics": {
                    "r2": round(r2, 3),
                    "rmse": round(rmse, 2),
                    "years_history": round(years_analyzed, 1),
                    "trend": trend_direction,
                    "peak_month": peak_month
                },
                "description": description,
                "explanation_steps": step_by_step,
                "executive_report": executive_report
            }

        except Exception as e:
            print(f"Error en PredictSeasonalTrend: {e}")
            raise e
        finally:
            conn.close()
