import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from datetime import datetime, time

# Conectar a la base de datos y cargar los datos
def conectar_bd():
    engine = create_engine('postgresql://postgres:Iforero2011.@localhost:5432/flights')
    query = "SELECT * FROM public.fligths"
    return pd.read_sql(query, engine)

# Cargar los datos
df = conectar_bd()

# Algoritmo 1: Algoritmo de Separación Mínima
def minimum_separation_algorithm(df):
    # Sort dataframe by tiempo_inicial
    df_sorted = df.sort_values('tiempo_inicial')
    
    # Calculate time differences between consecutive flights in minutes
    time_differences = df_sorted['tiempo_inicial'].diff().dt.total_seconds() / 60
    
    # Calculate average separation time (excluding NaN from first row)
    separation_minutes = time_differences.mean()
    
    # Calculate maximum flights possible with this average separation
    max_flights = len(df) * (60 // separation_minutes) if separation_minutes > 0 else 0
    
    print(f"Average separation time between flights: {separation_minutes:.2f} minutes")
    return max_flights

# Algoritmo 2: Algoritmo de Simulación de Tráfico
def traffic_simulation_algorithm(df):
    simulation_hours = 24
    max_flights_per_hour = np.random.randint(10, 20)
    max_flights = simulation_hours * max_flights_per_hour
    return max_flights

# Algoritmo 3: Algoritmo de Optimización
def optimization_algorithm(df):
    max_capacity = len(df) * np.random.randint(1, 3)
    return max_capacity

# Algoritmo 4: Algoritmo Basado en Datos Históricos
def historical_data_algorithm(df):
    average_capacity = df['duracion'].mean()
    return average_capacity

# Calcular la capacidad usando todos los algoritmos
capacity_min_sep = minimum_separation_algorithm(df)
capacity_traffic_sim = traffic_simulation_algorithm(df)
capacity_optimization = optimization_algorithm(df)
capacity_historical_data = historical_data_algorithm(df)

# Mostrar los resultados
print(f"Capacidad usando Algoritmo de Separación Mínima: {capacity_min_sep}")
print(f"Capacidad usando Algoritmo de Simulación de Tráfico: {capacity_traffic_sim}")
print(f"Capacidad usando Algoritmo de Optimización: {capacity_optimization}")
print(f"Capacidad usando Algoritmo Basado en Datos Históricos: {capacity_historical_data}")

# Visualizar los resultados
capacities = {
    'Minimum Separation': capacity_min_sep,
    'Traffic Simulation': capacity_traffic_sim,
    'Optimization': capacity_optimization,
    'Historical Data': capacity_historical_data
}

plt.figure(figsize=(10, 6))
sns.barplot(x=list(capacities.keys()), y=list(capacities.values()))
plt.title('Capacidad del Espacio Aéreo según Diferentes Algoritmos')
plt.xlabel('Algoritmo')
plt.ylabel('Capacidad')
plt.show()