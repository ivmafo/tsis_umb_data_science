from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
import os
import shutil
from fastapi.responses import JSONResponse
from src.infraestructure.config.container import DependencyContainer
import asyncio

router = APIRouter()
container = DependencyContainer()

# Add global variable to store current file path and processing status
current_file_path = None
processing_status = {
    "status": "idle",
    "total_rows": 0,
    "processed_rows": 0,
    "percentage": 0
}

async def process_file(file_path: str):
    global processing_status
    try:
        processing_status["status"] = "processing"
        result = await asyncio.to_thread(container.process_flights_use_case.execute, file_path)
        processing_status["status"] = "completed"
    except Exception as e:
        processing_status["status"] = "error"
        print(f"Error processing file: {str(e)}")
        raise

@router.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    global current_file_path, processing_status
    try:
        # Reset status
        processing_status = {
            "status": "idle",
            "total_rows": 0,
            "processed_rows": 0,
            "percentage": 0
        }

        # Create temp directory if it doesn't exist
        os.makedirs("temp", exist_ok=True)
        
        # Save file path
        file_location = f"temp/{file.filename}"
        current_file_path = file_location
        
        # Save uploaded file
        try:
            with open(file_location, "wb+") as file_object:
                shutil.copyfileobj(file.file, file_object)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

        # Get total rows
        try:
            processing_status["total_rows"] = container.process_flights_use_case.get_total_rows(file_location)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error counting rows: {str(e)}")

        # Process file in background
        background_tasks.add_task(process_file, file_location)
        
        return JSONResponse(content={"message": "File uploaded successfully"})
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/process-status")
async def get_process_status():
    global current_file_path, processing_status
    try:
        if not current_file_path:
            return {
                "status": "idle",
                "total_rows": 0,
                "processed_rows": 0,
                "percentage": 0
            }
        
        if processing_status["status"] == "processing":
            processed_rows = container.process_flights_use_case.get_processed_rows()
            processing_status["processed_rows"] = processed_rows
            processing_status["percentage"] = (processed_rows / processing_status["total_rows"] * 100) if processing_status["total_rows"] > 0 else 0
        
        return processing_status
    except Exception as e:
        print(f"Error checking status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))