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
    days: int = Query(30, description="Horizonte de predicción en días (ej. 7, 30, 90)"),
    sector_id: Optional[str] = Query(None, description="Filtrar proyección para un sector ATC específico"),
    airport: Optional[str] = Query(None, description="Filtrar por vuelos asociados a un aeropuerto (OACI)"),
    route: Optional[str] = Query(None, description="Filtrar por una ruta específica (formato ORIGEN-DESTINO)"),
    min_level: Optional[int] = Query(None, description="Nivel de vuelo mínimo para el filtrado predictivo"),
    max_level: Optional[int] = Query(None, description="Nivel de vuelo máximo para el filtrado predictivo"),
    use_case: PredictDailyDemand = Depends(get_predict_daily_demand_use_case)
):
    """
    Obtiene la proyección de demanda diaria (conteo de vuelos) utilizando un modelo de Random Forest Regressor.
    Este endpoint analiza patrones históricos para estimar la carga futura en diferentes dimensiones temporales.
    
    Args:
        days (int): Cantidad de días a futuro para proyectar.
        sector_id, airport, route, min_level, max_level: Filtros multidimensionales para segmentar la demanda.
        use_case (PredictDailyDemand): Motor predictivo inyectado.
        
    Returns:
        Dict: Series históricas y proyecciones con intervalos de confianza.
    """
    try:
        return use_case.execute(days_ahead=days, sector_id=sector_id, airport=airport, route=route, min_level=min_level, max_level=max_level)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/peak-hours")
def get_peak_hours_forecast(
    sector_id: Optional[str] = Query(None, description="ID del sector para el análisis de calor"),
    airport: Optional[str] = Query(None, description="Filtro por aeropuerto"),
    route: Optional[str] = Query(None, description="Filtro por ruta"),
    min_level: Optional[int] = Query(None, description="Altitud mínima"),
    max_level: Optional[int] = Query(None, description="Altitud máxima"),
    start_date: Optional[str] = Query(None, description="Fecha inicio para análisis estacional"),
    end_date: Optional[str] = Query(None, description="Fecha fin para análisis estacional"),
    aggregation: str = Query("avg", description="Método de agregación de carga: 'avg' (promedio) o 'sum' (total)"),
    use_case: PredictPeakHours = Depends(get_predict_peak_hours_use_case)
):
    """
    Genera una radiografía (Heatmap) de la intensidad de tráfico por hora y día de la semana.
    Permite identificar visualmente los 'cuellos de botella' operativos recurrentes.
    
    Args:
        sector_id, airport, route, min_level, max_level: Dimensiones de filtrado espacial y técnico.
        start_date, end_date: Si se proveen, el modelo cambia a modo de análisis estacional histórico.
        aggregation (str): Define si se visualiza el promedio típico o la acumulación total de flujos.
        use_case (PredictPeakHours): Orquestador de análisis térmico de tráfico.
        
    Returns:
        Dict: Matriz de calor formateada para PeakHoursHeatmap.tsx.
    """
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
    months: int = Query(12, description="Meses de historia para el análisis de tendencia de mercado"),
    sector_id: Optional[str] = Query(None, description="Filtro por sector"),
    airport: Optional[str] = Query(None, description="Filtro por aeropuerto"),
    route: Optional[str] = Query(None, description="Filtro por ruta específica"),
    min_level: Optional[int] = Query(None, description="Filtro por nivel"),
    max_level: Optional[int] = Query(None, description="Filtro por nivel"),
    use_case: PredictAirlineGrowth = Depends(get_predict_airline_growth_use_case)
):
    """
    Analiza la evolución del market share (cuota de mercado) para las aerolíneas principales.
    Calcula tasas de crecimiento utilizando regresión lineal sobre el historial operativo.
    
    Args:
        months (int): Profundidad del historial para el entrenamiento del modelo.
        use_case (PredictAirlineGrowth): Lógica de análisis de evolución corporativa.
        
    Returns:
        Dict: Ranking de aerolíneas con mayor crecimiento y proyecciones individuales.
    """
    try:
        return use_case.execute(months_history=months, sector_id=sector_id, airport=airport, route=route, min_level=min_level, max_level=max_level)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sector-saturation/{sector_id}")
def get_sector_saturation_forecast(
    sector_id: str,
    days: int = Query(30, description="Días a proyectar"),
    use_case: PredictSectorSaturation = Depends(get_predict_sector_saturation_use_case)
):
    """
    Cruza la capacidad técnica declarada del sector con la demanda futura proyectada.
    Emite el Índice de Saturación (%) y determina el estado de alerta operativa (Normal, Alerta, Crítico).
    
    Args:
        sector_id (str): Sector ATC objetivo del análisis de riesgo.
        days (int): Ventana de pronóstico.
        use_case (PredictSectorSaturation): Orquestador que vincula capacidad y demanda.
        
    Returns:
        Dict: Reporte de riesgo con descripción en lenguaje natural e indicadores clave.
    """
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
    start_date: str = Query(..., description="Fecha de inicio del periodo estacional (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Fecha de fin del periodo estacional (YYYY-MM-DD)"),
    sector_id: Optional[str] = Query(None, description="ID del sector"),
    airport: Optional[str] = Query(None, description="Filtro por aeropuerto"),
    route: Optional[str] = Query(None, description="Filtro por ruta"),
    min_level: Optional[int] = Query(None, description="Filtro nivel min"),
    max_level: Optional[int] = Query(None, description="Filtro nivel máx"),
    use_case: PredictSeasonalTrend = Depends(get_predict_seasonal_trend_use_case)
):
    """
    Genera un pronóstico de largo plazo basado en la descomposición de series temporales (Fourier).
    Captura ciclos anuales y semanales para proyectar la tendencia estructural de la demanda aeronáutica.
    
    Args:
        start_date/end_date (str): Ventana futura para la proyección estacional.
        use_case (PredictSeasonalTrend): Modelo híbrido (Fourier + Regresión Lineal).
        
    Returns:
        Dict: Descomposición de la serie, reporte ejecutivo y proyecciones de confianza.
    """
    try:
        return use_case.execute(start_date=start_date, end_date=end_date, sector_id=sector_id, airport=airport, route=route, min_level=min_level, max_level=max_level)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
