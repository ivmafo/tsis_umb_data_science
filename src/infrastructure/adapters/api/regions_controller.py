from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from src.application.use_cases.manage_regions import ManageRegions
from src.application.use_cases.manage_regions import ManageRegions
from src.application.di.container import get_manage_regions_use_case

router = APIRouter(prefix="/regions", tags=["regions"])

# Pydantic models for API
class RegionCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = ""
    nivel_min: Optional[int] = 0

class RegionResponse(BaseModel):
    id: int
    name: str
    code: str
    description: str
    created_at: datetime
    updated_at: datetime
    nivel_min: Optional[int]

# Dependency
# Dependency replaced by imports from container

@router.get("/", response_model=List[RegionResponse])
def list_regions(use_case: ManageRegions = Depends(get_manage_regions_use_case)):
    return use_case.list_regions()

@router.get("/{region_id}", response_model=RegionResponse)
def get_region(region_id: int, use_case: ManageRegions = Depends(get_manage_regions_use_case)):
    region = use_case.get_region(region_id)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    return region

@router.post("/", response_model=RegionResponse)
def create_region(region: RegionCreate, use_case: ManageRegions = Depends(get_manage_regions_use_case)):
    return use_case.create_region(region.model_dump())

@router.put("/{region_id}", response_model=RegionResponse)
def update_region(region_id: int, region: RegionCreate, use_case: ManageRegions = Depends(get_manage_regions_use_case)):
    updated_region = use_case.update_region(region_id, region.model_dump())
    if not updated_region:
        raise HTTPException(status_code=404, detail="Region not found")
    return updated_region

@router.delete("/{region_id}")
def delete_region(region_id: int, use_case: ManageRegions = Depends(get_manage_regions_use_case)):
    if not use_case.delete_region(region_id):
         raise HTTPException(status_code=404, detail="Region not found")
    return {"message": "Region deleted"}
