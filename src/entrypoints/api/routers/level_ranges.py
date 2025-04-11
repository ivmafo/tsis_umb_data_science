from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import traceback
from src.infraestructure.config.container import DependencyContainer

router = APIRouter()
container = DependencyContainer()

class LevelRangeRequest(BaseModel):
    origen: str
    destino: str
    nivel_min: int
    nivel_max: int
    ruta: str
    zona: str

@router.get("")
async def get_level_ranges():
    try:
        ranges = container.get_all_level_ranges_use_case.execute()
        return ranges
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error getting level ranges: {str(e)}")

@router.get("/{id}")
async def get_level_range(id: int):
    try:
        range = container.get_level_range_use_case.execute(id)
        if not range:
            raise HTTPException(status_code=404, detail=f"Level range with ID {id} not found")
        return range
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error getting level range: {str(e)}")

# ... (other level range endpoints following same pattern) ...