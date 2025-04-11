from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import traceback
from fastapi.responses import JSONResponse
from src.infraestructure.config.container import DependencyContainer

router = APIRouter()
container = DependencyContainer()

class ConfigRequest(BaseModel):
    key: str
    value: str

@router.get("")
async def get_configs():
    try:
        configs = container.get_all_configs_use_case.execute()
        return configs
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al obtener configuraciones: {str(e)}")

@router.get("/{key}")
async def get_config(key: str):
    try:
        config = container.get_config_use_case.execute(key)
        return config
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al obtener configuración: {str(e)}")

@router.post("")
async def create_config(config: ConfigRequest):
    try:
        result = container.create_config_use_case.execute(config.dict())
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al crear configuración: {str(e)}")

@router.put("/{key}")
async def update_config(key: str, config: ConfigRequest):
    try:
        result = container.update_config_use_case.execute(key, config.value)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al actualizar configuración: {str(e)}")

@router.delete("/{key}")
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