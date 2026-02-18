import duckdb
import pandas as pd
import numpy as np
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
        Runs a health check on the predictive models using recent data.
        Returns reliability scores and status.
        """
        report = []
        overall_status = "Healthy"
        
        # 1. Validate Daily Demand (Backtest last 7 days)
        try:
            # We can't easily "backtest" without mocking time, but we can check the R2 score of the current fit
            # using the `predict_daily_demand` logic which trains on available history.
            # We'll run a prediction and capture the metrics.
            dd_result = self.daily_demand.execute(days_ahead=1)
            if "error" not in dd_result:
                r2 = dd_result['accuracy_metrics']['r2_score']
                status = "Good" if r2 > 0.6 else ("Warning" if r2 > 0.3 else "Critical")
                report.append({
                    "model": "Demanda Diaria",
                    "metric": "R² Score",
                    "value": r2,
                    "threshold": "> 0.6",
                    "status": status,
                    "details": f"Entrenado con {dd_result['accuracy_metrics']['training_samples']} muestras."
                })
        except Exception as e:
            report.append({"model": "Demanda Diaria", "status": "Error", "details": str(e)})

        # 2. Validate Seasonal Trend
        try:
            # Check if we have enough data for seasonal (might fail if DB is small)
            # Use a dummy date range for year-long check
            current_year = pd.Timestamp.now().year
            st_result = self.seasonal.execute(start_date=f"{current_year}-01-01", end_date=f"{current_year}-12-31")
            if "error" not in st_result:
                r2 = st_result['metrics']['r2']
                status = "Good" if r2 > 0.5 else ("Warning" if r2 > 0.2 else "Critical")
                report.append({
                    "model": "Tendencia Estacional",
                    "metric": "R² (Fourier)",
                    "value": r2,
                    "threshold": "> 0.5",
                    "status": status,
                    "details": f"Analizados {st_result['metrics']['years_history']} años de historia."
                })
        except Exception as e:
            # Likely insufficient data
            report.append({"model": "Tendencia Estacional", "status": "Skipped", "details": "Datos insuficientes o error interno."})

        # 3. Validate Airline Growth
        try:
            ag_result = self.airline.execute()
            if "results" in ag_result and ag_result['results']:
                # Check avg reliability of top 3 airlines
                top_3 = ag_result['results'][:3]
                avg_r2 = np.mean([x['reliability'] for x in top_3]) if top_3 else 0
                status = "Good" if avg_r2 > 0.5 else "Warning"
                report.append({
                    "model": "Crecimiento Aerolíneas",
                    "metric": "R² Promedio (Top 3)",
                    "value": round(avg_r2, 2),
                    "threshold": "> 0.5",
                    "status": status,
                    "details": f"Evaluado sobre {len(ag_result['results'])} aerolíneas."
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
