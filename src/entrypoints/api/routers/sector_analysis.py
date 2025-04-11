from fastapi import APIRouter, HTTPException
from datetime import datetime
import traceback
from src.infraestructure.config.container import DependencyContainer

router = APIRouter()
container = DependencyContainer()

@router.get("/sectors")
async def get_analysis_sectors():
    try:
        sectors = container.sector_analysis_repository.get_all_sectors()
        return sectors
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error getting sectors: {str(e)}")

@router.get("/{sector}")
async def get_sector_analysis(sector: str, start_date: str, end_date: str, page: int = 1, page_size: int = 10000):
    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start_date_obj > end_date_obj:
            raise HTTPException(status_code=400, detail="Start date cannot be later than end date")
        
        skip = (page - 1) * page_size
        
        analysis_data = container.sector_analysis_repository.get_analysis_by_date_range(
            sector, start_date_obj, end_date_obj, skip, page_size
        )
        
        total_count = container.sector_analysis_repository.get_total_count(sector, start_date_obj, end_date_obj)
        
        return {
            "items": analysis_data,
            "total": total_count,
            "page": page,
            "page_size": page_size
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error getting sector analysis: {str(e)}")

# ... (other sector analysis endpoints) ...