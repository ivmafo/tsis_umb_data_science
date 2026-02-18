import duckdb
try:
    conn = duckdb.connect('data/metrics.duckdb', read_only=True)
    cols = conn.execute("PRAGMA table_info('flights')").fetchall()
    print([c[1] for c in cols])
except Exception as e:
    print(e)
finally:
    conn.close()
