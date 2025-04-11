from fastapi import APIRouter, HTTPException
from datetime import datetime
from src.infraestructure.config.container import DependencyContainer

router = APIRouter()
container = DependencyContainer()

@router.get("/sectors")
def get_sectors():
    try:
        use_case = container.get_sector_capacity_use_case()
        sectors = use_case.get_sectors()
        return {"sectors": sectors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{sector}")
def get_sector_capacity(sector: str, date: str):
    try:
        use_case = container.get_sector_capacity_use_case()
        date_obj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        
        if date_obj.year < 1900:
            raise HTTPException(status_code=400, detail="La fecha debe ser posterior a 1900")
            
        result = use_case.execute(sector, date_obj)
        
        if result is None:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para el sector {sector} en la fecha {date}")
            
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))