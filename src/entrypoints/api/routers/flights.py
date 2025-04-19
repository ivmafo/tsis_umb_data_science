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

class DateRangeDTO(BaseModel):
    id: str
    start_date: str
    end_date: str
    label: str
    origin_airport: str
    destination_airport: str
    nivel_min: int = 0  # Valor por defecto
    nivel_max: int = 99999  # Valor por defecto

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

@router.get("/origins")
async def get_origins():
    try:
        origins = container.flight_repository.get_distinct_origins()
        return origins
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))