from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from src.application.use_cases.ingest_flights_data import IngestFlightsDataUseCase
from src.application.di.container import get_ingest_flights_use_case

router = APIRouter(prefix="/etl", tags=["ETL"])


@router.post("/ingest")
def trigger_ingestion(
    background_tasks: BackgroundTasks,
    force_reload: bool = False,
    filename: str = None,
    use_case: IngestFlightsDataUseCase = Depends(get_ingest_flights_use_case)
):
    """Trigger the ingestion process in the background."""
    background_tasks.add_task(use_case.execute, force_reload=force_reload, specific_file=filename)
    return {"message": "Ingestion started", "status": "processing"}

@router.get("/progress")
def get_progress(use_case: IngestFlightsDataUseCase = Depends(get_ingest_flights_use_case)):
    return use_case.get_progress()

@router.get("/status")
def get_status(use_case: IngestFlightsDataUseCase = Depends(get_ingest_flights_use_case)):
    """Alias for progress used by SystemStatus component."""
    return use_case.get_progress()

@router.get("/history")
def get_history(use_case: IngestFlightsDataUseCase = Depends(get_ingest_flights_use_case)):
    return use_case.get_history()

@router.delete("/files/{filename}")
def delete_file(filename: str, use_case: IngestFlightsDataUseCase = Depends(get_ingest_flights_use_case)):
    """Delete a file and its associated data."""
    try:
        use_case.delete_file(filename)
        return {"message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset")
def reset_database(use_case: IngestFlightsDataUseCase = Depends(get_ingest_flights_use_case)):
    """Truncate flights and file_processing_control tables."""
    try:
        use_case.reset_database()
        return {"message": "Database reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
