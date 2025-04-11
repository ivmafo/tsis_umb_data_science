from fastapi import APIRouter, HTTPException
from typing import List
from src.core.dtos.airport_region_dtos import AirportRegionCreateDTO, AirportRegionUpdateDTO, AirportRegionDTO
from src.infraestructure.config.container import DependencyContainer

router = APIRouter()
container = DependencyContainer()

@router.get("/airport-regions", response_model=List[AirportRegionDTO])
async def get_airport_regions():
    try:
        result = container.get_all_airport_regions_use_case.execute()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/airport-regions/{id}", response_model=AirportRegionDTO)
async def get_airport_region(id: int):
    try:
        result = container.get_airport_region_by_id_use_case.execute(id)
        if not result:
            raise HTTPException(status_code=404, detail="Airport region not found")
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/airport-regions/icao/{icao_code}", response_model=List[AirportRegionDTO])
async def get_airport_regions_by_icao(icao_code: str):
    try:
        result = container.get_airport_regions_by_icao_use_case.execute(icao_code)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/airport-regions", response_model=AirportRegionDTO)
async def create_airport_region(airport_region: AirportRegionCreateDTO):
    try:
        result = container.create_airport_region_use_case.execute(airport_region.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/airport-regions/{id}", response_model=AirportRegionDTO)
async def update_airport_region(id: int, airport_region: AirportRegionUpdateDTO):
    try:
        result = container.update_airport_region_use_case.execute(id, airport_region.dict(exclude_unset=True))
        if not result:
            raise HTTPException(status_code=404, detail="Airport region not found")
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/airport-regions/{id}")
async def delete_airport_region(id: int):
    try:
        result = container.delete_airport_region_use_case.execute(id)
        if not result:
            raise HTTPException(status_code=404, detail="Airport region not found")
        return {"message": "Airport region deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))