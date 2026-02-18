from dataclasses import dataclass
from typing import Optional

@dataclass
class FileInfo:
    """
    Entidad que representa la información de un archivo procesado por el sistema.
    
    Se utiliza para el control de ingesta y validación de los datos cargados.
    """
    filename: str  # Nombre del archivo físico cargado
    size_bytes: int  # Tamaño del archivo en bytes
    validation_status: bool  # Indica si el archivo superó las validaciones iniciales
    error_message: Optional[str] = None  # Mensaje detallado en caso de error de proceso
    db_status: Optional[str] = None  # Estado de la integración en la base de datos (ej. 'PROCESSED')
