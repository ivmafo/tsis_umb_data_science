from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class HealthCheckResponse(BaseModel):
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    database: str = Field(..., description="Database status")
    timestamp: str = Field(..., description="Current timestamp")
