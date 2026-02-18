from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from src.domain.entities.region_airport import RegionAirport
from src.application.use_cases.manage_region_airports import ManageRegionAirports
from src.application.di.container import get_manage_region_airports_use_case

router = APIRouter(prefix="/region-airports", tags=["region-airports"])

class PaginatedResponse(BaseModel):
    data: List[RegionAirport]
    total: int
    page: int
    page_size: int

@router.get("/", response_model=PaginatedResponse)
def list_region_airports(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str = "",
    use_case: ManageRegionAirports = Depends(get_manage_region_airports_use_case)
):
    items, total = use_case.get_region_airports(page, page_size, search)
    return {
        "data": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.post("/", response_model=RegionAirport)
def create_region_airport(
    item: RegionAirport,
    use_case: ManageRegionAirports = Depends(get_manage_region_airports_use_case)
):
    try:
        return use_case.create_region_airport(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{id}", response_model=RegionAirport)
def update_region_airport(
    id: int,
    item: RegionAirport,
    use_case: ManageRegionAirports = Depends(get_manage_region_airports_use_case)
):
    try:
        return use_case.update_region_airport(id, item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{id}")
def delete_region_airport(
    id: int,
    use_case: ManageRegionAirports = Depends(get_manage_region_airports_use_case)
):
    use_case.delete_region_airport(id)
    return {"status": "success"}
