from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
from src.application.use_cases.manage_airports import ManageAirports
from src.application.use_cases.manage_airports import ManageAirports
from src.application.di.container import get_manage_airports_use_case
from src.domain.entities.airport import Airport

router = APIRouter(prefix="/airports", tags=["airports"])

class AirportResponse(BaseModel):
    id: int
    icao_code: str
    iata_code: Optional[str] = None
    name: str
    city: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[int] = None
    timezone: Optional[float] = None
    dst: Optional[str] = None
    type: Optional[str] = None
    source: Optional[str] = None

class AirportCreate(BaseModel):
    icao_code: str
    iata_code: Optional[str] = None
    name: str
    city: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[int] = None
    timezone: Optional[float] = None
    dst: Optional[str] = None
    type: Optional[str] = None
    source: Optional[str] = None

class PaginatedResponse(BaseModel):
    data: List[AirportResponse]
    total: int
    page: int
    page_size: int


@router.get("/", response_model=PaginatedResponse)
def list_airports(
    page: int = Query(1, ge=1, description="Número de página para la paginación (basado en 1)"), 
    page_size: int = Query(10, ge=1, le=100, description="Cantidad de aeropuertos por página (máx: 100)"), 
    search: str = Query("", description="Término de búsqueda opcional para filtrar por código OACI o nombre"),
    use_case: ManageAirports = Depends(get_manage_airports_use_case)
):
    """
    Obtiene un listado paginado y filtrable de todos los aeropuertos en la base de datos maestra.
    
    Args:
        page (int): El índice de la página solicitado.
        page_size (int): Límite de resultados por respuesta.
        search (str): Filtro de texto para coincidencia parcial en campos clave.
        use_case (ManageAirports): Inyección del caso de uso de gestión de aeropuertos.
        
    Returns:
        PaginatedResponse: Objeto conteniendo el set de datos, el total de registros y metadatos de paginación.
    """
    items, total = use_case.get_airports(page, page_size, search)
    return {
        "data": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.post("/", response_model=AirportResponse)
def create_airport(
    airport: AirportCreate, 
    use_case: ManageAirports = Depends(get_manage_airports_use_case)
):
    """
    Registra un nuevo aeropuerto en el catálogo del sistema.
    
    Args:
        airport (AirportCreate): Datos estructurados del nuevo aeropuerto siguiendo el esquema Pydantic.
        use_case (ManageAirports): Lógica de negocio para la persistencia del aeropuerto.
        
    Returns:
        AirportResponse: El registro del aeropuerto recién creado con su ID asignado.
    """
    return use_case.create_airport(airport.model_dump())

@router.get("/{airport_id}", response_model=AirportResponse)
def get_airport(
    airport_id: int, 
    use_case: ManageAirports = Depends(get_manage_airports_use_case)
):
    """
    Recupera la información técnica detallada de un aeropuerto específico mediante su ID interno.
    
    Args:
        airport_id (int): Identificador numérico único del aeropuerto en la BD.
        use_case (ManageAirports): Orquestador de acceso a datos.
        
    Returns:
        AirportResponse: Los detalles del aeropuerto encontrado.
        
    Raises:
        HTTPException: Error 404 si el ID no corresponde a ningún aeropuerto registrado.
    """
    airport = use_case.get_airport(airport_id)
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found")
    return airport

@router.put("/{airport_id}", response_model=AirportResponse)
def update_airport(
    airport_id: int, 
    airport: AirportCreate, 
    use_case: ManageAirports = Depends(get_manage_airports_use_case)
):
    """
    Actualiza los campos de un aeropuerto existente.
    
    Args:
        airport_id (int): ID del registro a modificar.
        airport (AirportCreate): Nuevo conjunto de datos para el aeropuerto.
        use_case (ManageAirports): Lógica para la actualización atómica en la base de datos.
        
    Returns:
        AirportResponse: El objeto actualizado.
        
    Raises:
        HTTPException: Error 404 si el aeropuerto no existe.
    """
    updated = use_case.update_airport(airport_id, airport.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Airport not found")
    return updated

@router.delete("/{airport_id}")
def delete_airport(
    airport_id: int, 
    use_case: ManageAirports = Depends(get_manage_airports_use_case)
):
    """
    Elimina permanentemente un aeropuerto del sistema.
    
    Args:
        airport_id (int): ID del aeropuerto a remover.
        use_case (ManageAirports): Orquestador de eliminación.
        
    Returns:
        dict: Mensaje de confirmación del éxito de la operación.
        
    Raises:
        HTTPException: Error 404 si el aeropuerto no pudo ser localizado para su eliminación.
    """
    if not use_case.delete_airport(airport_id):
        raise HTTPException(status_code=404, detail="Airport not found")
    return {"message": "Airport deleted"}
