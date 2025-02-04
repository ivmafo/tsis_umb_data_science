import yaml
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from src.data.puertos.db_port.py import DBPort

class PostgresAdapter(DBPort):
    def __init__(self, config_path: str = 'config.yaml'):
        self.config_path = config_path
        self.config = self._cargar_configuracion()
        self.engine = self._crear_engine()

    def _cargar_configuracion(self) -> dict:
        with open(self.config_path, 'r') as archivo:
            config = yaml.safe_load(archivo)
        return config['database']

    def _crear_engine(self) -> Engine:
        conexion_str = f"postgresql://{self.config['user']}:{self.config['password']}@{self.config['host']}:{self.config['port']}/{self.config['database']}"
        return create_engine(conexion_str)

    def obtener_conexion(self) -> Engine:
        return self.engine
