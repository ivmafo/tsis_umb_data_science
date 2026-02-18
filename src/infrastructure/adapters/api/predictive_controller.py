from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from src.application.use_cases.predict_daily_demand import PredictDailyDemand
from src.application.use_cases.predict_peak_hours import PredictPeakHours
from src.application.use_cases.predict_airline_growth import PredictAirlineGrowth
from src.application.use_cases.predict_sector_saturation import PredictSectorSaturation
from src.application.use_cases.predict_seasonal_trend import PredictSeasonalTrend
from src.application.di.container import (
    get_predict_daily_demand_use_case,
    get_predict_peak_hours_use_case,
    get_predict_airline_growth_use_case,
    get_predict_peak_hours_use_case,
    get_predict_airline_growth_use_case,
    get_predict_sector_saturation_use_case,
    get_predict_seasonal_trend_use_case
)

router = APIRouter(prefix="/predictive", tags=["Predictive"])

@router.get("/daily-demand")
def get_daily_demand_forecast(
    days: int = Query(30, description="Days to forecast"),
    sector_id: Optional[str] = None,
    airport: Optional[str] = None,
    route: Optional[str] = None,
    min_level: Optional[int] = None,
    max_level: Optional[int] = None,
    use_case: PredictDailyDemand = Depends(get_predict_daily_demand_use_case)
):
    """Forecast detailed daily flight volume."""
    try:
        return use_case.execute(days_ahead=days, sector_id=sector_id, airport=airport, route=route, min_level=min_level, max_level=max_level)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/peak-hours")
def get_peak_hours_forecast(
    sector_id: Optional[str] = None,
    airport: Optional[str] = None,
    route: Optional[str] = None,
    min_level: Optional[int] = None,
    max_level: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    aggregation: str = Query("avg", description="Aggregation method: 'avg' or 'sum'"),
    use_case: PredictPeakHours = Depends(get_predict_peak_hours_use_case)
):
    """Forecast weekly peak hour heatmap."""
    try:
        return use_case.execute(
            sector_id=sector_id, 
            airport=airport, 
            route=route, 
            min_level=min_level, 
            max_level=max_level,
            start_date=start_date,
            end_date=end_date,
            aggregation=aggregation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/airline-growth")
def get_airline_growth_forecast(
    months: int = Query(12, description="Months of history to analyze"),
    sector_id: Optional[str] = None,
    airport: Optional[str] = None,
    route: Optional[str] = None,
    min_level: Optional[int] = None,
    max_level: Optional[int] = None,
    use_case: PredictAirlineGrowth = Depends(get_predict_airline_growth_use_case)
):
    """Forecast airline market share trends."""
    try:
        return use_case.execute(months_history=months, sector_id=sector_id, airport=airport, route=route, min_level=min_level, max_level=max_level)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sector-saturation/{sector_id}")
def get_sector_saturation_forecast(
    sector_id: str,
    days: int = Query(30, description="Days to forecast"),
    use_case: PredictSectorSaturation = Depends(get_predict_sector_saturation_use_case)
):
    """Forecast sector saturation (Demand vs Capacity)."""
    try:
        result = use_case.execute(sector_id, days_ahead=days)
        if "error" in result:
             raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/seasonal-trend")
def get_seasonal_trend_forecast(
    start_date: str,
    end_date: str,
    sector_id: Optional[str] = None,
    airport: Optional[str] = None,
    route: Optional[str] = None,
    min_level: Optional[int] = None,
    max_level: Optional[int] = None,
    use_case: PredictSeasonalTrend = Depends(get_predict_seasonal_trend_use_case)
):
    """Forecast long-term seasonal trend using Fourier decomposition (10 Annual + 3 Weekly Orders)."""
    try:
        return use_case.execute(start_date=start_date, end_date=end_date, sector_id=sector_id, airport=airport, route=route, min_level=min_level, max_level=max_level)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
