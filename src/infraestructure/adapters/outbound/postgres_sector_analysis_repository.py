import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional
from datetime import datetime
from src.core.ports.sector_analysis_repository import SectorAnalysisRepository
from src.core.entities.sector_analysis import SectorDetailedAnalysis

class PostgresSectorAnalysisRepository(SectorAnalysisRepository):
    def __init__(self, connection: psycopg2.extensions.connection):
        self.connection = connection

    def get_by_sector_and_date(self, sector: str, date: datetime) -> Optional[SectorDetailedAnalysis]:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT * FROM sector_detailed_analysis
                    WHERE sector = %s AND DATE(hora) = DATE(%s)
                    ORDER BY hora DESC
                    LIMIT 1;
                """
                cursor.execute(query, (sector, date))
                result = cursor.fetchone()
                return SectorDetailedAnalysis(**result) if result else None
        except Exception as e:
            print(f"Error getting sector analysis by date: {e}")
            return None

    def get_by_sector(self, sector: str) -> List[SectorDetailedAnalysis]:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT * FROM sector_detailed_analysis
                    WHERE sector = %s
                    ORDER BY hora DESC;
                """
                cursor.execute(query, (sector,))
                results = cursor.fetchall()
                return [SectorDetailedAnalysis(**row) for row in results]
        except Exception as e:
            print(f"Error getting sector analysis: {e}")
            return []

    def get_all_sectors(self) -> List[str]:
        try:
            with self.connection.cursor() as cursor:
                query = """
                    SELECT DISTINCT sector 
                    FROM sector_detailed_analysis 
                    ORDER BY sector;
                """
                cursor.execute(query)
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting all sectors: {e}")
            return []

    def get_analysis_by_date_range(self, sector: str, start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 10000) -> List[SectorDetailedAnalysis]:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT * FROM sector_detailed_analysis
                    WHERE sector = %s 
                    AND hora BETWEEN %s AND %s
                    ORDER BY hora
                    OFFSET %s LIMIT %s;
                """
                print(f"Executing query with params: sector={sector}, start_date={start_date}, end_date={end_date}, skip={skip}, limit={limit}")
                cursor.execute(query, (sector, start_date, end_date, skip, limit))
                results = cursor.fetchall()
                print(f"Query returned {len(results)} results")
                return [SectorDetailedAnalysis(**row) for row in results]
        except Exception as e:
            print(f"Error getting sector analysis by date range: {e}")
            return []

    def get_total_count(self, sector: str, start_date: datetime, end_date: datetime) -> int:
        try:
            with self.connection.cursor() as cursor:
                query = """
                    SELECT COUNT(*) 
                    FROM sector_detailed_analysis
                    WHERE sector = %s 
                    AND hora BETWEEN %s AND %s;
                """
                cursor.execute(query, (sector, start_date, end_date))
                return cursor.fetchone()[0]
        except Exception as e:
            print(f"Error getting total count: {e}")
            return 0