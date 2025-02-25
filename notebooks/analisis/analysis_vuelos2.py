import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import calendar

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
    fecha_dt = pd.to_datetime(df[fecha_base])
    
    df['dia_semana'] = fecha_dt.dt.day_name()
    df['mes'] = fecha_dt.dt.month
    df['mes_nombre'] = fecha_dt.dt.month_name()
    df['dia'] = fecha_dt.dt.day
    df['año'] = fecha_dt.dt.year
    
    return df

def analizar_distribucion_mensual(df):
    plt.figure(figsize=(15, 6))
    monthly_counts = df.groupby('mes_nombre')['mes'].count()
    # Reordenar los meses
    month_order = list(calendar.month_name)[1:]
    monthly_counts = monthly_counts.reindex(month_order)
    
    sns.barplot(x=monthly_counts.index, y=monthly_counts.values)
    plt.title('Distribución de Vuelos por Mes')
    plt.xlabel('Mes')
    plt.ylabel('Número de Vuelos')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('resultados/distribucion_mensual.png')
    plt.close()

def crear_heatmap_mes_dia(df):
    plt.figure(figsize=(15, 8))
    pivot_table = pd.crosstab(df['mes_nombre'], df['dia_semana'])
    # Reordenar los meses y días
    month_order = list(calendar.month_name)[1:]
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot_table = pivot_table.reindex(month_order)
    pivot_table = pivot_table[day_order]
    
    # Changed fmt from 'd' to '.0f' to handle float values
    sns.heatmap(pivot_table, cmap='YlOrRd', annot=True, fmt='.0f')
    plt.title('Heatmap de Vuelos por Mes y Día de la Semana')
    plt.xlabel('Día de la Semana')
    plt.ylabel('Mes')
    plt.tight_layout()
    plt.savefig('resultados/heatmap_mes_dia.png')
    plt.close()

def analizar_patron_diario_por_mes(df):
    for mes in df['mes_nombre'].unique():
        plt.figure(figsize=(12, 6))
        df_mes = df[df['mes_nombre'] == mes]
        
        sns.countplot(data=df_mes, x='dia_semana', 
                     order=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
        plt.title(f'Distribución de Vuelos por Día de la Semana - {mes}')
        plt.xlabel('Día de la Semana')
        plt.ylabel('Número de Vuelos')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'resultados/distribucion_dias_{mes}.png')
        plt.close()

def analizar_tendencia_anual(df):
    plt.figure(figsize=(15, 6))
    yearly_monthly = df.groupby(['año', 'mes_nombre'])['mes'].count().reset_index(name='count')
    
    for year in yearly_monthly['año'].unique():
        year_data = yearly_monthly[yearly_monthly['año'] == year]
        plt.plot(year_data['mes_nombre'], year_data['count'], marker='o', label=str(year))
    
    plt.title('Tendencia de Vuelos por Mes y Año')
    plt.xlabel('Mes')
    plt.ylabel('Número de Vuelos')
    plt.xticks(rotation=45)
    plt.legend(title='Año')
    plt.tight_layout()
    plt.savefig('resultados/tendencia_anual.png')
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
    print("\nResumen estadístico por mes:")
    monthly_stats = df.groupby('mes_nombre').size()
    print(monthly_stats)

    # Generar visualizaciones
    analizar_distribucion_mensual(df)
    crear_heatmap_mes_dia(df)
    analizar_patron_diario_por_mes(df)
    analizar_tendencia_anual(df)

if __name__ == "__main__":
    main()