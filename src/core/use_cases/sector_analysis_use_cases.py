from datetime import datetime
from typing import List, Optional
from src.core.ports.sector_analysis_repository import SectorAnalysisRepository
from src.core.entities.sector_analysis import SectorDetailedAnalysis

class GetSectorAnalysisByDateUseCase:
    def __init__(self, sector_analysis_repository: SectorAnalysisRepository):
        self.sector_analysis_repository = sector_analysis_repository

    def execute(self, sector: str, date: datetime) -> Optional[SectorDetailedAnalysis]:
        return self.sector_analysis_repository.get_by_sector_and_date(sector, date)

class GetSectorAnalysisUseCase:
    def __init__(self, sector_analysis_repository: SectorAnalysisRepository):
        self.sector_analysis_repository = sector_analysis_repository

    def execute(self, sector: str) -> List[SectorDetailedAnalysis]:
        return self.sector_analysis_repository.get_by_sector(sector)

class GetAllSectorsUseCase:
    def __init__(self, sector_analysis_repository: SectorAnalysisRepository):
        self.sector_analysis_repository = sector_analysis_repository

    def execute(self) -> List[str]:
        return self.sector_analysis_repository.get_all_sectors()

class GetSectorAnalysisByDateRangeUseCase:
    def __init__(self, sector_analysis_repository: SectorAnalysisRepository):
        self.sector_analysis_repository = sector_analysis_repository

    def execute(self, sector: str, start_date: datetime, end_date: datetime) -> List[SectorDetailedAnalysis]:
        return self.sector_analysis_repository.get_analysis_by_date_range(
            sector, 
            start_date, 
            end_date
        )