import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

def conectar_bd():
    engine = create_engine('postgresql://postgres:Iforero2011.@localhost:5432/flights')
    query = "SELECT * FROM public.fligths"
    return pd.read_sql(query, engine)


def procesar_fechas(df):
    # Procesar hora_salida (time object)
    if 'hora_salida' in df.columns:
        df['hora'] = df['hora_salida'].apply(lambda x: x.hour if x else None)
    elif 'tiempo_inicial' in df.columns:
        df['hora'] = pd.to_datetime(df['tiempo_inicial']).dt.hour
    
    # Convertir fecha_salida a datetime si existe, sino usar fecha
    fecha_base = 'fecha_salida' if 'fecha_salida' in df.columns else 'fecha'
    df['dia_semana'] = pd.to_datetime(df[fecha_base]).dt.day_name()
    df['mes'] = pd.to_datetime(df[fecha_base]).dt.month
    
    # Procesar hora_pv (ya es time object)
    if 'hora_pv' in df.columns:
        df['hora_pv_num'] = df['hora_pv'].apply(lambda x: x.hour if x else None)
    
    # Procesar fecha y hora de llegada
    if 'fecha_llegada' in df.columns and 'hora_llegada' in df.columns:
        df['hora_llegada_num'] = df['hora_llegada'].apply(lambda x: x.hour if x else None)
    
    # Verificar datos procesados
    print("\nColumnas de tiempo procesadas:")
    print(df[['hora', 'dia_semana', 'mes']].dtypes)
    
    return df

def analizar_horas_pico(df):
    plt.figure(figsize=(15, 6))
    # Usar tiempo_inicial para el análisis de horas si existe
    hora_analisis = 'tiempo_inicial' if 'tiempo_inicial' in df.columns else 'hora'
    sns.histplot(data=df, x=pd.to_datetime(df[hora_analisis]).dt.hour, bins=24)
    plt.title('Distribución de Vuelos por Hora')
    plt.xlabel('Hora del Día')
    plt.ylabel('Número de Vuelos')
    plt.savefig('resultados/distribucion_horas.png')
    plt.close()


def analizar_dias_semana(df):
    plt.figure(figsize=(12, 6))
    orden_dias = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    sns.countplot(data=df, x='dia_semana', order=orden_dias)
    plt.xticks(rotation=45)
    plt.title('Distribución de Vuelos por Día de la Semana')
    plt.xlabel('Día')
    plt.ylabel('Número de Vuelos')
    plt.savefig('resultados/distribucion_dias.png')
    plt.close()

def crear_heatmap(df):
    pivot_table = pd.crosstab(df['hora'], df['dia_semana'])
    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot_table, cmap='YlOrRd', annot=True, fmt='d')
    plt.title('Heatmap de Vuelos por Hora y Día')
    plt.xlabel('Día de la Semana')
    plt.ylabel('Hora del Día')
    plt.savefig('resultados/heatmap_actividad.png')
    plt.close()

def main():
    # Crear directorio para resultados
    import os
    if not os.path.exists('resultados'):
        os.makedirs('resultados')

    # Cargar y procesar datos
    df = conectar_bd()
    df = procesar_fechas(df)

    # Mostrar información básica
    print("Información del Dataset:")
    print(df.info())
    print("\nPrimeras filas:")
    print(df.head())

    # Generar visualizaciones
    analizar_horas_pico(df)
    analizar_dias_semana(df)
    crear_heatmap(df)

if __name__ == "__main__":
    main()