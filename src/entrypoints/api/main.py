# src\entrypoints\api\main.py
import traceback
from datetime import datetime
from fastapi import FastAPI, File, Request, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.infraestructure.config.container import DependencyContainer
from src.core.dtos.flight_dtos import FlightFilterDTO  # Add this import
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import shutil
from pydantic import BaseModel
from fastapi.responses import JSONResponse  # Agregar esta importación al inicio
from src.core.entities.sector_capacity import SectorCapacityResponse
from src.core.use_cases.get_sector_capacity import GetSectorCapacityUseCase
from src.core.entities.sector_analysis import SectorDetailedAnalysis

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



@app.get("/api/flights/origins-count")
async def get_origins_count(
    years: str = None,
    months: str = None,
    origins: str = None,
    destinations: str = None,
    flightTypes: str = None,
    airlines: str = None,
    aircraftTypes: str = None    
):
    try:
        filters = FlightFilterDTO(
            years=years.split(',') if years else None,
            months=months.split(',') if months else None,
            origins=origins.split(',') if origins else None,
            destinations=destinations.split(',') if destinations else None,
            flight_types=flightTypes.split(',') if flightTypes else None,
            airlines=airlines.split(',') if airlines else None,
            aircraft_types=aircraftTypes.split(',') if aircraftTypes else None
        )
        
        result = container.get_flight_origins_count_use_case.execute(filters)
        # Convert to list if not already a list
        if isinstance(result, list):
            return result
        return []
        
    except Exception as e:
        print(f"Error in get_origins_count: {str(e)}")
        traceback.print_exc()  # Add this to get more detailed error information
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/flights/destinations-count")
async def get_destinations_count(
    years: str = None,
    months: str = None,
    origins: str = None,
    destinations: str = None,
    flightTypes: str = None,
    airlines: str = None,
    aircraftTypes: str = None
):
    try:
        filters = FlightFilterDTO(
            years=years.split(',') if years else None,
            months=months.split(',') if months else None,
            origins=origins.split(',') if origins else None,
            destinations=destinations.split(',') if destinations else None,
            flight_types=flightTypes.split(',') if flightTypes else None,
            airlines=airlines.split(',') if airlines else None,
            aircraft_types=aircraftTypes.split(',') if aircraftTypes else None
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
    aircraftTypes: str = None
):
    try:
        filters = FlightFilterDTO(
            years=years.split(',') if years else None,
            months=months.split(',') if months else None,
            origins=origins.split(',') if origins else None,
            destinations=destinations.split(',') if destinations else None,
            flight_types=flightTypes.split(',') if flightTypes else None,
            airlines=airlines.split(',') if airlines else None,
            aircraft_types=aircraftTypes.split(',') if aircraftTypes else None
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
    aircraftTypes: str = None
):
    try:
        filters = FlightFilterDTO(
            years=years.split(',') if years else None,
            months=months.split(',') if months else None,
            origins=origins.split(',') if origins else None,
            destinations=destinations.split(',') if destinations else None,
            flight_types=flightTypes.split(',') if flightTypes else None,
            airlines=airlines.split(',') if airlines else None,
            aircraft_types=aircraftTypes.split(',') if aircraftTypes else None
        )
        
        result = container.flight_repository.get_flight_types_count(filters)
        return result if result else []
        
    except Exception as e:
        print(f"Error in get_flight_types_count: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Add this class with the other BaseModel classes at the top
class LevelRangeRequest(BaseModel):
    min_level: int
    max_level: int
    alias: str

# Add these new endpoints
@app.get("/api/level-ranges")
async def get_level_ranges():
    try:
        ranges = container.get_all_level_ranges_use_case.execute()
        return ranges
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al obtener rangos de nivel: {str(e)}")

@app.get("/api/level-ranges/{id}")
async def get_level_range(id: int):
    try:
        range = container.get_level_range_use_case.execute(id)
        return range
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al obtener rango de nivel: {str(e)}")

@app.post("/api/level-ranges")
async def create_level_range(level_range: LevelRangeRequest):
    try:
        result = container.create_level_range_use_case.execute(level_range.dict())
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al crear rango de nivel: {str(e)}")

@app.put("/api/level-ranges/{id}")
async def update_level_range(id: int, level_range: LevelRangeRequest):
    try:
        level_range_dict = level_range.dict()
        result = container.update_level_range_use_case.execute(id, level_range_dict)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al actualizar rango de nivel: {str(e)}")

@app.delete("/api/level-ranges/{id}")
async def delete_level_range(id: int):
    try:
        result = container.delete_level_range_use_case.execute(id)
        if result:
            return {"message": f"Rango de nivel con ID '{id}' eliminado exitosamente"}
        return JSONResponse(
            status_code=404,
            content={"message": f"Rango de nivel con ID '{id}' no encontrado"}
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al eliminar rango de nivel: {str(e)}")

# Sector Capacity endpoints
@app.get("/api/sector-capacity/sectors")
def get_sectors():
    try:
        use_case = container.get_sector_capacity_use_case()
        sectors = use_case.get_sectors()
        return {"sectors": sectors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sector-capacity/{sector}")
def get_sector_capacity(sector: str, date: str):
    try:
        use_case = container.get_sector_capacity_use_case()
        
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="Formato de fecha inválido. Use YYYY-MM-DD HH:MM:SS"
            )
            
        if date_obj.year < 1900:
            raise HTTPException(
                status_code=400,
                detail="La fecha debe ser posterior a 1900"
            )
            
        result = use_case.execute(sector, date_obj)
        
        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron datos para el sector {sector} en la fecha {date}"
            )
            
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add these imports at the top with other imports
from src.core.entities.sector_analysis import SectorDetailedAnalysis

# Add these endpoints after the existing ones
@app.get("/api/sector-analysis/sectors")
async def get_analysis_sectors():
    try:
        sectors = container.sector_analysis_repository.get_all_sectors()
        return sectors
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error getting sectors: {str(e)}")

@app.get("/api/sector-analysis/{sector}")
async def get_sector_analysis(
    sector: str,
    start_date: str,
    end_date: str,
    page: int = 1,
    page_size: int = 10000
):
    try:
        print(f"Received request with params: sector={sector}, start_date={start_date}, end_date={end_date}, page={page}, page_size={page_size}")
        
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start_date_obj > end_date_obj:
            raise HTTPException(
                status_code=400,
                detail="Start date cannot be later than end date"
            )
        
        skip = (page - 1) * page_size
        
        analysis_data = container.sector_analysis_repository.get_analysis_by_date_range(
            sector,
            start_date_obj,
            end_date_obj,
            skip,
            page_size
        )
        
        total_count = container.sector_analysis_repository.get_total_count(
            sector,
            start_date_obj,
            end_date_obj
        )
        
        print(f"Found {total_count} total records, returning {len(analysis_data)} items")
        
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

@app.get("/api/sector-analysis/{sector}/date")
async def get_sector_analysis_by_date(
    sector: str,
    date: str
):
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        analysis = container.sector_analysis_repository.get_by_sector_and_date(sector, date_obj)
        
        if not analysis:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for sector {sector} on {date}"
            )
            
        return analysis
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error getting sector analysis: {str(e)}")



