# src\entrypoints\api\main.py
import traceback
from fastapi import FastAPI, File, Request, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import shutil
import os

# Importar casos de uso y repositorios
from src.infraestructure.config.database import PostgresConnectionPool
from src.infraestructure.adapters.outbound.postgres_flight_repository import PostgresFlightRepository
from src.infraestructure.adapters.outbound.postgres_file_processing_control_repository import PostgresFileProcessingControlRepository
from src.core.use_cases.process_flights_from_excel import ProcessFlightsFromExcelUseCase
from src.core.use_cases.process_directory_flights import ProcessDirectoryFlightsUseCase
from src.infraestructure.adapters.outbound.file_system_repository import LocalFileSystemRepository
from pydantic import BaseModel

class DirectoryRequest(BaseModel):
    directory_path: str

app = FastAPI()

# Configurar el pool de conexiones
pool = PostgresConnectionPool()
conn = pool.get_connection()

# Inicializar repositorios
base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
file_system_repo = LocalFileSystemRepository(base_path)
flight_repo = PostgresFlightRepository(conn)
file_repo = PostgresFileProcessingControlRepository(conn)

# Inicializar casos de uso
process_directory_uc = ProcessDirectoryFlightsUseCase(flight_repo, file_repo, file_system_repo)

templates = Jinja2Templates(directory="src/infrastructure/adapters/inbound/web/templates")

# Configure CORS
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_location = f"data/raw/{file.filename}"
        with open(file_location, "wb") as file_object:
            shutil.copyfileobj(file.file, file_object)
        process_flights_uc.execute(file_location)
        return {"message": f"Archivo '{file.filename}' procesado exitosamente."}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {str(e)}")
    
   

@app.get("/files") 
async def get_files():
    try:
        files = file_repo.get_all_files()
        print("LISTADO : ->>>>>>>>>>>>>>>>>>>>>>",files)
        return {"files": files}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al obtener archivos: {str(e)}")


# llamado a carga en bloque
@app.post("/upload-directory")
async def upload_directory(request: DirectoryRequest):
    try:
        # Initialize directory processing use case
        process_directory_uc = ProcessDirectoryFlightsUseCase(flight_repo, file_repo)
        result = process_directory_uc.execute(request.directory_path)
        
        return {
            "message": f"Procesados {len(result['processed_files'])} archivos exitosamente",
            "processed_files": result['processed_files'],
            "errors": result['errors']
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al procesar el directorio: {str(e)}")

def shutdown_event():
    pool.release_connection(conn)
    pool.close_all_connections()



