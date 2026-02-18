import duckdb
import logging
from typing import List, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

class ManageFilters:
    def __init__(self, db_path: str = "data/metrics.duckdb"):
        self.db_path = db_path

    def refresh_filters(self) -> dict:
        """
        Truncate and repopulate the filters_values table based on current flights data.
        """
        conn = duckdb.connect(self.db_path)
        try:
            # 1. Ensure table exists
            conn.execute("CREATE SEQUENCE IF NOT EXISTS filter_id_seq")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS filters_values (
                    id BIGINT DEFAULT nextval('filter_id_seq') PRIMARY KEY,
                    value VARCHAR,
                    parent_id BIGINT,
                    category_code VARCHAR -- To easily identify parent types (e.g. 'MATRICULA')
                )
            """)
            
            # 2. Clear existing data
            logger.info("Refreshing filters: Clearing table...")
            conn.execute("DELETE FROM filters_values")
            # Restart sequence to avoid conflicts with manual IDs 1-5
            try:
                conn.execute("ALTER SEQUENCE filter_id_seq RESTART WITH 100")
            except:
                pass
            
            # 3. Insert Root Categories (Parents)
            # id:1, value: matricula
            # id:2, value: tipo_aeronave
            # id:3, value: empresa
            # id:4, value: tipo_vuelo
            # id:5, value: callsign
            categories = [
                (1, 'Matrícula', 'MATRICULA'),
                (2, 'Tipo de Aeronave', 'TIPO_AERONAVE'),
                (3, 'Empresa', 'EMPRESA'),
                (4, 'Tipo de Vuelo', 'TIPO_VUELO'),
                (5, 'Callsign', 'CALLSIGN')
            ]
            
            # Reset sequence to ensure IDs don't conflict or just force IDs for roots?
            # User specified IDs 1-5 for roots.
            # Let's insert them explicitly.
            conn.executemany("INSERT INTO filters_values (id, value, parent_id, category_code) VALUES (?, ?, NULL, ?)", 
                             categories)
            
            # 4. Populate Children
            logger.info("Populating filter values from flights...")
            
            # Matricula (Parent 1)
            conn.execute("""
                INSERT INTO filters_values (value, parent_id, category_code)
                SELECT DISTINCT matricula, 1, 'MATRICULA_VAL' FROM flights WHERE matricula IS NOT NULL
            """)
            
            # Tipo Aeronave (Parent 2)
            conn.execute("""
                INSERT INTO filters_values (value, parent_id, category_code)
                SELECT DISTINCT tipo_aeronave, 2, 'TIPO_AERONAVE_VAL' FROM flights WHERE tipo_aeronave IS NOT NULL
            """)
            
            # Empresa (Parent 3)
            conn.execute("""
                INSERT INTO filters_values (value, parent_id, category_code)
                SELECT DISTINCT empresa, 3, 'EMPRESA_VAL' FROM flights WHERE empresa IS NOT NULL
            """)
            
            # Tipo Vuelo (Parent 4)
            conn.execute("""
                INSERT INTO filters_values (value, parent_id, category_code)
                SELECT DISTINCT tipo_vuelo, 4, 'TIPO_VUELO_VAL' FROM flights WHERE tipo_vuelo IS NOT NULL
            """)
             
            # Callsign (Parent 5)
            # Note: callsign might be high cardinality
            conn.execute("""
                INSERT INTO filters_values (value, parent_id, category_code)
                SELECT DISTINCT callsign, 5, 'CALLSIGN_VAL' FROM flights WHERE callsign IS NOT NULL
            """)
            
            row_count = conn.execute("SELECT count(*) FROM filters_values").fetchone()[0]
            logger.info(f"Filters refreshed. Total records: {row_count}")
            
            return {"status": "success", "total_records": row_count}
            
        except Exception as e:
            logger.error(f"Error refreshing filters: {e}")
            raise e
        finally:
            conn.close()

    def search_values(self, parent_id: int, query: str = "") -> List[Dict[str, Any]]:
        """
        Search for values within a specific category (parent_id).
        """
        conn = duckdb.connect(self.db_path, read_only=True)
        try:
            # Check table existence first to avoid errors on empty state
            try:
                 conn.execute("SELECT 1 FROM filters_values LIMIT 1")
            except:
                 return []

            sql = """
                SELECT id, value 
                FROM filters_values 
                WHERE parent_id = ? AND value ILIKE ?
                ORDER BY value
                LIMIT 50
            """
            pattern = f"%{query}%"
            results = conn.execute(sql, [parent_id, pattern]).fetchall()
            
            return [{"id": r[0], "value": r[1]} for r in results]
        except Exception as e:
            logger.error(f"Error searching filters: {e}")
            return []
        finally:
            conn.close()

    def get_origins(self) -> List[str]:
        """Fetch distinct origins from flights table."""
        conn = duckdb.connect(self.db_path, read_only=True)
        try:
             # Check if flights table exists
            try:
                conn.execute("SELECT 1 FROM flights LIMIT 1")
            except:
                return []

            result = conn.execute("""
                SELECT DISTINCT icao_code 
                FROM airports 
                WHERE icao_code IS NOT NULL 
                ORDER BY icao_code
            """).fetchall()
            return [row[0] for row in result]
        except Exception as e:
            logger.error(f"Error fetching origins: {e}")
            return []
        finally:
            conn.close()

    def get_destinations(self) -> List[str]:
        """Fetch distinct destinations from flights table."""
        conn = duckdb.connect(self.db_path, read_only=True)
        try:
            try:
                conn.execute("SELECT 1 FROM flights LIMIT 1")
            except:
                return []

            result = conn.execute("""
                SELECT DISTINCT icao_code 
                FROM airports 
                WHERE icao_code IS NOT NULL 
                ORDER BY icao_code
            """).fetchall()
            return [row[0] for row in result]
        except Exception as e:
            logger.error(f"Error fetching destinations: {e}")
            return []
        finally:
            conn.close()
