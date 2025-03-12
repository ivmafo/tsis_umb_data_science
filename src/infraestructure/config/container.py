from src.infraestructure.config.database import PostgresConnectionPool
from src.infraestructure.adapters.outbound.postgres_flight_repository import PostgresFlightRepository
from src.infraestructure.adapters.outbound.postgres_file_processing_control_repository import PostgresFileProcessingControlRepository
from src.infraestructure.adapters.outbound.postgres_config_repository import PostgresConfigRepository
from src.infraestructure.adapters.outbound.file_system_repository import LocalFileSystemRepository
from src.core.use_cases.process_flights_from_excel import ProcessFlightsFromExcelUseCase
from src.core.use_cases.process_directory_flights import ProcessDirectoryFlightsUseCase
from src.core.use_cases.config_use_cases import (
    CreateConfigUseCase, 
    UpdateConfigUseCase, 
    GetConfigUseCase, 
    GetAllConfigsUseCase
)
from src.core.use_cases.get_flight_origins_count import GetFlightOriginsCountUseCase
import os

# Add these imports at the top with other imports
from src.infraestructure.adapters.outbound.postgres_level_range_repository import PostgresLevelRangeRepository
from src.core.use_cases.level_range_use_cases import (
    CreateLevelRangeUseCase,
    UpdateLevelRangeUseCase,
    GetLevelRangeUseCase,
    GetAllLevelRangesUseCase,
    DeleteLevelRangeUseCase
)

class DependencyContainer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DependencyContainer, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Conexión a base de datos
        self.db_pool = PostgresConnectionPool()
        self.connection = self.db_pool.get_connection()

        # Base path
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        # Repositorios
        self._init_repositories()
        
        # Casos de uso
        self._init_use_cases()

    def _init_repositories(self):
        self.file_system_repository = LocalFileSystemRepository(self.base_path)
        self.flight_repository = PostgresFlightRepository(self.connection)
        self.file_repository = PostgresFileProcessingControlRepository(self.connection)
        self.config_repository = PostgresConfigRepository(self.connection)
        self.level_range_repository = PostgresLevelRangeRepository(self.connection)

    def _init_use_cases(self):
        # Casos de uso de configuración
        self.create_config_use_case = CreateConfigUseCase(self.config_repository)
        self.update_config_use_case = UpdateConfigUseCase(self.config_repository)
        self.get_config_use_case = GetConfigUseCase(self.config_repository)
        self.get_all_configs_use_case = GetAllConfigsUseCase(self.config_repository)

        # Casos de uso de rangos de nivel
        self.create_level_range_use_case = CreateLevelRangeUseCase(self.level_range_repository)
        self.update_level_range_use_case = UpdateLevelRangeUseCase(self.level_range_repository)
        self.get_level_range_use_case = GetLevelRangeUseCase(self.level_range_repository)
        self.get_all_level_ranges_use_case = GetAllLevelRangesUseCase(self.level_range_repository)
        self.delete_level_range_use_case = DeleteLevelRangeUseCase(self.level_range_repository)

        # Casos de uso de vuelos
        self.process_flights_use_case = ProcessFlightsFromExcelUseCase(
            self.flight_repository,
            self.file_repository
        )
        self.process_directory_use_case = ProcessDirectoryFlightsUseCase(
            self.flight_repository,
            self.file_repository,
            self.file_system_repository
        )
        
        # Casos de uso
        self.get_flight_origins_count_use_case = GetFlightOriginsCountUseCase(
            self.flight_repository
        )

    def cleanup(self):
        if hasattr(self, 'connection') and self.connection:
            self.db_pool.release_connection(self.connection)
            self.db_pool.close_all_connections()