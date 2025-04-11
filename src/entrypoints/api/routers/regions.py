from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import traceback
from src.infraestructure.config.container import DependencyContainer
from src.core.dtos.region_dtos import RegionDTO

router = APIRouter()
container = DependencyContainer()

class RegionRequest(BaseModel):
    name: str
    code: str
    description: str = None

@router.get("")
async def get_regions():
    try:
        regions = container.get_all_regions_use_case.execute()
        return regions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}")
async def get_region(id: int):
    try:
        region = container.get_region_by_id_use_case.execute(id)
        if not region:
            raise HTTPException(status_code=404, detail=f"Región con ID {id} no encontrada")
        return region
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def create_region(region: RegionRequest):
    try:
        return container.create_region_use_case.execute(region.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id}")
async def update_region(id: int, region: RegionRequest):
    try:
        result = container.update_region_use_case.execute(id, region.dict())
        if not result:
            raise HTTPException(status_code=404, detail=f"Región con ID {id} no encontrada")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id}")
async def delete_region(id: int):
    try:
        result = container.delete_region_use_case.execute(id)
        if result:
            return {"message": "Región eliminada exitosamente"}
        raise HTTPException(status_code=404, detail="Región no encontrada")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))