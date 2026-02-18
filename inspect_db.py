import duckdb
import os

db_path = 'data/metrics.duckdb'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

con = duckdb.connect(db_path)

print("Columns:")
try:
    result = con.execute("SELECT * FROM flights LIMIT 1;")
    print([desc[0] for desc in result.description])
except Exception as e:
    print(f"Error getting columns: {e}")

print("\nTesting strftime query:")
try:
    query = "SELECT strftime(fecha, '%Y/%m') as name, COUNT(*) as value FROM flights GROUP BY name ORDER BY name LIMIT 5"
    result = con.execute(query).fetchall()
    for row in result:
        print(row)
except Exception as e:
    print(f"Error executing Test Query: {e}")

