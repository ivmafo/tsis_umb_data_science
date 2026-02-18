"""Dependency Injection Container."""
from dependency_injector import containers, providers

from ...infrastructure.adapters.polars.polars_data_source import PolarsDataSource
from ...infrastructure.adapters.database.duckdb_metric_repository import DuckDBMetricRepository
from ...infrastructure.config.settings import Settings
from ...infrastructure.adapters.duckdb_repository import DuckDBRegionRepository
from ...infrastructure.adapters.duckdb_airport_repository import DuckDBAirportRepository
from ...infrastructure.adapters.duckdb_region_airport_repository import DuckDBRegionAirportRepository
from ..use_cases.ingest_flights_data import IngestFlightsDataUseCase
from ..use_cases.manage_regions import ManageRegions
from ..use_cases.manage_airports import ManageAirports
from ..use_cases.manage_region_airports import ManageRegionAirports
from ..use_cases.export_raw_flights_use_case import ExportRawFlightsUseCase
from ..use_cases.generate_executive_report import GenerateExecutiveReport
from ..use_cases.manage_sectors import ManageSectors
from ..use_cases.manage_sectors import ManageSectors
from ..use_cases.calculate_sector_capacity import CalculateSectorCapacity
from ..use_cases.predict_daily_demand import PredictDailyDemand
from ..use_cases.predict_peak_hours import PredictPeakHours
from ..use_cases.predict_airline_growth import PredictAirlineGrowth
from ..use_cases.predict_sector_saturation import PredictSectorSaturation
from ..use_cases.predict_seasonal_trend import PredictSeasonalTrend


class Container(containers.DeclarativeContainer):
    """
    Dependency Injection container.
    
    This wires together all dependencies following the dependency inversion principle.
    The container knows about concrete implementations but use cases only depend on
    abstract interfaces.
    """
    
    # Configuration
    config = providers.Singleton(Settings)
    
    # Infrastructure - Data Source (Polars adapter)
    data_source_repository = providers.Singleton(
        PolarsDataSource,
        config=config
    )
    
    # Infrastructure - Persistence (DuckDB adapter)
    metric_repository = providers.Singleton(
        DuckDBMetricRepository,
        database_path=config.provided.database_path
    )

    regions_repository = providers.Singleton(
        DuckDBRegionRepository,
        db_path=config.provided.database_path
    )

    airports_repository = providers.Singleton(
        DuckDBAirportRepository,
        db_path=config.provided.database_path,
        csv_path="data/raw/data.csv" # Or configured path
    )

    region_airports_repository = providers.Singleton(
        DuckDBRegionAirportRepository,
        db_path=config.provided.database_path,
        csv_path="data/raw/region_airports.csv" # Or configured path
    )
    
    # Application - Use Cases
    # Application - Use Cases
    # Metrics use cases removed as requested

    ingest_flights_data_use_case = providers.Factory(
        IngestFlightsDataUseCase,
        db_path=config.provided.database_path,
        data_dir=config.provided.data_directory
    )

    manage_regions_use_case = providers.Factory(
        ManageRegions,
        repository=regions_repository
    )

    manage_airports_use_case = providers.Factory(
        ManageAirports,
        repository=airports_repository
    )

    manage_region_airports_use_case = providers.Factory(
        ManageRegionAirports,
        repository=region_airports_repository,
        airport_repository=airports_repository,
        region_repository=regions_repository
    )


    export_raw_flights_use_case = providers.Factory(
        ExportRawFlightsUseCase,
        db_path=config.provided.database_path
    )

    generate_executive_report_use_case = providers.Factory(
        GenerateExecutiveReport,
        db_path=config.provided.database_path
    )

    manage_sectors_use_case = providers.Factory(
        ManageSectors,
        db_path=config.provided.database_path
    )

    calculate_sector_capacity_use_case = providers.Factory(
        CalculateSectorCapacity,
        db_path=config.provided.database_path
    )

    predict_daily_demand_use_case = providers.Factory(
        PredictDailyDemand,
        db_path=config.provided.database_path
    )

    predict_peak_hours_use_case = providers.Factory(
        PredictPeakHours,
        db_path=config.provided.database_path
    )

    predict_airline_growth_use_case = providers.Factory(
        PredictAirlineGrowth,
        db_path=config.provided.database_path
    )

    predict_sector_saturation_use_case = providers.Factory(
        PredictSectorSaturation,
        db_path=config.provided.database_path
    )

    predict_seasonal_trend_use_case = providers.Factory(
        PredictSeasonalTrend,
        db_path=config.provided.database_path
    )


# Global container instance
container = Container()

def get_ingest_flights_use_case() -> IngestFlightsDataUseCase:
    """Dependency provider for IngestFlightsDataUseCase."""
    return container.ingest_flights_data_use_case()

def get_manage_regions_use_case() -> ManageRegions:
    """Dependency provider for ManageRegions."""
    return container.manage_regions_use_case()

def get_manage_airports_use_case() -> ManageAirports:
    """Dependency provider for ManageAirports."""
    return container.manage_airports_use_case()

def get_manage_region_airports_use_case() -> ManageRegionAirports:
    """Dependency provider for ManageRegionAirports."""
    return container.manage_region_airports_use_case()

def get_export_raw_flights_use_case() -> ExportRawFlightsUseCase:
    """Dependency provider for ExportRawFlightsUseCase."""
    return container.export_raw_flights_use_case()

def get_generate_executive_report_use_case() -> GenerateExecutiveReport:
    return container.generate_executive_report_use_case()

def get_manage_sectors_use_case() -> ManageSectors:
    return container.manage_sectors_use_case()

def get_calculate_sector_capacity_use_case() -> CalculateSectorCapacity:
    return container.calculate_sector_capacity_use_case()

def get_predict_daily_demand_use_case() -> PredictDailyDemand:
    return container.predict_daily_demand_use_case()

def get_predict_peak_hours_use_case() -> PredictPeakHours:
    return container.predict_peak_hours_use_case()

def get_predict_airline_growth_use_case() -> PredictAirlineGrowth:
    return container.predict_airline_growth_use_case()

def get_predict_sector_saturation_use_case() -> PredictSectorSaturation:
    return container.predict_sector_saturation_use_case()

def get_predict_seasonal_trend_use_case() -> PredictSeasonalTrend:
    return container.predict_seasonal_trend_use_case()


