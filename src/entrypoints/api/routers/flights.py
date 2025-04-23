from fastapi import APIRouter, HTTPException
from typing import List, Optional
import traceback
from datetime import datetime
from src.core.dtos.flight_dtos import (
    FlightFilterDTO, 
    FlightOriginCountDTO,
    DateRangesAnalysisRequestDTO,
    FlightDestinationCountDTO,
    FlightAirlineCountDTO,
    FlightTypeCountDTO
)
from src.infraestructure.config.container import DependencyContainer
from pydantic import BaseModel, validator  # Agregamos el import de validator

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

class DateRangeDTO(BaseModel):
    id: str
    start_date: str
    end_date: str
    label: str
    origin_airport: str
    destination_airport: str
    nivel_min: int = 0
    nivel_max: int = 99999

    class Config:
        validate_assignment = True

    @validator('nivel_min', 'nivel_max', pre=True)
    def validate_levels(cls, v):
        if v is None:
            return 0 if cls.current_field_name == 'nivel_min' else 99999
        return int(v)

class DateRangesAnalysisRequestDTO(BaseModel):
    date_ranges: List[DateRangeDTO]
    type: str = 'origin'  # Valor por defecto

@router.post("/analyze-date-ranges")
async def analyze_date_ranges(request: DateRangesAnalysisRequestDTO):
    try:
        print("Debug - Received request:", request.dict())
        result = container.flight_repository.get_hourly_counts_by_date_ranges(
            request.date_ranges,
            request.type
        )
        print("Debug - Result:", result)
        return result
    except Exception as e:
        print("Error in analyze_date_ranges:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=422, detail=str(e))

@router.post("/analyze-date-ranges-destination")
async def analyze_date_ranges_destination(request: DateRangesAnalysisRequestDTO):
    try:
        print("=== Debug: analyze-date-ranges-destination endpoint ===")
        print("Received request:", request.dict())
        
        result = container.flight_repository.get_hourly_counts_by_date_ranges_destination(
            request.date_ranges
        )
        print("Analysis result:", result)
        return result
    except Exception as e:
        print(f"Error in analyze_date_ranges_destination: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=422, detail=str(e))

@router.get("/aircraft-types")
async def get_aircraft_types():
    try:
        types = container.flight_repository.get_aircraft_types()
        return {"aircraftTypes": types}
    except Exception as e:
        print(f"Error in get_aircraft_types endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/airlines")
async def get_airlines():
    try:
        airlines = container.flight_repository.get_airlines()
        return {"airlines": airlines}
    except Exception as e:
        print(f"Error in get_airlines endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/months")
async def get_months():
    try:
        months = container.flight_repository.get_months()
        return {"months": months}
    except Exception as e:
        print(f"Error in get_months endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/origins")
async def get_origins():
    try:
        origins = container.flight_repository.get_origins()
        return {"origins": origins}
    except Exception as e:
        print(f"Error in get_origins endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/destinations")
async def get_destinations():
    try:
        destinations = container.flight_repository.get_destinations()
        return {"destinations": destinations}
    except Exception as e:
        print(f"Error in get_destinations endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/airlines-count")
async def get_airlines_count():
    try:
        repository = container.flight_repository
        counts = repository.get_airlines_count()
        return counts
    except Exception as e:
        print(f"Error in get_airlines_count endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/flight-types")
async def get_flight_types():
    try:
        types = container.flight_repository.get_flight_types()
        return types
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/origins-count", response_model=List[FlightOriginCountDTO])
async def get_origins_count(
    years: Optional[str] = None,
    months: Optional[str] = None,
    origins: Optional[str] = None,
    destinations: Optional[str] = None,
    flight_types: Optional[str] = None,
    airlines: Optional[str] = None,
    aircraft_types: Optional[str] = None,
    level_ranges: Optional[str] = None,
    level_min: Optional[int] = None,
    level_max: Optional[int] = None
):
    try:
        filters = FlightFilterDTO(
            years=years.split(',') if years else [],
            months=months.split(',') if months else [],
            origins=origins.split(',') if origins else [],
            destinations=destinations.split(',') if destinations else [],
            flight_types=flight_types.split(',') if flight_types else [],
            airlines=airlines.split(',') if airlines else [],
            aircraft_types=aircraft_types.split(',') if aircraft_types else [],
            level_ranges=level_ranges.split(',') if level_ranges else [],
            level_min=level_min,
            level_max=level_max
        )
        
        return container.get_flight_origins_count_use_case.execute(filters)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/destinations-count")
async def get_destinations_count(filters: Optional[FlightFilterDTO] = None):
    try:
        counts = container.flight_repository.get_destinations_count(filters)
        return counts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/years")
async def get_years():
    try:
        # Get a fresh instance of the repository
        repository = container.flight_repository
        years = repository.get_years()
        if not years:
            return {"years": []}
        return {"years": years}
    except Exception as e:
        print(f"Error in get_years: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/types")
async def get_flight_types():
    try:
        repository = container.flight_repository
        types = repository.get_flight_types()
        if not types:
            return {"types": []}
        return {"types": types}
    except Exception as e:
        print(f"Error in get_flight_types: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/months")
async def get_months():
    try:
        with container.flight_repository() as repo:
            months = repo.get_months()
            return {"months": months}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/origins")
async def get_origins():
    try:
        with container.flight_repository() as repo:
            origins = repo.get_origins()
            return {"origins": origins}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/destinations")
async def get_destinations():
    try:
        with container.flight_repository() as repo:
            destinations = repo.get_destinations()
            return {"destinations": destinations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/types")
async def get_flight_types():
    try:
        with container.flight_repository() as repo:
            types = repo.get_flight_types()
            return {"types": types}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/airlines")
async def get_airlines():
    try:
        with container.flight_repository() as repo:
            airlines = repo.get_airlines()
            return {"airlines": airlines}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/airlines-count", response_model=List[FlightAirlineCountDTO])
async def get_airlines_count(
    years: Optional[str] = None,
    months: Optional[str] = None,
    origins: Optional[str] = None,
    destinations: Optional[str] = None,
    flight_types: Optional[str] = None,
    airlines: Optional[str] = None,
    aircraft_types: Optional[str] = None,
    level_ranges: Optional[str] = None,
    level_min: Optional[int] = None,
    level_max: Optional[int] = None
):
    try:
        filters = FlightFilterDTO(
            years=years.split(',') if years else [],
            months=months.split(',') if months else [],
            origins=origins.split(',') if origins else [],
            destinations=destinations.split(',') if destinations else [],
            flight_types=flight_types.split(',') if flight_types else [],
            airlines=airlines.split(',') if airlines else [],
            aircraft_types=aircraft_types.split(',') if aircraft_types else [],
            level_ranges=level_ranges.split(',') if level_ranges else [],
            level_min=level_min,
            level_max=level_max
        )
        return container.flight_repository.get_airlines_count(filters)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/flight-types-count", response_model=List[FlightTypeCountDTO])
async def get_flight_types_count(
    years: Optional[str] = None,
    months: Optional[str] = None,
    origins: Optional[str] = None,
    destinations: Optional[str] = None,
    flight_types: Optional[str] = None,
    airlines: Optional[str] = None,
    aircraft_types: Optional[str] = None,
    level_ranges: Optional[str] = None,
    level_min: Optional[int] = None,
    level_max: Optional[int] = None
):
    try:
        filters = FlightFilterDTO(
            years=years.split(',') if years else [],
            months=months.split(',') if months else [],
            origins=origins.split(',') if origins else [],
            destinations=destinations.split(',') if destinations else [],
            flight_types=flight_types.split(',') if flight_types else [],
            airlines=airlines.split(',') if airlines else [],
            aircraft_types=aircraft_types.split(',') if aircraft_types else [],
            level_ranges=level_ranges.split(',') if level_ranges else [],
            level_min=level_min,
            level_max=level_max
        )
        return container.flight_repository.get_flight_types_count(filters)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monthly-analysis")
async def analyze_monthly_data(request: DateRangesAnalysisRequestDTO):
    try:
        print("Debug - Monthly Analysis Request:", request.dict())
        result = container.flight_repository.get_monthly_counts_by_date_ranges(
            request.date_ranges,
            request.type
        )
        print("Debug - Monthly Analysis Result:", result)
        return result
    except Exception as e:
        print("Error in monthly analysis:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=422, detail=str(e))

@router.post("/monthly-analysis-destination")
async def analyze_monthly_destination_data(request: DateRangesAnalysisRequestDTO):
    try:
        print("Debug - Monthly Destination Analysis Request:", request.dict())
        result = container.flight_repository.get_monthly_counts_by_date_ranges_destination(
            request.date_ranges
        )
        print("Debug - Monthly Destination Analysis Result:", result)
        return result
    except Exception as e:
        print("Error in monthly destination analysis:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=422, detail=str(e))

@router.post("/yearly-counts-origin")
async def get_yearly_origin_counts(request: DateRangesAnalysisRequestDTO):
    try:
        print("Debug - Yearly Origin Analysis Request:", request.dict())
        result = container.get_flight_yearly_counts_use_case.execute(
            request.date_ranges,
            'origin'
        )
        print("Debug - Yearly Origin Analysis Result:", result)
        return result
    except Exception as e:
        print("Error in yearly origin analysis:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=422, detail=str(e))

@router.post("/yearly-counts-destination")
async def get_yearly_destination_counts(request: DateRangesAnalysisRequestDTO):
    try:
        print("Debug - Yearly Destination Analysis Request:", request.dict())
        result = container.get_flight_yearly_counts_use_case.execute(
            request.date_ranges,
            'destination'
        )
        print("Debug - Yearly Destination Analysis Result:", result)
        return result
    except Exception as e:
        print("Error in yearly destination analysis:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=422, detail=str(e))