from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
from src.application.use_cases.manage_airports import ManageAirports
from src.application.use_cases.manage_airports import ManageAirports
from src.application.di.container import get_manage_airports_use_case
from src.domain.entities.airport import Airport

router = APIRouter(prefix="/airports", tags=["airports"])

class AirportResponse(BaseModel):
    id: int
    icao_code: str
    iata_code: Optional[str] = None
    name: str
    city: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[int] = None
    timezone: Optional[float] = None
    dst: Optional[str] = None
    type: Optional[str] = None
    source: Optional[str] = None

class AirportCreate(BaseModel):
    icao_code: str
    iata_code: Optional[str] = None
    name: str
    city: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[int] = None
    timezone: Optional[float] = None
    dst: Optional[str] = None
    type: Optional[str] = None
    source: Optional[str] = None

class PaginatedResponse(BaseModel):
    data: List[AirportResponse]
    total: int
    page: int
    page_size: int


@router.get("/", response_model=PaginatedResponse)
def list_airports(
    page: int = Query(1, ge=1), 
    page_size: int = Query(10, ge=1, le=100), 
    search: str = "",
    use_case: ManageAirports = Depends(get_manage_airports_use_case)
):
    items, total = use_case.get_airports(page, page_size, search)
    return {
        "data": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.post("/", response_model=AirportResponse)
def create_airport(airport: AirportCreate, use_case: ManageAirports = Depends(get_manage_airports_use_case)):
    return use_case.create_airport(airport.model_dump())

@router.get("/{airport_id}", response_model=AirportResponse)
def get_airport(airport_id: int, use_case: ManageAirports = Depends(get_manage_airports_use_case)):
    airport = use_case.get_airport(airport_id)
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    return airport

@router.put("/{airport_id}", response_model=AirportResponse)
def update_airport(airport_id: int, airport: AirportCreate, use_case: ManageAirports = Depends(get_manage_airports_use_case)):
    updated = use_case.update_airport(airport_id, airport.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Airport not found")
    return updated

@router.delete("/{airport_id}")
def delete_airport(airport_id: int, use_case: ManageAirports = Depends(get_manage_airports_use_case)):
    if not use_case.delete_airport(airport_id):
        raise HTTPException(status_code=404, detail="Airport not found")
    return {"message": "Airport deleted"}
