"""Main application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .infrastructure.adapters.api.metrics_controller import router as metrics_router
from .infrastructure.adapters.api.etl_controller import router as etl_router
from .infrastructure.adapters.api.stats_controller import router as stats_router
from .infrastructure.adapters.api.filters_controller import router as filters_router
from .infrastructure.adapters.api.reports_controller import router as reports_router
from .infrastructure.adapters.api.airports_controller import router as airports_router
from .infrastructure.adapters.api.regions_controller import router as regions_router
from .infrastructure.adapters.api.region_airports_controller import router as region_airports_router
from .infrastructure.adapters.api.files_controller import router as files_router
from .infrastructure.adapters.api.sectors_controller import router as sectors_router
from .infrastructure.adapters.api.predictive_controller import router as predictive_router
from .infrastructure.config.settings import Settings
from .application.di.container import Container


# Initialize settings and container
settings = Settings()
container = Container()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    This is the modern way to handle startup/shutdown in FastAPI.
    """
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Database: {settings.database_path}")
    print(f"Data directory: {settings.data_directory}")
    
    # Log Routes
    # We access app via closure/argument? No, lifespan receives app.
    print("--- REGISTERED ROUTES ---")
    for route in app.routes:
        if hasattr(route, "path"):
            print(f"Route: {route.path}")
    print("-----------------------")
    
    yield
    
    # Shutdown
    print("Shutting down...")


def create_app() -> FastAPI:
    """
    Application factory pattern.
    
    Creates and configures the FastAPI application.
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Hexagonal Architecture Data Processing System with Polars and FastAPI",
        lifespan=lifespan
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(metrics_router)
    app.include_router(etl_router)
    app.include_router(stats_router)
    app.include_router(filters_router)
    app.include_router(reports_router) # Register Reports Router
    app.include_router(airports_router)
    app.include_router(regions_router)
    app.include_router(region_airports_router)
    app.include_router(files_router)
    app.include_router(reports_router)
    app.include_router(sectors_router)
    app.include_router(predictive_router)
    
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
