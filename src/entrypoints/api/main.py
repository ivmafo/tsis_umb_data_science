# src\entrypoints\api\main.py
import traceback
from typing import List, Optional
from src.core.entities.sector_analysis import SectorDetailedAnalysis
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from src.infraestructure.config.container import DependencyContainer
from src.core.dtos.flight_dtos import (
    FlightFilterDTO, 
    FlightOriginCountDTO,
    DateRangesAnalysisRequestDTO,
    FlightHourlyCountDTO
)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import shutil
from pydantic import BaseModel
from fastapi.responses import JSONResponse  # Agregar esta importación al inicio
from src.core.entities.sector_capacity import SectorCapacityResponse
from src.core.use_cases.get_sector_capacity import GetSectorCapacityUseCase
from src.core.entities.sector_analysis import SectorDetailedAnalysis
from src.entrypoints.api.routers import (
    uploads,
    config,
    flights,
    level_ranges,
    sector_capacity,
    regions,
    sector_analysis,  # Added comma here
    files
)

app = FastAPI()
container = DependencyContainer()
templates = Jinja2Templates(directory="src/infrastructure/adapters/inbound/web/templates")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(uploads.router, prefix="/api")
app.include_router(config.router, prefix="/api/config")
app.include_router(flights.router, prefix="/api/flights")
app.include_router(level_ranges.router, prefix="/api/level-ranges")
app.include_router(sector_capacity.router, prefix="/api/sector-capacity")
app.include_router(regions.router, prefix="/api/regions")
app.include_router(sector_analysis.router, prefix="/api/sector-analysis")
app.include_router(files.router)

# Add to your imports
from src.entrypoints.api.routers import airport_regions

# Add to your router includes
app.include_router(airport_regions.router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

