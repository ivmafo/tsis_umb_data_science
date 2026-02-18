"""Metrics API Controller - FastAPI router for metrics endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from ....application.di.container import Container
from ....application.dtos.metric_dto import HealthCheckResponse


router = APIRouter(prefix="/api/v1", tags=["metrics"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        version="1.0.0"
    )
