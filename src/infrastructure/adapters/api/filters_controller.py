from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Any
from src.application.use_cases.manage_filters import ManageFilters

router = APIRouter(prefix="/filters", tags=["filters"])

def get_manage_filters_use_case():
    return ManageFilters()

@router.post("/refresh")
def refresh_filters(use_case: ManageFilters = Depends(get_manage_filters_use_case)):
    """Re-populates the filters cache table from the flights data."""
    try:
        result = use_case.refresh_filters()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{parent_id}/search")
def search_filter_values(
    parent_id: int, 
    q: str = "", 
    use_case: ManageFilters = Depends(get_manage_filters_use_case)
):
    """
    Search values for a specific category (parent_id).
    Parent IDs: 1=Matricula, 2=Tipo Aeronave, 3=Empresa, 4=Tipo Vuelo, 5=Callsign
    """
    return use_case.search_values(parent_id, q)

@router.get("/origins")
def get_origins(use_case: ManageFilters = Depends(get_manage_filters_use_case)):
    """Get distinct origins for filtering."""
    try:
        return use_case.get_origins()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/destinations")
def get_destinations(use_case: ManageFilters = Depends(get_manage_filters_use_case)):
    """Get distinct destinations for filtering."""
    try:
        return use_case.get_destinations()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
