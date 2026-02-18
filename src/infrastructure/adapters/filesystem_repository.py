import os
import openpyxl
import io
import logging
import zipfile
from typing import List, BinaryIO, Union
from src.domain.entities.file_info import FileInfo
from src.domain.ports.file_repository import FileRepository

class FilesystemRepository(FileRepository):
    def __init__(self, data_directory: str):
        self.data_directory = data_directory
        os.makedirs(data_directory, exist_ok=True)
        
        # Columnas requeridas para validación (basado en análisis previo)
        self.required_columns = [
            'Fecha', 'ID', 'SSR', 'Callsign', 'Empresa', 
            'Origen', 'Destino', 'Nivel'
        ]

    def list_files(self) -> List[FileInfo]:
        files = []
        if not os.path.exists(self.data_directory):
            return []
            
        for filename in os.listdir(self.data_directory):
            if filename.endswith(".xlsx"):
                filepath = os.path.join(self.data_directory, filename)
                size = os.path.getsize(filepath)
                # Asumimos que los archivos ya existentes son válidos o se validarán al leer
                files.append(FileInfo(filename=filename, size_bytes=size, validation_status=True))
        return files

    def save_file(self, filename: str, content: Union[BinaryIO, bytes]) -> FileInfo:
        filepath = os.path.join(self.data_directory, filename)
        logger = logging.getLogger(__name__)
        
        # Validar antes de guardar permanentemente
        try:
            # Manejar tanto bytes como stream
            if isinstance(content, bytes):
                file_content = content
            else:
                content.seek(0)
                file_content = content.read()
            
            file_size = len(file_content)
            logger.info(f"Procesando archivo {filename}, tamaño: {file_size} bytes")
            
            if file_size == 0:
                return FileInfo(
                    filename=filename,
                    size_bytes=0,
                    validation_status=False,
                    error_message="El archivo está vacío"
                )

            # Usar un buffer de memoria para que openpyxl no tenga problemas con el stream de FastAPI
            buffer = io.BytesIO(file_content)
            
            # 1. Verificar Magic Numbers (Firma del archivo)
            buffer.seek(0)
            magic = buffer.read(8)
            buffer.seek(0) # Siempre resetear
            
            # ZIP magic numbers: PK.. (50 4B 03 04)
            is_zip = magic.startswith(b'PK\x03\x04')
            # OLE2 magic numbers (XLS antiguo): D0 CF 11 E0 A1 B1 1A E1
            is_ole = magic.startswith(b'\xd0\xcf\x11\xe0')
            
            logger.info(f"DEBUG: Magic numbers para {filename}: {magic.hex()} (ZIP: {is_zip}, OLE: {is_ole})")
            print(f"DEBUG: Magic numbers para {filename}: {magic.hex()} (ZIP: {is_zip}, OLE: {is_ole})")

            if not is_zip:
                if is_ole:
                    return FileInfo(
                        filename=filename,
                        size_bytes=file_size,
                        validation_status=False,
                        error_message="El archivo parece ser un Excel antiguo (.xls). Por favor, guárdelo como 'Libro de Excel (*.xlsx)' e intente de nuevo."
                    )
                else:
                    return FileInfo(
                        filename=filename,
                        size_bytes=file_size,
                        validation_status=False,
                        error_message=f"El archivo no tiene el formato técnico de Excel .xlsx esperado (No es un archivo ZIP válido). Firma detectada: {magic.hex()[:8]}"
                    )

            # openpyxl necesita un archivo real o un objeto tipo archivo
            # Un archivo .xlsx es técnicamente un archivo ZIP
            try:
                # Verificar con zipfile directamente primero por si openpyxl da error genérico
                if not zipfile.is_zipfile(buffer):
                    raise zipfile.BadZipFile("No es un archivo ZIP válido según zipfile")
                
                buffer.seek(0)
                wb = openpyxl.load_workbook(buffer, read_only=True, data_only=True)
                sheet = wb.active
                # Obtener cabeceras (primera fila)
                headers = [str(cell.value).strip() if cell.value else "" for cell in next(sheet.rows)]
            except Exception as zip_err:
                logger.error(f"Error de formato Excel/Zip para {filename}: {str(zip_err)}")
                return FileInfo(
                    filename=filename,
                    size_bytes=file_size,
                    validation_status=False,
                    error_message=f"El archivo .xlsx está corrupto o no se puede abrir: {str(zip_err)}"
                )
            
            # Verificar headers
            missing = [col for col in self.required_columns if col not in headers]
            
            if missing:
                return FileInfo(
                    filename=filename,
                    size_bytes=0,
                    validation_status=False,
                    error_message=f"Faltan columnas requeridas: {', '.join(missing)}"
                )
                
            # Si es válido, guardar el contenido que ya leímos
            with open(filepath, "wb") as f:
                f.write(file_content)
                
            return FileInfo(
                filename=filename,
                size_bytes=os.path.getsize(filepath),
                validation_status=True,
                error_message=None
            )
            
        except Exception as e:
            logger.error(f"Error inesperado al guardar archivo {filename}: {str(e)}")
            return FileInfo(
                filename=filename,
                size_bytes=0,
                validation_status=False,
                error_message=f"Error inesperado: {str(e)}"
            )
