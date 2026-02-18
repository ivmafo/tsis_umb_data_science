import duckdb
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("DataCheck")

# DB Path from settings (hardcoded for checking)
DB_PATH = "data/metrics.duckdb"

def check_data():
    if not os.path.exists(DB_PATH):
        logger.error(f"Database file not found at {DB_PATH}")
        return

    logger.info(f"Connecting to {DB_PATH}...")
    try:
        # Try read_only first to avoid lock contention if possible
        conn = duckdb.connect(DB_PATH, read_only=True)
        
        # Count total rows
        count = conn.execute("SELECT COUNT(*) FROM flights").fetchone()[0]
        logger.info(f"\nTotal rows in 'flights' table: {count}")
        
        if count > 0:
            # Show last 5 rows
            logger.info("\nLast 5 inserted rows (ID, SID, Fecha, Callsign):")
            rows = conn.execute("SELECT id, sid, fecha, callsign FROM flights ORDER BY id DESC LIMIT 5").fetchall()
            for row in rows:
                logger.info(row)
                
            # Check for specific previously failing strings if meaningful
            logger.info("\nChecking sample SIDs:")
            sids = conn.execute("SELECT DISTINCT sid FROM flights LIMIT 5").fetchall()
            logger.info([s[0] for s in sids])

    except Exception as e:
        logger.error(f"Error reading database: {e}")
        logger.info("Hint: If the server is running, you might need to stop it to release the file lock if not using WAL mode or if writes are happening.")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_data()
