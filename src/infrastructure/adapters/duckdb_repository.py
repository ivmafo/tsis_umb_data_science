import duckdb
from typing import List, Optional
from src.domain.entities.region import Region
from src.domain.ports.region_repository import RegionRepository
from datetime import datetime

class DuckDBRegionRepository(RegionRepository):
    def __init__(self, db_path: str = "tesis.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return duckdb.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE SEQUENCE IF NOT EXISTS regions_id_seq;
                CREATE TABLE IF NOT EXISTS regions (
                    id INTEGER DEFAULT nextval('regions_id_seq'),
                    name VARCHAR,
                    code VARCHAR,
                    description VARCHAR,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    nivel_min INTEGER,
                    PRIMARY KEY (id)
                );
            """)
            
            # Seeding data
            conn.execute("""
                INSERT INTO regions (id, name, code, description, created_at, updated_at, nivel_min)
                VALUES 
                (1, 'FIR Barranquilla(SKBQ)', 'FIR-SKBQ', 'FIR Barranquilla (SKBQ): Cubre la parte norte del país.', '2025-04-09 16:29:57.58647', '2025-04-09 16:29:57.58647', 0),
                (2, 'FIR Bogotá(SKBO)', 'FIR-SKBO', 'FIR Bogotá (SKBO): Cubre la parte central y sur del país...', '2025-04-09 16:30:32.451245', '2025-04-10 00:50:50.322984', 0)
                ON CONFLICT (id) DO NOTHING;
            """)
            
            # Update sequence to verify it doesn't conflict with manually inserted IDs
            # We encounter issues with the default sequence specific to this environment/file.
            # Strategy: Switch to a new sequence (v2) and sync it.
            try:
                # 1. Create repair sequence
                conn.execute("CREATE SEQUENCE IF NOT EXISTS regions_id_seq_v2;")
                
                # 2. Point table to new sequence
                conn.execute("ALTER TABLE regions ALTER id SET DEFAULT nextval('regions_id_seq_v2');")

                # 3. Get current max ID
                max_id_result = conn.execute("SELECT MAX(id) FROM regions").fetchone()
                max_id = max_id_result[0] if max_id_result and max_id_result[0] is not None else 0
                
                # 4. Advance sequence until it's safe
                curr_seq = conn.execute("SELECT nextval('regions_id_seq_v2')").fetchone()[0]
                while curr_seq <= max_id:
                    curr_seq = conn.execute("SELECT nextval('regions_id_seq_v2')").fetchone()[0]

            except Exception as e:
                print(f"Warning: Could not sync sequence: {e}")

    def get_all(self) -> List[Region]:
        with self._get_connection() as conn:
            result = conn.execute("SELECT id, name, code, description, created_at, updated_at, nivel_min FROM regions").fetchall()
            return [
                Region(
                    id=row[0], name=row[1], code=row[2], description=row[3],
                    created_at=row[4], updated_at=row[5], nivel_min=row[6]
                ) for row in result
            ]

    def get_by_id(self, region_id: int) -> Optional[Region]:
        with self._get_connection() as conn:
            result = conn.execute("SELECT id, name, code, description, created_at, updated_at, nivel_min FROM regions WHERE id = ?", [region_id]).fetchone()
            if result:
                return Region(
                    id=result[0], name=result[1], code=result[2], description=result[3],
                    created_at=result[4], updated_at=result[5], nivel_min=result[6]
                )
            return None

    def create(self, region: Region) -> Region:
        now = datetime.now()
        with self._get_connection() as conn:
            # DuckDB returns inserted row with RETURNING clause
            result = conn.execute("""
                INSERT INTO regions (name, code, description, created_at, updated_at, nivel_min)
                VALUES (?, ?, ?, ?, ?, ?)
                RETURNING id;
            """, [region.name, region.code, region.description, now, now, region.nivel_min]).fetchone()
            
            region.id = result[0]
            region.created_at = now
            region.updated_at = now
            return region

    def update(self, region: Region) -> Optional[Region]:
        now = datetime.now()
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE regions 
                SET name = ?, code = ?, description = ?, updated_at = ?, nivel_min = ?
                WHERE id = ?
            """, [region.name, region.code, region.description, now, region.nivel_min, region.id])
            
            return self.get_by_id(region.id)

    def delete(self, region_id: int) -> bool:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM regions WHERE id = ?", [region_id])
            return True # DuckDB doesn't easily return rowcount in simple execute, assuming success
