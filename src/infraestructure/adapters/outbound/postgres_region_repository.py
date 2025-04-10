from typing import List, Optional
from src.core.ports.region_repository import RegionRepository
from src.core.entities.region import Region
from psycopg2.extras import RealDictCursor

class PostgresRegionRepository(RegionRepository):
    def __init__(self, connection):
        self.connection = connection

    def get_all(self) -> List[Region]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id, name, code, description, created_at, updated_at
                FROM regions
                ORDER BY name
            """)
            return [Region(**row) for row in cursor.fetchall()]

    def get_by_id(self, id: int) -> Optional[Region]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id, name, code, description, created_at, updated_at
                FROM regions
                WHERE id = %s
            """, (id,))
            row = cursor.fetchone()
            return Region(**row) if row else None

    def create(self, region_data: dict) -> Region:
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    INSERT INTO regions (name, code, description)
                    VALUES (%s, %s, %s)
                    RETURNING id, name, code, description, created_at, updated_at
                """, (region_data['name'], region_data['code'], region_data.get('description')))
                self.connection.commit()
                result = cursor.fetchone()
                return Region(**result) if result else None
        except Exception as e:
            self.connection.rollback()
            print(f"Error in create: {str(e)}")  # Debug log
            raise

    def update(self, id: int, region_data: dict) -> Optional[Region]:
        set_clause = []
        params = []
        
        if 'name' in region_data:
            set_clause.append("name = %s")
            params.append(region_data['name'])
        if 'code' in region_data:
            set_clause.append("code = %s")
            params.append(region_data['code'])
        if 'description' in region_data:
            set_clause.append("description = %s")
            params.append(region_data['description'])
            
        set_clause.append("updated_at = CURRENT_TIMESTAMP")
        params.append(id)
        
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(f"""
                UPDATE regions
                SET {', '.join(set_clause)}
                WHERE id = %s
                RETURNING id, name, code, description, created_at, updated_at
            """, tuple(params))
            self.connection.commit()
            row = cursor.fetchone()
            return Region(**row) if row else None

    def delete(self, id: int) -> bool:
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM regions WHERE id = %s", (id,))
            self.connection.commit()
            return cursor.rowcount > 0