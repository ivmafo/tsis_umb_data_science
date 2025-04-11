from fastapi import APIRouter, HTTPException
from typing import List, Optional
import traceback
from datetime import datetime
from src.core.dtos.flight_dtos import (
    FlightFilterDTO, 
    FlightOriginCountDTO,
    DateRangesAnalysisRequestDTO
)
from src.infraestructure.config.container import DependencyContainer
from pydantic import BaseModel

router = APIRouter()
container = DependencyContainer()

# Common models
class DateRange(BaseModel):
    id: int
    startDate: str
    endDate: str
    label: str

class DateRangesRequest(BaseModel):
    dateRanges: List[DateRange]

# Flight endpoints
@router.get("/years")
async def get_flight_years():
    try:
        years = container.flight_repository.get_distinct_years()
        return {"years": years}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/months")
async def get_flight_months():
    try:
        months = container.flight_repository.get_distinct_months()
        return {"months": months}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/origins")
async def get_flight_origins():
    try:
        origins = container.flight_repository.get_distinct_origins()
        return {"origins": origins}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/destinations")
async def get_flight_destinations():
    try:
        destinations = container.flight_repository.get_distinct_destinations()
        return {"destinations": destinations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/flight-types")
async def get_flight_types():
    try:
        flight_types = container.flight_repository.get_distinct_flight_types()
        return {"flightTypes": flight_types}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/airlines")
async def get_airlines():
    try:
        airlines = container.flight_repository.get_distinct_airlines()
        return {"airlines": airlines}
    except Exception as e:
        print(f"Error in get_airlines endpoint: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/aircraft-types")
async def get_aircraft_types():
    try:
        aircraft_types = container.flight_repository.get_distinct_aircraft_types()
        return {"aircraftTypes": aircraft_types}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/origins-count", response_model=List[FlightOriginCountDTO])
def get_origins_count(
    years: Optional[str] = None,
    months: Optional[str] = None,
    origins: Optional[str] = None,
    destinations: Optional[str] = None,
    flight_types: Optional[str] = None,
    airlines: Optional[str] = None,
    aircraft_types: Optional[str] = None,
    level_min: Optional[int] = None,
    level_max: Optional[int] = None
):
    try:
        years_list = years.split(',') if years else []
        months_list = months.split(',') if months else []
        origins_list = origins.split(',') if origins else []
        destinations_list = destinations.split(',') if destinations else []
        flight_types_list = flight_types.split(',') if flight_types else []
        airlines_list = airlines.split(',') if airlines else []
        aircraft_types_list = aircraft_types.split(',') if aircraft_types else []
        
        filters = FlightFilterDTO(
            years=years_list,
            months=months_list,
            origins=origins_list,
            destinations=destinations_list,
            flight_types=flight_types_list,
            airlines=airlines_list,
            aircraft_types=aircraft_types_list,
            level_min=level_min,
            level_max=level_max
        )
        
        print(f"Origins count filters: {filters.__dict__}")
        return container.flight_repository.get_origins_count(filters)
    except Exception as e:
        print(f"Error in get_origins_count endpoint: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/destinations-count")
async def get_destinations_count(
    years: Optional[str] = None,
    months: Optional[str] = None,
    origins: Optional[str] = None,
    destinations: Optional[str] = None,
    flightTypes: Optional[str] = None,
    airlines: Optional[str] = None,
    aircraftTypes: Optional[str] = None,
    level_min: Optional[int] = None,
    level_max: Optional[int] = None
):
    try:
        filters = FlightFilterDTO(
            years=years.split(',') if years else [],
            months=months.split(',') if months else [],
            origins=origins.split(',') if origins else [],
            destinations=destinations.split(',') if destinations else [],
            flight_types=flightTypes.split(',') if flightTypes else [],
            airlines=airlines.split(',') if airlines else [],
            aircraft_types=aircraftTypes.split(',') if aircraftTypes else [],
            level_min=level_min,
            level_max=level_max
        )
        
        result = container.flight_repository.get_destinations_count(filters)
        return result if result else []
    except Exception as e:
        print(f"Error in get_destinations_count: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/airlines-count")
async def get_airlines_count(
    years: Optional[str] = None,
    months: Optional[str] = None,
    origins: Optional[str] = None,
    destinations: Optional[str] = None,
    flightTypes: Optional[str] = None,
    airlines: Optional[str] = None,
    aircraftTypes: Optional[str] = None,
    level_min: Optional[int] = None,
    level_max: Optional[int] = None
):
    try:
        filters = FlightFilterDTO(
            years=years.split(',') if years else [],
            months=months.split(',') if months else [],
            origins=origins.split(',') if origins else [],
            destinations=destinations.split(',') if destinations else [],
            flight_types=flightTypes.split(',') if flightTypes else [],
            airlines=airlines.split(',') if airlines else [],
            aircraft_types=aircraftTypes.split(',') if aircraftTypes else [],
            level_min=level_min,
            level_max=level_max
        )
        
        result = container.flight_repository.get_airlines_count(filters)
        return result if result else []
    except Exception as e:
        print(f"Error in get_airlines_count: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/flight-types-count")
async def get_flight_types_count(
    years: Optional[str] = None,
    months: Optional[str] = None,
    origins: Optional[str] = None,
    destinations: Optional[str] = None,
    flightTypes: Optional[str] = None,
    airlines: Optional[str] = None,
    aircraftTypes: Optional[str] = None,
    level_min: Optional[int] = None,
    level_max: Optional[int] = None
):
    try:
        filters = FlightFilterDTO(
            years=years.split(',') if years else [],
            months=months.split(',') if months else [],
            origins=origins.split(',') if origins else [],
            destinations=destinations.split(',') if destinations else [],
            flight_types=flightTypes.split(',') if flightTypes else [],
            airlines=airlines.split(',') if airlines else [],
            aircraft_types=aircraftTypes.split(',') if aircraftTypes else [],
            level_min=level_min,
            level_max=level_max
        )
        
        result = container.flight_repository.get_flight_types_count(filters)
        return result if result else []
    except Exception as e:
        print(f"Error in get_flight_types_count: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-date-ranges")
async def analyze_date_ranges(request: DateRangesAnalysisRequestDTO):
    try:
        result = container.flight_repository.get_hourly_counts_by_date_ranges(
            request.date_ranges,
            request.type
        )
        return result
    except Exception as e:
        print(f"Error in analyze_date_ranges: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-date-ranges-destination")
async def analyze_date_ranges_destination(request: DateRangesAnalysisRequestDTO):
    try:
        result = container.flight_repository.get_hourly_counts_by_date_ranges_destination(
            request.date_ranges
        )
        return result
    except Exception as e:
        print(f"Error in analyze_date_ranges_destination: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))