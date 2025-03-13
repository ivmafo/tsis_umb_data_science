from typing import List, Optional
from datetime import datetime
from psycopg2.extras import RealDictCursor
from src.core.ports.sector_capacity_repository import SectorCapacityRepository
from src.core.entities.sector_capacity import SectorCapacityResponse

class PostgresSectorCapacityRepository(SectorCapacityRepository):
    def __init__(self, connection):
        self.connection = connection

    def get_sectors(self) -> List[str]:
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT origen 
                    FROM fligths 
                    WHERE origen IS NOT NULL
                    ORDER BY origen
                """)
                results = cursor.fetchall()
                return [row[0] for row in results if row[0]]
        except Exception as e:
            print(f"Error obteniendo sectores: {str(e)}")
            return []

    def get_sector_capacity(self, sector: str, date: datetime) -> Optional[SectorCapacityResponse]:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "SELECT * FROM calculate_detailed_sector_capacity(%s, %s::timestamp)",
                    (sector.upper(), date)
                )
                result = cursor.fetchone()
                
                if not result:
                    return None

                return SectorCapacityResponse(
                    sector=result['sector'],
                    hora=result['hora'],
                    tps=result['tps'],
                    tfc=result['tfc'],
                    tm=result['tm'],
                    tc=result['tc'],
                    tt=result['tt'],
                    scv_value=result['scv_value'],
                    capacidad_horaria_base=result['capacidad_horaria_base'],
                    capacidad_horaria_alta=result['capacidad_horaria_alta'],
                    capacidad_horaria_baja=result['capacidad_horaria_baja'],
                    carga_trabajo_total_base=result['carga_trabajo_total_base'],
                    carga_trabajo_total_alta=result['carga_trabajo_total_alta'],
                    carga_trabajo_total_baja=result['carga_trabajo_total_baja']
                )
        except Exception as e:
            print(f"Error obteniendo capacidad del sector: {str(e)}")
            raise