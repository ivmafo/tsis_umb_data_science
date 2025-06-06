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
    GetAllConfigsUseCase,
    DeleteConfigUseCase
)
# Add the correct import for GetSectorCapacityUseCase
from src.core.use_cases.get_sector_capacity import GetSectorCapacityUseCase
from src.core.use_cases.get_flight_origins_count import GetFlightOriginsCountUseCase
import os

# Add these imports at the top with other imports
from src.infraestructure.adapters.outbound.postgres_level_range_repository import PostgresLevelRangeRepository
from src.core.use_cases.level_range_use_cases import (
    CreateLevelRangeUseCase,
    UpdateLevelRangeUseCase,
    GetLevelRangeUseCase,
    GetAllLevelRangesUseCase,
    DeleteLevelRangeUseCase,
    GetLevelRangeByRouteUseCase,
    GetLevelRangesByZoneUseCase
)
from src.infraestructure.adapters.outbound.postgres_sector_capacity_repository import PostgresSectorCapacityRepository
# Add to imports
from src.infraestructure.adapters.outbound.postgres_sector_analysis_repository import PostgresSectorAnalysisRepository
from src.core.use_cases.sector_analysis_use_cases import (
    GetSectorAnalysisByDateUseCase,
    GetSectorAnalysisUseCase,
    GetAllSectorsUseCase,
    GetSectorAnalysisByDateRangeUseCase
)
# Add to imports
from src.core.use_cases.get_flight_hourly_counts import GetFlightHourlyCountsUseCase
# Add to imports
from src.infraestructure.adapters.outbound.postgres_region_repository import PostgresRegionRepository
from src.core.use_cases.region_use_cases import (
    GetAllRegionsUseCase,
    GetRegionByIdUseCase,
    CreateRegionUseCase,
    UpdateRegionUseCase,
    DeleteRegionUseCase
)

# Add these imports at the top of the file
from src.core.ports.airport_region_repository import AirportRegionRepository
from src.infraestructure.adapters.outbound.postgres_airport_region_repository import PostgresAirportRegionRepository
from src.core.use_cases.airport_region_use_cases import (
    GetAllAirportRegionsUseCase,
    GetAirportRegionByIdUseCase,
    GetAirportRegionsByIcaoUseCase,
    CreateAirportRegionUseCase,
    UpdateAirportRegionUseCase,
    DeleteAirportRegionUseCase
)

# Primero, agregar el import
from src.core.use_cases.get_flight_yearly_counts import GetFlightYearlyCountsUseCase

# Add to imports at the top
from src.core.use_cases.get_flight_counts_by_fir_use_case import GetFlightCountsByFirUseCase

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
        self.sector_capacity_repository = PostgresSectorCapacityRepository(self.connection)
        # Add this line
        self.sector_analysis_repository = PostgresSectorAnalysisRepository(self.connection)
        self.region_repository = PostgresRegionRepository(self.connection)
        self.airport_region_repository = PostgresAirportRegionRepository(self.connection)

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
        self.get_level_range_by_route_use_case = GetLevelRangeByRouteUseCase(self.level_range_repository)
        self.get_level_ranges_by_zone_use_case = GetLevelRangesByZoneUseCase(self.level_range_repository)

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
        
        # Initialize sector capacity use case
        self.sector_capacity_use_case = GetSectorCapacityUseCase(
            self.sector_capacity_repository
        )
        self.get_flight_hourly_counts_use_case = GetFlightHourlyCountsUseCase(
            self.flight_repository
        )

        # Agregar el caso de uso para el análisis anual
        self.get_flight_yearly_counts_use_case = GetFlightYearlyCountsUseCase(
            self.flight_repository
        )



        # Inicializar casos de uso de regiones
        self.get_all_regions_use_case = GetAllRegionsUseCase(self.region_repository)
        self.get_region_by_id_use_case = GetRegionByIdUseCase(self.region_repository)
        self.create_region_use_case = CreateRegionUseCase(self.region_repository)
        self.update_region_use_case = UpdateRegionUseCase(self.region_repository)
        self.delete_region_use_case = DeleteRegionUseCase(self.region_repository)

        # Initialize airport region use cases
        self.get_all_airport_regions_use_case = GetAllAirportRegionsUseCase(self.airport_region_repository)
        self.get_airport_region_by_id_use_case = GetAirportRegionByIdUseCase(self.airport_region_repository)
        self.get_airport_regions_by_icao_use_case = GetAirportRegionsByIcaoUseCase(self.airport_region_repository)
        self.create_airport_region_use_case = CreateAirportRegionUseCase(self.airport_region_repository)
        self.update_airport_region_use_case = UpdateAirportRegionUseCase(self.airport_region_repository)
        self.delete_airport_region_use_case = DeleteAirportRegionUseCase(self.airport_region_repository)

    def get_sector_capacity_use_case(self):
        return self.sector_capacity_use_case
        
    def cleanup(self):
        if hasattr(self, 'connection') and self.connection:
            self.db_pool.release_connection(self.connection)
            self.db_pool.close_all_connections()

    # Add this property
    @property
    def get_flight_counts_by_fir_use_case(self) -> GetFlightCountsByFirUseCase:
        return GetFlightCountsByFirUseCase(self.flight_repository)