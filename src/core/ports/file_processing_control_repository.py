#src\core\ports\file_processing_control_repository.py
"""
Puerto que define el contrato para el control de procesamiento de archivos,
siguiendo los principios de arquitectura hexagonal y clean architecture.

Este puerto actúa como una interfaz en el núcleo del dominio que establece
las operaciones necesarias para el seguimiento y control del procesamiento
de archivos, independiente de su implementación en la capa de infraestructura.
"""

from abc import ABC, abstractmethod

class FileProcessingControlRepository(ABC):
    """
    Puerto abstracto que define el contrato para el control de procesamiento de archivos.

    Esta interfaz sigue el patrón de puertos y adaptadores de la arquitectura hexagonal,
    permitiendo que el dominio defina cómo se debe realizar el seguimiento del
    procesamiento de archivos sin depender de implementaciones específicas.

    Methods:
        add_file(file_name: str) -> None:
            Registra un archivo como procesado en el sistema.
            
        is_file_processed(file_name: str) -> bool:
            Verifica si un archivo ya ha sido procesado.
    """

    @abstractmethod
    def add_file(self, file_name: str) -> None:
        """
        Registra un archivo como procesado.

        Args:
            file_name (str): Nombre del archivo que ha sido procesado

        Returns:
            None
        """
        pass

    @abstractmethod
    def is_file_processed(self, file_name: str) -> bool:
        """
        Verifica si un archivo ya ha sido procesado.

        Args:
            file_name (str): Nombre del archivo a verificar

        Returns:
            bool: True si el archivo ya fue procesado, False en caso contrario
        """
        pass

