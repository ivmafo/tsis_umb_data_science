
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from src.application.di.container import get_manage_sectors_use_case, get_calculate_sector_capacity_use_case
from src.application.use_cases.manage_sectors import ManageSectors
from src.application.use_cases.calculate_sector_capacity import CalculateSectorCapacity
from pydantic import BaseModel

router = APIRouter(prefix="/sectors", tags=["sectors"])

class SectorCreate(BaseModel):
    name: str
    definition: Dict[str, Any] # e.g. {"origins": ["SKBO"]}
    t_transfer: float = 0.0
    t_comm_ag: float = 0.0
    t_separation: float = 0.0
    t_coordination: float = 0.0
    adjustment_factor_r: float = 0.8
    capacity_baseline: int = 0

class SectorUpdate(BaseModel):
    name: Optional[str] = None
    definition: Optional[Dict[str, Any]] = None
    t_transfer: Optional[float] = None
    t_comm_ag: Optional[float] = None
    t_separation: Optional[float] = None
    t_coordination: Optional[float] = None
    adjustment_factor_r: Optional[float] = None
    capacity_baseline: Optional[int] = None

class CapacityRequest(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None

@router.get("/")
def get_sectors(uc: ManageSectors = Depends(get_manage_sectors_use_case)):
    """
    Recupera el listado completo de los sectores ATC predefinidos en el sistema.
    
    Args:
        uc (ManageSectors): Caso de uso inyectado para la gestión de sectores.
        
    Returns:
        List[Dict]: Una lista de objetos JSON representando cada sector y sus parámetros técnicos.
    """
    return uc.get_all()

@router.get("/{id}")
def get_sector(
    id: str, 
    uc: ManageSectors = Depends(get_manage_sectors_use_case)
):
    """
    Obtiene la configuración técnica y parámetros de capacidad de un sector específico por su ID.
    
    Args:
        id (str): Identificador único (UUID) del sector.
        uc (ManageSectors): Instancia del orquestador de persistencia de sectores.
        
    Returns:
        Dict: Los atributos detallados del sector localizado.
        
    Raises:
        HTTPException: Código 404 si el sector no existe en la base de datos.
    """
    sector = uc.get_by_id(id)
    if not sector:
        raise HTTPException(status_code=404, detail="Sector not found")
    return sector

@router.post("/")
def create_sector(
    sector: SectorCreate, 
    uc: ManageSectors = Depends(get_manage_sectors_use_case)
):
    """
    Crea un nuevo sector aeronáutico definiendo sus límites operativos (orígenes/destinos) y tiempos técnicos.
    
    Args:
        sector (SectorCreate): Esquema con la definición del sector y coeficientes de la Circular 006.
        uc (ManageSectors): Ejecutor lógico de la creación de registros.
        
    Returns:
        dict: Objeto con el ID del nuevo sector y mensaje de éxito.
    """
    new_id = uc.create(sector.dict())
    return {"id": new_id, "message": "Sector created"}

@router.put("/{id}")
def update_sector(
    id: str, 
    sector: SectorUpdate, 
    uc: ManageSectors = Depends(get_manage_sectors_use_case)
):
    """
    Actualiza de forma parcial los parámetros técnicos o la definición geográfica de un sector existente.
    
    Args:
        id (str): UUID del sector a modificar.
        sector (SectorUpdate): Objeto con los campos a actualizar (solo se modifican los campos proporcionados).
        uc (ManageSectors): Orquestador de la actualización.
        
    Returns:
        dict: Confirmación de la actualización.
        
    Raises:
        HTTPException: Error 404 si no se encuentra el sector objetivo.
    """
    # Pydantic dict exclude_unset to avoid overwriting with None
    success = uc.update(id, sector.dict(exclude_unset=True))
    if not success:
         raise HTTPException(status_code=404, detail="Sector not found or update failed")
    return {"message": "Sector updated"}

@router.delete("/{id}")
def delete_sector(
    id: str, 
    uc: ManageSectors = Depends(get_manage_sectors_use_case)
):
    """
    Elimina físicamente un sector de la base de datos.
    
    Args:
        id (str): El identificador único del sector.
        uc (ManageSectors): Caso de uso para gestionar la eliminación.
        
    Returns:
        dict: Mensaje de éxito tras la remoción.
        
    Raises:
        HTTPException: Error 404 si el sector no existe.
    """
    success = uc.delete(id)
    if not success:
         raise HTTPException(status_code=404, detail="Sector not found")
    return {"message": "Sector deleted"}

@router.post("/{id}/calculate")
def calculate_capacity(
    id: str, 
    req: CapacityRequest, 
    uc: CalculateSectorCapacity = Depends(get_calculate_sector_capacity_use_case)
):
    """
    Realiza el cálculo matemático de capacidad horaria (CH) y volumen (SCV) para un sector dada una ventana de tiempo.
    Este endpoint es el núcleo de aplicación de la Circular 006 de la Aerocivil.
    
    Args:
        id (str): El sector objetivo del cálculo.
        req (CapacityRequest): Rango de fechas para el análisis de flujos históricos.
        uc (CalculateSectorCapacity): Caso de uso que implementa la lógica matemática y física.
        
    Returns:
        Dict: Resultados detallados de SCV, TFC, TPS y CH Ajustada.
        
    Raises:
        HTTPException: 404 para sectores inválidos o 500 para errores internos de cálculo.
    """
    try:
        filters = {"start_date": req.start_date, "end_date": req.end_date}
        result = uc.execute(id, filters)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
