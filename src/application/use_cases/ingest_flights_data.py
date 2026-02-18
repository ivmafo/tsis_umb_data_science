import duckdb
import polars as pl
import glob
import os
import logging
import time
from datetime import datetime
import pandas as pd
from src.infrastructure.utils.date_parser import DateParser

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IngestFlightsDataUseCase:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(IngestFlightsDataUseCase, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path: str = "data/metrics.duckdb", data_dir: str = "data"):
        # Prevent re-initialization if singleton wrapper logic isn't perfect, though __new__ handles creation
        if not hasattr(self, 'initialized'):
            self.db_path = db_path
            self.data_dir = data_dir
            
            # Column mapping
            self.column_mapping = {
                "Fecha": "fecha", "fecha": "fecha",
                "id": "id", "ID": "id", "Id": "id",
                "sid": "sid", "SID": "sid", "Sid": "sid",
                "SSR": "ssr", "ssr": "ssr",
                "callsign": "callsign", "Callsign": "callsign", "Call sign": "callsign", "call-sign": "callsign", "CallSign": "callsign",
                "matricula": "matricula", "Matrícula": "matricula",
                "tipo_aeronave": "tipo_aeronave", "Tip Aer": "tipo_aeronave", "Tipo Aeronave": "tipo_aeronave",
                "empresa": "empresa", "Empresa": "empresa",
                "numero_vuelo": "numero_vuelo", "# Vuelo": "numero_vuelo", "Numero de Vuelo": "numero_vuelo",
                "tipo_vuelo": "tipo_vuelo", "Tip Vuel": "tipo_vuelo", "Tipo de Vuelo": "tipo_vuelo",
                "tiempo_inicial": "tiempo_inicial", "Tiempo Inicial": "tiempo_inicial",
                "origen": "origen", "Origen": "origen",
                "fecha_salida": "fecha_salida", "Fec Sal": "fecha_salida", "Fecha de Salida": "fecha_salida",
                "hora_salida": "hora_salida", "Hr Sal": "hora_salida", "Hora de Salida": "hora_salida",
                "Hora PV": "hora_pv", "hora_pv": "hora_pv",
                "destino": "destino", "Destino": "destino",
                "fecha_llegada": "fecha_llegada", "Fec Lle": "fecha_llegada", "Fecha de Llegada": "fecha_llegada",
                "hora_llegada": "hora_llegada", "Hr Lle": "hora_llegada", "Hora de Llegada": "hora_llegada",
                "nivel": "nivel", "Nivel": "nivel",
                "duracion": "duracion", "Duración": "duracion",
                "distancia": "distancia", "Distancia": "distancia",
                "velocidad": "velocidad", "Velocidad": "velocidad",
                "Eq SSR": "eq_ssr", "eq_ssr": "eq_ssr",
                "nombre_origen": "nombre_origen", "Nombre origen ZZZZ": "nombre_origen", "Nombre Origen": "nombre_origen",
                "nombre_destino": "nombre_destino", "Nombre destino ZZZZ": "nombre_destino", "Nombre Destino": "nombre_destino",
                "Fecha de Registro": "fecha_registro", "fecha_registro": "fecha_registro"
            }

            # Target columns list
            self.target_columns = [
                'id', 'file_id', 'fecha', 'sid', 'ssr', 'callsign', 'matricula', 'tipo_aeronave', 'empresa', 
                'numero_vuelo', 'tipo_vuelo', 'tiempo_inicial', 'origen', 'fecha_salida', 
                'hora_salida', 'hora_pv', 'destino', 'fecha_llegada', 'hora_llegada', 'nivel', 
                'duracion', 'distancia', 'velocidad', 'eq_ssr', 'nombre_origen', 
                'nombre_destino', 'fecha_registro'
            ]
            
            # State tracking
            self.current_file = None
            self.total_files = 0
            self.processed_count = 0
            self.initialized = True

    def _init_db(self, conn):
        """Initialize database tables and sequences."""
        
        # 1. Tracking Table (Must exist before Flights for FK)
        conn.execute("CREATE SEQUENCE IF NOT EXISTS tracking_id_seq")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS file_processing_control (
                id BIGINT DEFAULT nextval('tracking_id_seq') PRIMARY KEY,
                file_name VARCHAR,
                processed_at TIMESTAMP,
                status VARCHAR, 
                row_count BIGINT,
                error_message VARCHAR
            )
        """)

        # 2. Main Flights Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS flights (
                id BIGINT, 
                file_id BIGINT REFERENCES file_processing_control(id), -- Added FK
                fecha DATE,
                sid VARCHAR,
                ssr VARCHAR,
                callsign VARCHAR,
                matricula VARCHAR,
                tipo_aeronave VARCHAR,
                empresa VARCHAR,
                numero_vuelo BIGINT,
                tipo_vuelo VARCHAR,
                tiempo_inicial TIMESTAMP,
                origen VARCHAR,
                fecha_salida DATE,
                hora_salida TIME,
                hora_pv TIME,
                destino VARCHAR,
                fecha_llegada DATE,
                hora_llegada TIME,
                nivel BIGINT,
                duracion BIGINT,
                distancia BIGINT,
                velocidad BIGINT,
                eq_ssr VARCHAR,
                nombre_origen VARCHAR,
                nombre_destino VARCHAR,
                fecha_registro DATE
            )
        """)
        
        # Schema Correction/Migration: Ensure sid is VARCHAR
        try:
            # Check current schema
            columns = conn.execute("DESCRIBE flights").fetchall()
            logger.info(f"Current flights schema: {columns}")
            for col in columns:
                name = col[0].lower()
                type_ = str(col[1]).upper()
                logger.info(f"Checking column {name} of type {type_}")
                if name == 'sid' and type_ not in ['VARCHAR', 'STRING']:
                    logger.info(f"Detected sid column as {type_}. Migrating to VARCHAR.")
                    conn.execute("ALTER TABLE flights ALTER COLUMN sid TYPE VARCHAR")
                    logger.info("Migration command executed.")
        except Exception as e:
            logger.warning(f"Schema migration check failed: {e}")

        except Exception as e:
            logger.warning(f"Schema migration check failed: {e}")

        # Schema Correction: Ensure file_id exists
        try:
            # Re-fetch columns to check for file_id
            columns = conn.execute("DESCRIBE flights").fetchall()
            col_names = [col[0].lower() for col in columns]
            if 'file_id' not in col_names:
                logger.info("Adding file_id column to flights table.")
                conn.execute("ALTER TABLE flights ADD COLUMN file_id BIGINT")
                
                # Update existing records to link to a dummy or keep null?
                # For now keep null.
                
                # Try adding FK. Note: Adding FK to existing table in DuckDB is limited/syntax specific.
                # Just column for now to enable insertion. 
        except Exception as e:
             logger.warning(f"file_id migration check failed: {e}")

        

    @staticmethod
    def _clean_int(val):
        """Clean integer strings with commas."""
        if val is None: return None
        s = str(val).replace(',', '').split('.')[0]
        try:
            return int(s)
        except:
            return None

    def execute(self, force_reload: bool = False, specific_file: str = None) -> dict:
        start_time = time.time()
        
        if specific_file:
            files = [specific_file]
        else:
            files_xlsx = glob.glob(os.path.join(self.data_dir, "*.xlsx"))
            files_csv = glob.glob(os.path.join(self.data_dir, "*.csv"))
            files = files_xlsx + files_csv
        
        if not files:
            return {"status": "error", "message": "No data files found."}

        self.total_files = len(files)
        self.processed_count = 0
        
        conn = duckdb.connect(self.db_path)
        
        if force_reload and not specific_file:
            self.reset_database(conn)
            
        self._init_db(conn)
        
        processed_files = 0
        total_inserted = 0
        
        try:
            for i, file_path in enumerate(files):
                file_name = os.path.basename(file_path)
                self.current_file = file_name
                
                if not force_reload:
                    status_row = conn.execute("SELECT status FROM file_processing_control WHERE file_name = ?", [file_name]).fetchone()
                    if status_row and status_row[0] == 'COMPLETED':
                        logger.info(f"Skipping {file_name} (already processed)")
                        self.processed_count += 1
                        continue
                
                logger.info(f"Processing ({i+1}/{len(files)}): {file_name}")
                
                # Update status to PROCESSING and get ID
                conn.execute("DELETE FROM file_processing_control WHERE file_name = ?", [file_name])
                
                # Fetch sequence manually or use RETURNING
                tracking_id = conn.execute("INSERT INTO file_processing_control (file_name, processed_at, status) VALUES (?, CURRENT_TIMESTAMP, 'PROCESSING') RETURNING id", [file_name]).fetchone()[0]
                
                try:
                    # Read
                    if file_path.endswith('.xlsx'):
                        pdf = pd.read_excel(file_path, dtype=str, engine='openpyxl')
                        df = pl.from_pandas(pdf)
                    else:
                        df = pl.read_csv(file_path, ignore_errors=True, infer_schema_length=0)

                    if df.height == 0:
                        logger.warning(f"File {file_name} is empty.")
                        conn.execute("UPDATE file_processing_control SET status = 'SKIPPED', error_message = 'Empty file' WHERE file_name = ?", [file_name])
                        self.processed_count += 1
                        continue

                    # 1. Rename Columns
                    rename_map = {}
                    for col in df.columns:
                        if col in self.column_mapping:
                            rename_map[col] = self.column_mapping[col]
                    df = df.rename(rename_map)

                    # 1b. Add file_id
                    df = df.with_columns(pl.lit(tracking_id).alias('file_id'))

                    # 1c. Enforce types for critical columns immediately
                    if 'sid' in df.columns:
                        df = df.with_columns(pl.col('sid').cast(pl.Utf8))

                    # 2. Add Missing Columns
                    existing = set(df.columns)
                    missing = [c for c in self.target_columns if c not in existing]
                    if missing:
                        df = df.with_columns([pl.lit(None).alias(c) for c in missing])
                    
                    # 3. Robust Transformation using DateParser
                    # Dates
                    date_cols = ['fecha', 'fecha_salida', 'fecha_llegada', 'fecha_registro']
                    for col in date_cols:
                        if col in df.columns:
                            df = df.with_columns(
                                pl.col(col).map_elements(DateParser.parse_date, return_dtype=pl.Date, skip_nulls=True).alias(col)
                            )
                    
                    # Times
                    for col in ['hora_salida', 'hora_pv', 'hora_llegada']:
                         if col in df.columns:
                            df = df.with_columns(
                                pl.col(col).map_elements(DateParser.parse_time, return_dtype=pl.Time, skip_nulls=True).alias(col)
                            )

                    if 'tiempo_inicial' in df.columns:
                         df = df.with_columns(
                            pl.col('tiempo_inicial').cast(pl.String).str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S", strict=False)
                         )

                    # INT Columns
                    int_cols = ['numero_vuelo', 'nivel', 'duracion', 'distancia', 'velocidad'] 
                    
                    if 'id' in df.columns:
                         df = df.with_columns(
                            pl.col('id').map_elements(self._clean_int, return_dtype=pl.Int64, skip_nulls=True).alias('id')
                        )

                    for col in int_cols:
                        if col in df.columns:
                             df = df.with_columns(
                                pl.col(col).map_elements(self._clean_int, return_dtype=pl.Int64, skip_nulls=True).alias(col)
                            )

                    # 4. Final Select
                    df = df.select(self.target_columns)
                    
                    # 5. Insert
                    conn.register('temp_view', df)
                    conn.execute(f"INSERT INTO flights ({', '.join(self.target_columns)}) SELECT * FROM temp_view")
                    conn.unregister('temp_view')
                    
                    rows = len(df)
                    total_inserted += rows
                    processed_files += 1
                    
                    conn.execute("""
                        UPDATE file_processing_control 
                        SET status = 'COMPLETED', row_count = ?, error_message = NULL 
                        WHERE file_name = ?
                    """, [rows, file_name])
                    
                    del df

                except Exception as file_error:
                    error_msg = str(file_error)
                    logger.error(f"Error processing {file_name}: {error_msg}")
                    import traceback
                    logger.error(traceback.format_exc())
                    conn.execute("UPDATE file_processing_control SET status = 'ERROR', error_message = ? WHERE file_name = ?", [error_msg, file_name])
                
                self.processed_count += 1
                self.current_file = None
            
            return {
                "status": "success", 
                "message": f"Processed {processed_files} files.", 
                "rows_inserted": total_inserted,
                "duration_seconds": time.time() - start_time
            }
            
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {"status": "error", "message": str(e)}
        finally:
            conn.close()

    def reset_database(self, conn=None):
        """Drop and recreate tables."""
        should_close = False
        if conn is None:
            conn = duckdb.connect(self.db_path)
            should_close = True
            
        try:
            logger.info("Dropping tables for reset...")
            conn.execute("DROP TABLE IF EXISTS flights")
            conn.execute("DROP TABLE IF EXISTS file_processing_control")
            conn.execute("DROP SEQUENCE IF EXISTS tracking_id_seq")
            
            # Re-init immediately
            self._init_db(conn)
            logger.info("Tables recreated.")
            return True
        except Exception as e:
            logger.error(f"Error resetting database: {e}")
            raise e
        finally:
            if should_close:
                conn.close()


    def get_progress(self):
        """Returns current processing status."""
        return {
            "current_file": self.current_file,
            "status": "running" if self.current_file else "idle",
            "progress": f"{self.processed_count}/{self.total_files}" if self.total_files > 0 else "0/0"
        }

    def get_history(self):
        """Returns processing history."""
        conn = duckdb.connect(self.db_path)
        try:
             # Ensure table exists first just in case
             self._init_db(conn)
             result = conn.execute("SELECT * FROM file_processing_control ORDER BY processed_at DESC LIMIT 50").fetchall()
             columns = ["id", "file_name", "processed_at", "status", "row_count", "error_message"]
             return [dict(zip(columns, row)) for row in result]
        except Exception as e:
            logger.error(f"Error fetching history: {e}")
            return []
        finally:
            conn.close()


    def delete_file(self, filename: str) -> bool:
        """
        Delete a file record, its associated flight data, and the physical file.
        
        Args:
            filename: The name of the file to delete.
            
        Returns:
            bool: True if deleted (or not found but handled), False if critical error.
        """
        conn = duckdb.connect(self.db_path)
        try:
            # 1. Get File ID
            row = conn.execute("SELECT id FROM file_processing_control WHERE file_name = ?", [filename]).fetchone()
            
            if row:
                file_id = row[0]
                logger.info(f"Deleting flights for file {filename} (ID: {file_id})...")
                conn.execute("DELETE FROM flights WHERE file_id = ?", [file_id])
                
                logger.info(f"Deleting file record {filename}...")
                conn.execute("DELETE FROM file_processing_control WHERE id = ?", [file_id])
            else:
                logger.warning(f"File {filename} not found in database. Proceeding to checking physical file.")

            # 2. Delete Physical File
            file_path = os.path.join(self.data_dir, filename)
            if os.path.exists(file_path):
                logger.info(f"Deleting physical file {file_path}...")
                os.remove(file_path)
            else:
                logger.warning(f"Physical file {file_path} not found.")

            return True
        except Exception as e:
            logger.error(f"Error deleting file {filename}: {e}")
            raise e
        finally:
            conn.close()
