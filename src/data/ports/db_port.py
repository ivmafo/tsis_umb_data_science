from abc import ABC, abstractmethod

class DBPort(ABC):
    @abstractmethod
    def obtener_conexion(self):
        pass

