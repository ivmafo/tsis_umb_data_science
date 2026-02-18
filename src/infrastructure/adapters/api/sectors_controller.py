
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from src.application.di.container import get_manage_sectors_use_case, get_calculate_sector_capacity_use_case
from src.application.use_cases.manage_sectors import ManageSectors
from src.application.use_cases.calculate_sector_capacity import CalculateSectorCapacity
from pydantic import BaseModel

router = APIRouter(prefix="/sectors", tags=["sectors"])

class SectorCreate(BaseModel):
    name: str
    definition: Dict[str, Any] # e.g. {"origins": ["SKBO"]}
    t_transfer: float = 0.0
    t_comm_ag: float = 0.0
    t_separation: float = 0.0
    t_coordination: float = 0.0
    adjustment_factor_r: float = 0.8
    capacity_baseline: int = 0

class SectorUpdate(BaseModel):
    name: Optional[str] = None
    definition: Optional[Dict[str, Any]] = None
    t_transfer: Optional[float] = None
    t_comm_ag: Optional[float] = None
    t_separation: Optional[float] = None
    t_coordination: Optional[float] = None
    adjustment_factor_r: Optional[float] = None
    capacity_baseline: Optional[int] = None

class CapacityRequest(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None

@router.get("/")
def get_sectors(uc: ManageSectors = Depends(get_manage_sectors_use_case)):
    return uc.get_all()

@router.get("/{id}")
def get_sector(id: str, uc: ManageSectors = Depends(get_manage_sectors_use_case)):
    sector = uc.get_by_id(id)
    if not sector:
        raise HTTPException(status_code=404, detail="Sector not found")
    return sector

@router.post("/")
def create_sector(sector: SectorCreate, uc: ManageSectors = Depends(get_manage_sectors_use_case)):
    new_id = uc.create(sector.dict())
    return {"id": new_id, "message": "Sector created"}

@router.put("/{id}")
def update_sector(id: str, sector: SectorUpdate, uc: ManageSectors = Depends(get_manage_sectors_use_case)):
    # Pydantic dict exclude_unset to avoid overwriting with None
    success = uc.update(id, sector.dict(exclude_unset=True))
    if not success:
         raise HTTPException(status_code=404, detail="Sector not found or update failed")
    return {"message": "Sector updated"}

@router.delete("/{id}")
def delete_sector(id: str, uc: ManageSectors = Depends(get_manage_sectors_use_case)):
    success = uc.delete(id)
    if not success:
         raise HTTPException(status_code=404, detail="Sector not found")
    return {"message": "Sector deleted"}

@router.post("/{id}/calculate")
def calculate_capacity(id: str, req: CapacityRequest, uc: CalculateSectorCapacity = Depends(get_calculate_sector_capacity_use_case)):
    try:
        filters = {"start_date": req.start_date, "end_date": req.end_date}
        result = uc.execute(id, filters)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
