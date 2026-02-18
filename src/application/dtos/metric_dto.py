from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class HealthCheckResponse(BaseModel):
    """
    Modelo de respuesta para la verificación de estado del sistema.
    """
    status: str = Field(..., description="Estado general del servicio (ej. 'ok')")
    version: str = Field(..., description="Versión actual de la aplicación")
    database: str = Field(..., description="Estado de la conexión con la base de datos DuckDB")
    timestamp: str = Field(..., description="Marca de tiempo actual del servidor")
