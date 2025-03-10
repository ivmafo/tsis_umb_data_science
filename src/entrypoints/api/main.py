# src\entrypoints\api\main.py
import traceback
from fastapi import FastAPI, File, Request, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.infraestructure.config.container import DependencyContainer
from src.core.dtos.flight_dtos import FlightFilterDTO  # Add this import
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import shutil
from pydantic import BaseModel
from fastapi.responses import JSONResponse  # Agregar esta importación al inicio

class DirectoryRequest(BaseModel):
    directory_path: str

class ConfigRequest(BaseModel):
    key: str
    value: str

app = FastAPI()
container = DependencyContainer()

templates = Jinja2Templates(directory="src/infrastructure/adapters/inbound/web/templates")

# Configure CORS
origins = ["http://localhost:3000"]
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

class ProcessStatus:
    def __init__(self):
        self.total_rows = 0
        self.processed_rows = 0
        self.status = "idle"  # idle, processing, completed, error

process_status = ProcessStatus()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        process_status.status = "processing"
        process_status.processed_rows = 0
        
        file_location = f"data/raw/{file.filename}"
        with open(file_location, "wb") as file_object:
            shutil.copyfileobj(file.file, file_object)
        
        def update_progress(processed_rows):
            process_status.processed_rows = processed_rows
            # Mantener el estado en "processing" mientras se actualiza
            process_status.status = "processing"
        
        container.process_flights_use_case.update_progress = update_progress
        process_status.total_rows = container.process_flights_use_case.get_total_rows(file_location)
        result = container.process_flights_use_case.execute(file_location)
        
        process_status.status = "completed"
        return {"message": f"Archivo '{file.filename}' procesado exitosamente.", "details": result}
            
    except Exception as e:
        process_status.status = "error"
        print(f"Error processing file: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        container.process_flights_use_case.update_progress = None

@app.get("/api/process-status")
async def get_process_status():
    return {
        "status": process_status.status,
        "total_rows": process_status.total_rows,
        "processed_rows": process_status.processed_rows,
        "percentage": round((process_status.processed_rows / process_status.total_rows * 100) 
                          if process_status.total_rows > 0 else 0)
    }

@app.get("/files") 
async def get_files():
    try:
        files = container.file_repository.get_all_files()
        return {"files": files}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al obtener archivos: {str(e)}")

@app.post("/upload-directory")
async def upload_directory(request: DirectoryRequest):
    try:
        result = container.process_directory_use_case.execute(request.directory_path)
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

@app.get("/api/config")
async def get_configs():
    try:
        configs = container.get_all_configs_use_case.execute()
        return configs
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al obtener configuraciones: {str(e)}")

@app.get("/api/config/{key}")
async def get_config(key: str):
    try:
        config = container.get_config_use_case.execute(key)
        return config
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al obtener configuración: {str(e)}")

@app.post("/api/config")
async def create_config(config: ConfigRequest):
    try:
        result = container.create_config_use_case.execute(config.dict())
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al crear configuración: {str(e)}")

@app.put("/api/config/{key}")
async def update_config(key: str, config: ConfigRequest):
    try:
        result = container.update_config_use_case.execute(key, config.value)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al actualizar configuración: {str(e)}")
@app.delete("/api/config/{key}")
async def delete_config(key: str):
    try:
        result = container.config_repository.delete_by_key(key)
        if result:
            return {"message": f"Configuración '{key}' eliminada exitosamente"}
        return JSONResponse(
            status_code=404,
            content={"message": f"Configuración '{key}' no encontrada"}
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al eliminar configuración: {str(e)}")
@app.on_event("shutdown")
async def shutdown_event():
    container.cleanup()


@app.get("/api/flights/years")
async def get_flight_years():
    try:
        years = container.flight_repository.get_distinct_years()
        return {"years": years}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/flights/months")
async def get_flight_months():
    try:
        months = container.flight_repository.get_distinct_months()
        return {"months": months}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/flights/origins")
async def get_flight_origins():
    try:
        origins = container.flight_repository.get_distinct_origins()
        return {"origins": origins}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/flights/destinations")
async def get_flight_destinations():
    try:
        destinations = container.flight_repository.get_distinct_destinations()
        return {"destinations": destinations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/flights/flight-types")
async def get_flight_types():
    try:
        flight_types = container.flight_repository.get_distinct_flight_types()
        return {"flightTypes": flight_types}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/flights/airlines")
async def get_airlines():
    try:
        airlines = container.flight_repository.get_distinct_airlines()
        return {"airlines": airlines}
    except Exception as e:
        print(f"Error in get_airlines endpoint: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/flights/aircraft-types")
async def get_aircraft_types():
    try:
        aircraft_types = container.flight_repository.get_distinct_aircraft_types()
        return {"aircraftTypes": aircraft_types}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/flights/level-ranges")
async def get_level_ranges():
    try:
        level_ranges = container.flight_repository.get_distinct_level_ranges()
        return {"levelRanges": level_ranges}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/flights/origins-count")
async def get_origins_count(
    years: str = None,
    months: str = None,
    origins: str = None,
    destinations: str = None,
    flightTypes: str = None,
    airlines: str = None,
    aircraftTypes: str = None,    # Nuevo parámetro
    levelRanges: str = None       # Nuevo parámetro
):
    try:
        filters = FlightFilterDTO(
            years=years.split(',') if years else None,
            months=months.split(',') if months else None,
            origins=origins.split(',') if origins else None,
            destinations=destinations.split(',') if destinations else None,
            flight_types=flightTypes.split(',') if flightTypes else None,
            airlines=airlines.split(',') if airlines else None,
            aircraft_types=aircraftTypes.split(',') if aircraftTypes else None,
            level_ranges=levelRanges.split(',') if levelRanges else None
        )
        
        result = container.get_flight_origins_count_use_case.execute(filters)
        # Asegurarse de que siempre devolvemos una lista
        return result if result else []
        
    except Exception as e:
        print(f"Error in get_origins_count: {str(e)}")  # Agregar log para debugging
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/flights/destinations-count")
async def get_destinations_count(
    years: str = None,
    months: str = None,
    origins: str = None,
    destinations: str = None,
    flightTypes: str = None,
    airlines: str = None,
    aircraftTypes: str = None,
    levelRanges: str = None
):
    try:
        filters = FlightFilterDTO(
            years=years.split(',') if years else None,
            months=months.split(',') if months else None,
            origins=origins.split(',') if origins else None,
            destinations=destinations.split(',') if destinations else None,
            flight_types=flightTypes.split(',') if flightTypes else None,
            airlines=airlines.split(',') if airlines else None,
            aircraft_types=aircraftTypes.split(',') if aircraftTypes else None,
            level_ranges=levelRanges.split(',') if levelRanges else None
        )
        
        result = container.flight_repository.get_destinations_count(filters)
        return result if result else []
        
    except Exception as e:
        print(f"Error in get_destinations_count: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/flights/airlines-count")
async def get_airlines_count(
    years: str = None,
    months: str = None,
    origins: str = None,
    destinations: str = None,
    flightTypes: str = None,
    airlines: str = None,
    aircraftTypes: str = None,
    levelRanges: str = None
):
    try:
        filters = FlightFilterDTO(
            years=years.split(',') if years else None,
            months=months.split(',') if months else None,
            origins=origins.split(',') if origins else None,
            destinations=destinations.split(',') if destinations else None,
            flight_types=flightTypes.split(',') if flightTypes else None,
            airlines=airlines.split(',') if airlines else None,
            aircraft_types=aircraftTypes.split(',') if aircraftTypes else None,
            level_ranges=levelRanges.split(',') if levelRanges else None
        )
        
        result = container.flight_repository.get_airlines_count(filters)
        return result if result else []
        
    except Exception as e:
        print(f"Error in get_airlines_count: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/flights/flight-types-count")
async def get_flight_types_count(
    years: str = None,
    months: str = None,
    origins: str = None,
    destinations: str = None,
    flightTypes: str = None,
    airlines: str = None,
    aircraftTypes: str = None,
    levelRanges: str = None
):
    try:
        filters = FlightFilterDTO(
            years=years.split(',') if years else None,
            months=months.split(',') if months else None,
            origins=origins.split(',') if origins else None,
            destinations=destinations.split(',') if destinations else None,
            flight_types=flightTypes.split(',') if flightTypes else None,
            airlines=airlines.split(',') if airlines else None,
            aircraft_types=aircraftTypes.split(',') if aircraftTypes else None,
            level_ranges=levelRanges.split(',') if levelRanges else None
        )
        
        result = container.flight_repository.get_flight_types_count(filters)
        return result if result else []
        
    except Exception as e:
        print(f"Error in get_flight_types_count: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



