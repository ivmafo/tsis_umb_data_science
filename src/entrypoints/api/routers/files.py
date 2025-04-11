from fastapi import APIRouter, HTTPException
from typing import List
from src.infraestructure.config.container import DependencyContainer

router = APIRouter()
container = DependencyContainer()

@router.get("/api/files")
async def list_files():
    try:
        files = container.file_processing_control_repository.get_all_files()
        return [
            {
                "id": file["id"],
                "name": file["file_name"],
                "processedAt": file["processed_at"].isoformat() if file["processed_at"] else None,
                "processed": file["processed"]
            }
            for file in files
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))