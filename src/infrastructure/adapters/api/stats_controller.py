from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Dict, Any
from src.application.use_cases.get_flight_stats import GetFlightStats

router = APIRouter(prefix="/stats", tags=["stats"])

def get_stats_use_case():
    return GetFlightStats()

@router.post("/flights-by-origin")
def get_flights_by_origin(
    filters: Dict[str, Any] = Body(...),
    use_case: GetFlightStats = Depends(get_stats_use_case)
):
    """
    Get flight counts aggregated by origin, filtered by the provided criteria.
    """
    try:
        return use_case.execute(filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from src.application.use_cases.get_destination_stats import GetDestinationStats

def get_dest_stats_use_case():
    return GetDestinationStats()

@router.post("/flights-by-destination")
def get_flights_by_destination(
    filters: Dict[str, Any] = Body(...),
    use_case: GetDestinationStats = Depends(get_dest_stats_use_case)
):
    """
    Get flight counts aggregated by destination, filtered by the provided criteria.
    """
    try:
        return use_case.execute(filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from src.application.use_cases.get_flight_type_stats import GetFlightTypeStats

def get_flight_type_stats_use_case():
    return GetFlightTypeStats()

@router.post("/flights-by-type")
def get_flights_by_type(
    filters: Dict[str, Any] = Body(...),
    use_case: GetFlightTypeStats = Depends(get_flight_type_stats_use_case)
):
    """
    Get flight counts aggregated by flight type (tipo_vuelo), filtered by the provided criteria.
    """
    try:
        return use_case.execute(filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from src.application.use_cases.get_company_stats import GetCompanyStats

def get_company_stats_use_case():
    return GetCompanyStats()

@router.post("/flights-by-company")
def get_flights_by_company(
    filters: Dict[str, Any] = Body(...),
    use_case: GetCompanyStats = Depends(get_company_stats_use_case)
):
    """
    Get flight counts aggregated by company (empresa), filtered by the provided criteria.
    """
    try:
        return use_case.execute(filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from src.application.use_cases.get_time_stats import GetTimeStats
from src.application.use_cases.get_peak_hour_stats import GetPeakHourStats

def get_time_stats_use_case():
    return GetTimeStats()

@router.post("/flights-over-time")
def get_flights_over_time(
    filters: Dict[str, Any] = Body(...),
    use_case: GetTimeStats = Depends(get_time_stats_use_case)
):
    """
    Get flight counts aggregated by time (YYYY/MM), filtered by the provided criteria.
    """
    try:
        return use_case.execute(filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_peak_hour_stats_use_case():
    return GetPeakHourStats()

@router.post("/flights-peak-hours")
def get_flights_peak_hours(
    filters: Dict[str, Any] = Body(...),
    use_case: GetPeakHourStats = Depends(get_peak_hour_stats_use_case)
):
    """
    Get flight counts aggregated by Day of Week and Hour (Heatmap).
    """
    try:
        return use_case.execute(filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from src.application.use_cases.get_region_stats import GetRegionStats

def get_region_stats_use_case():
    return GetRegionStats()

@router.post("/flights-by-region")
def get_flights_by_region(
    filters: Dict[str, Any] = Body(...),
    use_case: GetRegionStats = Depends(get_region_stats_use_case)
):
    """
    Get flight counts aggregated by Region and Origin.
    """
    try:
        return use_case.execute(filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from src.application.use_cases.get_region_destination_stats import GetRegionDestinationStats

def get_region_dest_stats_use_case():
    return GetRegionDestinationStats()

@router.post("/flights-by-region-destination")
def get_flights_by_region_destination(
    filters: Dict[str, Any] = Body(...),
    use_case: GetRegionDestinationStats = Depends(get_region_dest_stats_use_case)
):
    """
    Get flight counts aggregated by Region and Destination.
    """
    try:
        return use_case.execute(filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
