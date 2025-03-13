import pandas as pd
import requests
from sqlalchemy import create_engine, text
import numpy as np

def create_airport_table(engine):
    # Create airports table if it doesn't exist
    create_table_query = """
    CREATE TABLE IF NOT EXISTS airports (
        id SERIAL PRIMARY KEY,
        icao_code VARCHAR(4),
        iata_code VARCHAR(3),
        name VARCHAR(100),
        city VARCHAR(100),
        country VARCHAR(100),
        latitude FLOAT,
        longitude FLOAT,
        altitude FLOAT,
        timezone FLOAT,
        dst CHAR(1),
        type VARCHAR(50),
        source VARCHAR(50)
    )
    """
    with engine.connect() as conn:
        conn.execute(text(create_table_query))
        conn.commit()

def get_openflights_data():
    # OpenFlights airport data URL
    url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
    
    # Column names for the OpenFlights data
    columns = ['id', 'name', 'city', 'country', 'iata_code', 'icao_code',
               'latitude', 'longitude', 'altitude', 'timezone', 'dst', 'tz_database_time_zone', 'type', 'source']
    
    # Read the data
    df = pd.read_csv(url, names=columns)
    
    # Clean the data
    df = df[df['icao_code'].notna()]  # Keep only records with ICAO codes
    df['icao_code'] = df['icao_code'].str.strip()
    
    return df

def main():
    # Database connection
    engine = create_engine('postgresql://postgres:Iforero2011.@localhost:5432/flights')
    
    # Create the table
    create_airport_table(engine)
    
    # Get OpenFlights data
    airports_df = get_openflights_data()
    
    # Filter columns we want to save
    columns_to_save = ['icao_code', 'iata_code', 'name', 'city', 'country', 
                      'latitude', 'longitude', 'altitude', 'timezone', 'dst', 
                      'type', 'source']
    
    airports_df = airports_df[columns_to_save]
    
    # Save to PostgreSQL
    airports_df.to_sql('airports', engine, if_exists='replace', index=False)
    
    print(f"Successfully loaded {len(airports_df)} airports to database")
    
    # Create an index on ICAO code for better performance
    with engine.connect() as conn:
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_airports_icao ON airports(icao_code)"))
        conn.commit()

if __name__ == "__main__":
    main()



def test_airport_data():
    engine = create_engine('postgresql://postgres:Iforero2011.@localhost:5432/flights')
    query = """
    SELECT DISTINCT a.*
    FROM airports a
    JOIN fligths f ON f.origen = a.icao_code OR f.destino = a.icao_code
    ORDER BY a.icao_code
    """
    all_airports = pd.read_sql(query, engine)
    print("All airports in flight data:")
    print(all_airports[['icao_code', 'name', 'city', 'country', 'latitude', 'longitude']])

test_airport_data()