from fastapi import APIRouter, UploadFile, HTTPException, Depends
from typing import List
from src.domain.entities.file_info import FileInfo
from src.application.use_cases.manage_files import ManageFiles
from src.infrastructure.adapters.filesystem_repository import FilesystemRepository

router = APIRouter(prefix="/files", tags=["files"])

# Simple dependency injection (could be improved with a Container)
def get_manage_files_use_case() -> ManageFiles:
    repository = FilesystemRepository(data_directory="data")
    return ManageFiles(repository)

@router.get("/", response_model=List[FileInfo])
async def list_files(use_case: ManageFiles = Depends(get_manage_files_use_case)):
    return use_case.list_files()

@router.post("/", response_model=FileInfo)
async def upload_file(
    file: UploadFile, 
    use_case: ManageFiles = Depends(get_manage_files_use_case)
):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are allowed")
    
    content = await file.read()
    file_info = use_case.upload_file(file.filename, content)
    
    if not file_info.validation_status:
        raise HTTPException(status_code=400, detail=file_info.error_message)
        
    return file_info
