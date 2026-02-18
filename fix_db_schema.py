import duckdb
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "data/metrics.duckdb"

def fix_schema():
    logger.info(f"Connecting to database at {DB_PATH}")
    conn = duckdb.connect(DB_PATH)
    
    try:
        # Check current schema
        columns = conn.execute("DESCRIBE flights").fetchall()
        logger.info("Current Schema:")
        for col in columns:
            logger.info(f" - {col[0]}: {col[1]}")
            
        # Fix SID
        conn.execute("ALTER TABLE flights ALTER COLUMN sid TYPE VARCHAR")
        logger.info("Successfully altered 'sid' column to VARCHAR.")
        
        # Verify
        columns_after = conn.execute("DESCRIBE flights").fetchall()
        for col in columns_after:
             if col[0] == 'sid':
                 logger.info(f"New 'sid' type: {col[1]}")
                 
    except Exception as e:
        logger.error(f"Error updating schema: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_schema()
