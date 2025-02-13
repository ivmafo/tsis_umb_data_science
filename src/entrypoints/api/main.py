#tsis_umb_data_science/src/entrypoints/api/main.py
import traceback
from fastapi import FastAPI, File, Request, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import shutil

# Importar casos de uso y repositorios
from src.infraestructure.config.database import PostgresConnectionPool
from src.infraestructure.adapters.outbound.postgres_flight_repository import PostgresFlightRepository
from src.infraestructure.adapters.outbound.postgres_file_processing_control_repository import PostgresFileProcessingControlRepository
from src.core.use_cases.process_flights_from_excel import ProcessFlightsFromExcelUseCase

app = FastAPI()

# Configurar el pool de conexiones
pool = PostgresConnectionPool()
conn = pool.get_connection()

# Inicializar repositorios
flight_repo = PostgresFlightRepository(conn)
file_repo = PostgresFileProcessingControlRepository(conn)

# Inicializar caso de uso para procesar archivos Excel
process_flights_uc = ProcessFlightsFromExcelUseCase(flight_repo, file_repo)

templates = Jinja2Templates(directory="src/infrastructure/adapters/inbound/web/templates")

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
        return files
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al obtener archivos: {str(e)}")



@app.on_event("shutdown")
def shutdown_event():
    pool.release_connection(conn)
    pool.close_all_connections()



