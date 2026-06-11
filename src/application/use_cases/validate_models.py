import duckdb
import pandas as pd
import numpy as np
from datetime import timedelta
from typing import Dict, Any, List
from .predict_daily_demand import PredictDailyDemand
from .predict_seasonal_trend import PredictSeasonalTrend
from .predict_airline_growth import PredictAirlineGrowth

class ValidateModels:
    def __init__(self, db_path: str = "data/metrics.duckdb"):
        self.db_path = db_path
        self.daily_demand = PredictDailyDemand(db_path)
        self.seasonal = PredictSeasonalTrend(db_path)
        self.airline = PredictAirlineGrowth(db_path)

    def execute(self) -> Dict[str, Any]:
        """
        Runs a health check on the predictive models using temporal backtesting.
        Hides the last 90 days of data, forecasts them, and measures MAE/MAPE against physical flights.
        """
        report = []
        overall_status = "Healthy"
        
        # 0. Get max date in flights table to determine backtesting window
        conn = duckdb.connect(self.db_path, read_only=True)
        try:
            max_date_res = conn.execute("SELECT MAX(fecha)::DATE FROM flights").fetchone()
            max_date = max_date_res[0] if max_date_res and max_date_res[0] else None
        except Exception as e:
            print(f"Error querying max date: {e}")
            max_date = None
        finally:
            conn.close()

        if not max_date:
            return {
                "timestamp": pd.Timestamp.now().isoformat(),
                "overall_status": "Critical Issues",
                "validation_report": [{
                    "model": "Validación General",
                    "status": "Critical",
                    "details": "No se encontraron vuelos en la base de datos para realizar la validación."
                }]
            }

        # Cutoff is 90 days before max_date
        cutoff_date = max_date - timedelta(days=90)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d")
        max_str = max_date.strftime("%Y-%m-%d")

        # 1. Backtest Daily Demand (Random Forest)
        try:
            dd_result = self.daily_demand.execute(days_ahead=90, cutoff_date=cutoff_str)
            if "error" not in dd_result:
                # Query actual flight counts for the backtesting period
                conn = duckdb.connect(self.db_path, read_only=True)
                try:
                    actual_df = conn.execute("""
                        SELECT fecha::DATE as ds, COUNT(*) as y 
                        FROM flights 
                        WHERE fecha >= ? AND fecha <= ?
                        GROUP BY 1 ORDER BY 1
                    """, [cutoff_str, max_str]).fetchdf()
                finally:
                    conn.close()

                # Merge predictions and actuals
                pred_dict = {x['date']: x['value'] for x in dd_result['forecast']}
                actual_dict = {
                    row['ds'].strftime("%Y-%m-%d") if hasattr(row['ds'], 'strftime') else str(row['ds']): row['y']
                    for _, row in actual_df.iterrows()
                }

                common_dates = sorted(list(set(pred_dict.keys()) & set(actual_dict.keys())))
                if common_dates:
                    y_true = np.array([actual_dict[d] for d in common_dates])
                    y_pred = np.array([pred_dict[d] for d in common_dates])
                    mae = np.mean(np.abs(y_true - y_pred))
                    mape = np.mean(np.abs(y_true - y_pred) / np.maximum(y_true, 1)) * 100
                    
                    status = "Good" if mape < 15.0 else ("Warning" if mape < 30.0 else "Critical")
                    report.append({
                        "model": "Demanda Diaria (Backtesting 90d)",
                        "metric": "MAPE (%)",
                        "value": round(mape, 2),
                        "threshold": "< 15.0%",
                        "status": status,
                        "details": f"Error Absoluto Medio (MAE): {round(mae, 2)} vuelos/día. Evaluado sobre {len(common_dates)} días de prueba."
                    })
                else:
                    report.append({
                        "model": "Demanda Diaria (Backtesting 90d)",
                        "status": "Warning",
                        "details": "No se encontraron fechas comunes en la ventana de backtesting para calcular errores."
                    })
            else:
                report.append({"model": "Demanda Diaria (Backtesting 90d)", "status": "Error", "details": dd_result["error"]})
        except Exception as e:
            report.append({"model": "Demanda Diaria (Backtesting 90d)", "status": "Error", "details": str(e)})

        # 2. Backtest Seasonal Trend (Regresión Lineal con Calendario)
        try:
            st_result = self.seasonal.execute(start_date=cutoff_str, end_date=max_str, cutoff_date=cutoff_str)
            if "error" not in st_result:
                # Query actual flight counts
                conn = duckdb.connect(self.db_path, read_only=True)
                try:
                    actual_df = conn.execute("""
                        SELECT fecha::DATE as ds, COUNT(*) as y 
                        FROM flights 
                        WHERE fecha >= ? AND fecha <= ?
                        GROUP BY 1 ORDER BY 1
                    """, [cutoff_str, max_str]).fetchdf()
                finally:
                    conn.close()

                # Merge predictions and actuals
                pred_dict = {x['date']: x['value'] for x in st_result['forecast']}
                actual_dict = {
                    row['ds'].strftime("%Y-%m-%d") if hasattr(row['ds'], 'strftime') else str(row['ds']): row['y']
                    for _, row in actual_df.iterrows()
                }

                common_dates = sorted(list(set(pred_dict.keys()) & set(actual_dict.keys())))
                if common_dates:
                    y_true = np.array([actual_dict[d] for d in common_dates])
                    y_pred = np.array([pred_dict[d] for d in common_dates])
                    mae = np.mean(np.abs(y_true - y_pred))
                    mape = np.mean(np.abs(y_true - y_pred) / np.maximum(y_true, 1)) * 100
                    
                    status = "Good" if mape < 20.0 else ("Warning" if mape < 40.0 else "Critical")
                    report.append({
                        "model": "Tendencia Estacional (Backtesting 90d)",
                        "metric": "MAPE (%)",
                        "value": round(mape, 2),
                        "threshold": "< 20.0%",
                        "status": status,
                        "details": f"Error Absoluto Medio (MAE): {round(mae, 2)} vuelos/día. Evaluado sobre {len(common_dates)} días de prueba."
                    })
                else:
                    report.append({
                        "model": "Tendencia Estacional (Backtesting 90d)",
                        "status": "Warning",
                        "details": "No se encontraron fechas comunes en la ventana de backtesting."
                    })
            else:
                report.append({"model": "Tendencia Estacional (Backtesting 90d)", "status": "Error", "details": st_result["error"]})
        except Exception as e:
            report.append({"model": "Tendencia Estacional (Backtesting 90d)", "status": "Error", "details": str(e)})

        # 3. Validate Airline Growth (Keep legacy training check as it is a market share ranker)
        try:
            ag_result = self.airline.execute()
            if "results" in ag_result and ag_result['results']:
                top_3 = ag_result['results'][:3]
                avg_r2 = np.mean([x['reliability'] for x in top_3]) if top_3 else 0
                status = "Good" if avg_r2 > 0.5 else "Warning"
                report.append({
                    "model": "Crecimiento Aerolíneas",
                    "metric": "R² Promedio (Top 3)",
                    "value": round(avg_r2, 2),
                    "threshold": "> 0.5",
                    "status": status,
                    "details": f"Evaluado sobre {len(ag_result['results'])} aerolíneas activas."
                })
        except Exception as e:
            report.append({"model": "Crecimiento Aerolíneas", "status": "Error", "details": str(e)})

        # Overall Status Logic
        if any(r.get('status') == 'Critical' for r in report):
            overall_status = "Critical Issues"
        elif any(r.get('status') == 'Warning' for r in report):
            overall_status = "Warnings Detected"

        return {
            "timestamp": pd.Timestamp.now().isoformat(),
            "overall_status": overall_status,
            "validation_report": report
        }
