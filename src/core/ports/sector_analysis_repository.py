from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from src.core.entities.sector_analysis import SectorDetailedAnalysis

class SectorAnalysisRepository(ABC):
    @abstractmethod
    def get_by_sector_and_date(self, sector: str, date: datetime) -> Optional[SectorDetailedAnalysis]:
        pass

    @abstractmethod
    def get_by_sector(self, sector: str) -> List[SectorDetailedAnalysis]:
        pass

    @abstractmethod
    def get_all_sectors(self) -> List[str]:
        pass

    @abstractmethod
    def get_analysis_by_date_range(self, sector: str, start_date: datetime, end_date: datetime) -> List[SectorDetailedAnalysis]:
        pass