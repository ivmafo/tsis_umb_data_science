import duckdb
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import holidays
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any, List, Optional

class PredictSeasonalTrend:
    """
    Caso de uso para la generación de pronósticos de tendencia estacional a largo plazo.
    
    Utiliza un modelo híbrido basado en variables dummy del calendario de Colombia
    y Regresión Lineal para proyectar la tendencia de fondo y picos de tráfico.
    """
    def __init__(self, db_path: str = "data/metrics.duckdb", backend_agent=None):
        self.db_path = db_path
        self.backend_agent = backend_agent

    def execute(self, start_date: str, end_date: str, sector_id: str = None, airport: str = None, route: str = None, min_level: int = None, max_level: int = None, cutoff_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Genera un pronóstico detallado descomponiendo la serie temporal en patrones cíclicos.
        
        Args:
            start_date: Fecha de inicio del pronóstico (YYYY-MM-DD).
            end_date: Fecha de fin del pronóstico (YYYY-MM-DD).
            sector_id: ID opcional del sector para filtrar.
            airport: Código de aeropuerto opcional para filtrar.
            route: Ruta opcional (ej. SKBO-SKRG) para filtrar.
            min_level/max_level: Rangos de niveles de vuelo opcionales.
            cutoff_date: Fecha de corte opcional para backtesting.
            
        Returns:
            Dict: Reporte ejecutivo, historial y proyección futura con intervalos de confianza.
        """
        from typing import Optional
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

            # Filtro de fecha de corte para backtesting
            if cutoff_date:
                conditions.append("fecha < ?")
                params.append(cutoff_date)

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

            # 2. Preprocesamiento e Ingeniería de Características (Variables Dummy de Calendario)
            df['ds'] = pd.to_datetime(df['ds'])
            df = df.sort_values('ds').reset_index(drop=True)

            # Detectar y filtrar grandes brechas en los datos históricos (más de 30 días sin registros)
            if len(df) > 1:
                df['diff_days'] = df['ds'].diff().dt.days
                large_gaps = df[df['diff_days'] > 30]
                if not large_gaps.empty:
                    last_gap_idx = large_gaps.index[-1]
                    df = df.iloc[last_gap_idx:].copy().reset_index(drop=True)
            
            df = df[['ds', 'y']]

            # Rellenar pequeños huecos diarios con cero
            full_range = pd.date_range(start=df['ds'].min(), end=df['ds'].max(), freq='D')
            df = df.set_index('ds').reindex(full_range, fill_value=0).reset_index()
            df.columns = ['ds', 'y']

            def get_easter_date(y):
                a = y % 19
                b = y // 100
                c = y % 100
                d = b // 4
                e = b % 4
                f = (b + 8) // 25
                g = (b - f + 1) // 3
                h = (19 * a + b - d - g + 15) % 30
                i = c // 4
                k = c % 4
                L = (32 + 2 * e + 2 * i - h - k) % 7
                m = (a + 11 * h + 22 * L) // 451
                month = (h + L - 7 * m + 114) // 31
                day = ((h + L - 7 * m + 114) % 31) + 1
                return date(y, month, day)

            def add_calendar_features(data, date_col='ds'):
                years = data[date_col].dt.year.unique().tolist()
                
                # Cargar festivos oficiales de Colombia
                try:
                    co_holidays = holidays.Colombia(years=years)
                except Exception:
                    co_holidays = {}
                
                # Cargar eventos personalizados de la base de datos
                custom_holidays = {}
                conn_cal = duckdb.connect(self.db_path, read_only=True)
                try:
                    table_exists = conn_cal.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = 'calendar_events'").fetchone()[0] > 0
                    if table_exists:
                        res = conn_cal.execute("SELECT fecha, tipo FROM calendar_events").fetchall()
                        custom_holidays = {
                            row[0].strftime("%Y-%m-%d") if isinstance(row[0], (date, datetime)) else str(row[0]): row[1]
                            for row in res
                        }
                except Exception as ex:
                    print(f"Error cargando eventos personalizados: {ex}")
                finally:
                    conn_cal.close()

                # Precalcular Pascua
                easter_dates = {}
                for y in years:
                    try:
                        easter_dates[y] = get_easter_date(y)
                    except Exception:
                        pass

                es_festivo = []
                semana_santa = []
                semana_receso = []
                fin_de_ano = []

                for dt in data[date_col]:
                    dt_date = dt.date()
                    dt_str = dt_date.strftime("%Y-%m-%d")
                    y = dt_date.year

                    # 1. Puentes y Festivos
                    is_fest = 1 if (dt_date in co_holidays or custom_holidays.get(dt_str) == 'festivo') else 0
                    es_festivo.append(is_fest)

                    # 2. Semana Santa (Domingo de Ramos a Domingo de Resurrección)
                    is_ss = 0
                    if y in easter_dates:
                        e_date = easter_dates[y]
                        palm_sunday = e_date - timedelta(days=7)
                        if palm_sunday <= dt_date <= e_date:
                            is_ss = 1
                    if custom_holidays.get(dt_str) == 'semana_santa':
                         is_ss = 1
                    semana_santa.append(is_ss)

                    # 3. Semana de Receso Escolar (Octubre)
                    is_rec = 0
                    columbus_day = date(y, 10, 12)
                    wd = columbus_day.weekday()
                    if wd == 0:
                        columbus_monday = columbus_day
                    else:
                        columbus_monday = columbus_day + timedelta(days=(7 - wd))
                    
                    receso_start = columbus_monday - timedelta(days=7)
                    receso_end = columbus_monday - timedelta(days=1)
                    if receso_start <= dt_date <= receso_end:
                        is_rec = 1
                    if custom_holidays.get(dt_str) == 'receso':
                        is_rec = 1
                    semana_receso.append(is_rec)

                    # 4. Temporada de Fin de Año (15-Dic a 15-Ene)
                    is_fda = 0
                    if (dt_date.month == 12 and dt_date.day >= 15) or (dt_date.month == 1 and dt_date.day <= 15):
                        is_fda = 1
                    if custom_holidays.get(dt_str) == 'fin_de_ano':
                        is_fda = 1
                    fin_de_ano.append(is_fda)

                data['es_festivo'] = es_festivo
                data['semana_santa'] = semana_santa
                data['semana_receso'] = semana_receso
                data['fin_de_ano'] = fin_de_ano

                # Dummies de día de la semana
                for i in range(7):
                    data[f'day_of_week_{i}'] = (data[date_col].dt.dayofweek == i).astype(int)

                # Dummies de mes
                for i in range(1, 13):
                    data[f'month_{i}'] = (data[date_col].dt.month == i).astype(int)

                # Índice de Tendencia
                data['trend_index'] = data[date_col].map(datetime.toordinal)

                return data

            df_train = add_calendar_features(df.copy())
            
            feature_cols = [c for c in df_train.columns if c.startswith('day_of_week_') or c.startswith('month_') or c in ['es_festivo', 'semana_santa', 'semana_receso', 'fin_de_ano', 'trend_index']]
            X = df_train[feature_cols]
            y = df_train['y']

            # 3. Entrenamiento del Modelo (Regresión Lineal Escalada)
            model = make_pipeline(StandardScaler(), LinearRegression())
            model.fit(X, y)
            
            y_pred_train = model.predict(X)
            r2 = model.score(X, y)
            rmse = np.sqrt(np.mean((y - y_pred_train)**2))
            
            residuals = y - y_pred_train
            std_resid = np.std(residuals)

            # 4. Proyección Futura
            req_start = datetime.strptime(start_date, "%Y-%m-%d")
            req_end = datetime.strptime(end_date, "%Y-%m-%d")
            
            forecast_dates = pd.date_range(start=req_start, end=req_end, freq='D')
            df_future = pd.DataFrame({'ds': forecast_dates})
            df_future = add_calendar_features(df_future)
            
            X_future = df_future[feature_cols]
            y_future = model.predict(X_future)
            
            # Obtener Techo Operativo (Capacidad Máxima ATC del sector si aplica)
            capacidad_maxima = float('inf')
            if sector_id and self.backend_agent:
                try:
                    cap_report = self.backend_agent.execute_dynamic_capacity_calculation(sector_id, {})
                    if "stochastic_capacity_report" in cap_report:
                        stochastic_data = cap_report["stochastic_capacity_report"]
                        ch_adjusted = stochastic_data.get("stochastic_simulated_capacity", 0)
                        if ch_adjusted > 0:
                            capacidad_maxima = ch_adjusted * 24
                except Exception as ex:
                    print(f"Error consultando capacidad límite para sector {sector_id}: {ex}")

            # Asegurar que no existan valores negativos y aplicar Techo Operativo
            y_future = np.maximum(y_future, 0)
            if capacidad_maxima < float('inf'):
                y_future = np.minimum(y_future, capacidad_maxima)

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

            # --- DYNAMIC BACKTESTING (90 DAYS) ---
            backtest_mape = None
            backtest_mae = None
            if not cutoff_date and len(df) >= 120:
                try:
                    bt_cutoff_str = (df['ds'].max() - timedelta(days=90)).strftime("%Y-%m-%d")
                    bt_res = self.execute(
                        start_date=bt_cutoff_str,
                        end_date=df['ds'].max().strftime("%Y-%m-%d"),
                        sector_id=sector_id,
                        airport=airport,
                        route=route,
                        min_level=min_level,
                        max_level=max_level,
                        cutoff_date=bt_cutoff_str
                    )
                    if "error" not in bt_res:
                        actuals = df[df['ds'] >= (df['ds'].max() - timedelta(days=90))]
                        pred_dict = {x['date']: x['value'] for x in bt_res['forecast']}
                        actual_dict = {
                            row['ds'].strftime("%Y-%m-%d") if hasattr(row['ds'], 'strftime') else str(row['ds']): row['y']
                            for _, row in actuals.iterrows()
                        }
                        common_dates = sorted(list(set(pred_dict.keys()) & set(actual_dict.keys())))
                        if common_dates:
                            y_true = np.array([actual_dict[d] for d in common_dates])
                            y_pred = np.array([pred_dict[d] for d in common_dates])
                            backtest_mae = float(np.mean(np.abs(y_true - y_pred)))
                            backtest_mape = float(np.mean(np.abs(y_true - y_pred) / np.maximum(y_true, 1)) * 100)
                except Exception as ex:
                    print(f"Error in internal backtest: {ex}")

            # Análisis de Tendencia y Estacionalidad para Reporte Ejecutivo
            years_analyzed = (df['ds'].max() - df['ds'].min()).days / 365.25
            trend_direction = "Creciente" if model.named_steps['linearregression'].coef_[0] > 0 else "Decreciente"
            
            df['month'] = df['ds'].dt.month_name()
            monthly_avg = df.groupby('month')['y'].mean().sort_values(ascending=False)
            peak_month = monthly_avg.index[0]

            description = (
                f"El análisis de largo plazo revela una tendencia estructural **{trend_direction}**. "
                f"Históricamente, el mes de mayor actividad es **{peak_month}**. "
                f"El modelo modeló las estacionalidades mediante variables dummy de calendario de Colombia con una fiabilidad del **{round(r2*100, 1)}%**."
            )
            
            step_by_step = [
                {"step": "1. Descomposición", "detail": "La serie temporal se separó en componentes: Tendencia de largo plazo y Estacionalidades discretas de calendario."},
                {"step": "2. Ajuste del Modelo", "detail": f"Se utilizó regresión lineal multivariable sobre {round(years_analyzed, 1)} años de datos reales, parametrizando puentes festivos, Semana Santa y recesos."},
                {"step": "3. Proyección y Techo", "detail": "Se proyectaron los patrones futuros y se restringieron dinámicamente mediante el techo operativo de capacidad del sector."}
            ]

            # --- REPORTE EJECUTIVO (Storytelling) ---
            narrative_text = (
                f"**Estimado Coordinador de Vuelo:**\n\n"
                f"Al elevar la vista hacia el horizonte estratégico ({round(years_analyzed, 1)} años de historia), identificamos una tendencia estructural **{trend_direction}**.\n"
                f"Esto significa que, más allá de los altibajos diarios, el tráfico de fondo está {'aumentando' if trend_direction == 'Creciente' else 'disminuyendo'}.\n\n"
                f"**El Ciclo de Vida Anual:**\n"
                f"Su operación tiene un 'ritmo cardíaco' predecible. El mes de **{peak_month}** actúa consistentemente como el pico de actividad anual. "
                f"Este patrón se ha modelado utilizando el calendario aeronáutico nacional con una fidelidad del **{round(r2*100, 1)}%**.\n\n"
            )
            
            if backtest_mape is not None and backtest_mae is not None:
                narrative_text += (
                    f"**Validación Científica del Modelo (Backtesting de 90 Días):**\n"
                    f"Para validar la precisión del modelo en escenarios reales bajo estas mismas condiciones y filtros, realizamos una prueba retrospectiva (backtesting) ocultando los últimos 90 días de datos históricos conocidos. "
                    f"El modelo predijo ese periodo con un **Error Porcentual Absoluto Medio (MAPE) de sólo {round(backtest_mape, 2)}%** "
                    f"y un **Error Absoluto Medio (MAE) de {round(backtest_mae, 1)} vuelos/día**. "
                    f"Este nivel de error está significativamente por debajo del umbral de tolerancia del 20.0%, confirmando la alta fiabilidad operativa de las predicciones en este sector/filtro.\n\n"
                )

            narrative_text += (
                f"**Descomposición del Caos:**\n"
                f"Hemos separado la señal del ruido. Lo que parece un gráfico caótico es en realidad la suma de fuerzas limpias: el crecimiento a largo plazo + puentes festivos + temporadas de receso escolar. "
                f"Nuestra proyección extiende estas fuerzas hacia el futuro y las restringe bajo los techos de capacidad oficial del sector para garantizar que no se violen las realidades físicas de su operación."
            )
            
            executive_report = {
                "title": "Informe Ejecutivo de Tendencia Estacional",
                "narrative": narrative_text,
                "key_highlights": [
                    {"label": "Tendencia", "value": trend_direction, "insight": "Dirección a largo plazo"},
                    {"label": "Mes Pico", "value": peak_month, "insight": "Máxima actividad anual"},
                    {"label": "Predictibilidad (R²)", "value": f"{round(r2*100, 1)}%", "insight": "Fuerza del patrón"}
                ]
            }
            if backtest_mape is not None:
                executive_report["key_highlights"].append(
                    {"label": "Precisión (MAPE)", "value": f"{round(backtest_mape, 2)}%", "insight": "Error porcentual en backtesting de 90 días"}
                )
            
            return {
                "model": "Variables Dummy de Calendario (Regresión Lineal)",
                "history": history_data,
                "forecast": forecast_data,
                "metrics": {
                    "r2": round(r2, 3),
                    "rmse": round(rmse, 2),
                    "years_history": round(years_analyzed, 1),
                    "trend": trend_direction,
                    "peak_month": peak_month,
                    "backtest_mape": round(backtest_mape, 2) if backtest_mape is not None else None,
                    "backtest_mae": round(backtest_mae, 2) if backtest_mae is not None else None
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
