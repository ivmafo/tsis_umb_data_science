import duckdb
import os
from typing import List, Optional, Tuple
from src.domain.entities.airport import Airport
from src.domain.ports.airport_repository import AirportRepository

class DuckDBAirportRepository(AirportRepository):
    def __init__(self, db_path: str = "tesis.db", csv_path: str = "data/raw/data.csv"):
        self.db_path = db_path
        self.csv_path = csv_path
        self._init_db()

    def _get_connection(self):
        return duckdb.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            # Create sequence for new IDs
            conn.execute("CREATE SEQUENCE IF NOT EXISTS airports_id_seq START 1;")
            
            # Check if table exists
            table_exists = conn.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = 'airports'").fetchone()[0] > 0
            
            if not table_exists:
                # Create table
                conn.execute(f"""
                    CREATE TABLE airports (
                        id INTEGER DEFAULT nextval('airports_id_seq'),
                        icao_code VARCHAR,
                        iata_code VARCHAR,
                        name VARCHAR,
                        city VARCHAR,
                        country VARCHAR,
                        latitude DOUBLE,
                        longitude DOUBLE,
                        altitude INTEGER,
                        timezone DOUBLE,
                        dst VARCHAR,
                        type VARCHAR,
                        source VARCHAR,
                        reference_code VARCHAR DEFAULT '4E',
                        has_rapid_exit_taxiway BOOLEAN DEFAULT FALSE,
                        requires_backtrack BOOLEAN DEFAULT FALSE,
                        PRIMARY KEY (id)
                    );
                """)
                
            # Siempre intentamos agregar las columnas en caso de que la tabla ya exista (migración en caliente)
            try:
                conn.execute("ALTER TABLE airports ADD COLUMN reference_code VARCHAR DEFAULT '4E';")
            except Exception: pass
            try:
                conn.execute("ALTER TABLE airports ADD COLUMN has_rapid_exit_taxiway BOOLEAN DEFAULT FALSE;")
            except Exception: pass
            try:
                conn.execute("ALTER TABLE airports ADD COLUMN requires_backtrack BOOLEAN DEFAULT FALSE;")
            except Exception: pass
            
            # Import from CSV if exists and table is empty
            if os.path.exists(self.csv_path):
                row_count = conn.execute("SELECT count(*) FROM airports").fetchone()[0]
                if row_count == 0:
                    # We use a temp table or direct insert to handle the ID generation
                    # read_csv_auto infers types, but we want to map them to our schema
                    # The CSV doesn't have an ID column, so we insert into our table which auto-generates IDs
                    conn.execute(f"""
                        INSERT INTO airports (icao_code, iata_code, name, city, country, latitude, longitude, altitude, timezone, dst, type, source)
                        SELECT * FROM read_csv_auto('{self.csv_path}', nullstr='\\N');
                    """)
                
                # Sync sequence just in case, though nextval should have been used for each row
                max_id = conn.execute("SELECT MAX(id) FROM airports").fetchone()[0]
                if max_id:
                    # Ensure sequence is ahead
                    curr = conn.execute("SELECT nextval('airports_id_seq')").fetchone()[0]
                    while curr <= max_id:
                        curr = conn.execute("SELECT nextval('airports_id_seq')").fetchone()[0]

    def get_paginated(self, page: int, page_size: int, search: str = "") -> Tuple[List[Airport], int]:
        offset = (page - 1) * page_size
        with self._get_connection() as conn:
            # Base query
            query = "SELECT * FROM airports"
            count_query = "SELECT COUNT(*) FROM airports"
            params = []
            
            if search:
                search_term = f"%{search}%"
                where_clause = """ WHERE 
                    name ILIKE ? OR 
                    city ILIKE ? OR 
                    country ILIKE ? OR 
                    icao_code ILIKE ? OR 
                    iata_code ILIKE ?
                """
                query += where_clause
                count_query += where_clause
                params = [search_term] * 5
            
            # Get total count
            total = conn.execute(count_query, params).fetchone()[0]
            
            # Get data
            query += " ORDER BY id LIMIT ? OFFSET ?"
            params.extend([page_size, offset])
            
            rows = conn.execute(query, params).fetchall()
            
            items = [
                Airport(
                    id=row[0], icao_code=row[1], iata_code=row[2], name=row[3],
                    city=row[4], country=row[5], latitude=row[6], longitude=row[7],
                    altitude=row[8], timezone=row[9], dst=row[10], type=row[11], source=row[12],
                    reference_code=row[13] if len(row)>13 and row[13] is not None else "4E", 
                    has_rapid_exit_taxiway=row[14] if len(row)>14 and row[14] is not None else False, 
                    requires_backtrack=row[15] if len(row)>15 and row[15] is not None else False
                ) for row in rows
            ]
            
            return items, total

    def get_by_id(self, airport_id: int) -> Optional[Airport]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM airports WHERE id = ?", [airport_id]).fetchone()
            if row:
                return Airport(
                    id=row[0], icao_code=row[1], iata_code=row[2], name=row[3],
                    city=row[4], country=row[5], latitude=row[6], longitude=row[7],
                    altitude=row[8], timezone=row[9], dst=row[10], type=row[11], source=row[12],
                    reference_code=row[13] if len(row)>13 and row[13] is not None else "4E", 
                    has_rapid_exit_taxiway=row[14] if len(row)>14 and row[14] is not None else False, 
                    requires_backtrack=row[15] if len(row)>15 and row[15] is not None else False
                )
            return None

    def get_by_icao(self, icao_code: str) -> Optional[Airport]:
        with self._get_connection() as conn:
            # Case insensitive search usually better for codes
            row = conn.execute("SELECT * FROM airports WHERE icao_code ILIKE ?", [icao_code]).fetchone()
            if row:
                return Airport(
                    id=row[0], icao_code=row[1], iata_code=row[2], name=row[3],
                    city=row[4], country=row[5], latitude=row[6], longitude=row[7],
                    altitude=row[8], timezone=row[9], dst=row[10], type=row[11], source=row[12],
                    reference_code=row[13] if len(row)>13 and row[13] is not None else "4E", 
                    has_rapid_exit_taxiway=row[14] if len(row)>14 and row[14] is not None else False, 
                    requires_backtrack=row[15] if len(row)>15 and row[15] is not None else False
                )
            return None

    def create(self, airport: Airport) -> Airport:
        with self._get_connection() as conn:
            # Let DB handle ID via sequence
            res = conn.execute("""
                INSERT INTO airports (icao_code, iata_code, name, city, country, latitude, longitude, altitude, timezone, dst, type, source, reference_code, has_rapid_exit_taxiway, requires_backtrack)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                RETURNING id;
            """, [
                airport.icao_code, airport.iata_code, airport.name, airport.city, airport.country,
                airport.latitude, airport.longitude, airport.altitude, airport.timezone,
                airport.dst, airport.type, airport.source, airport.reference_code,
                airport.has_rapid_exit_taxiway, airport.requires_backtrack
            ]).fetchone()
            
            airport.id = res[0]
            return airport

    def update(self, airport: Airport) -> Optional[Airport]:
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE airports 
                SET icao_code=?, iata_code=?, name=?, city=?, country=?, latitude=?, longitude=?, altitude=?, timezone=?, dst=?, type=?, source=?,
                reference_code=?, has_rapid_exit_taxiway=?, requires_backtrack=?
                WHERE id = ?
            """, [
                airport.icao_code, airport.iata_code, airport.name, airport.city, airport.country,
                airport.latitude, airport.longitude, airport.altitude, airport.timezone,
                airport.dst, airport.type, airport.source, airport.reference_code,
                airport.has_rapid_exit_taxiway, airport.requires_backtrack, airport.id
            ])
            
            return self.get_by_id(airport.id)

    def delete(self, airport_id: int) -> bool:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM airports WHERE id = ?", [airport_id])
            return True
