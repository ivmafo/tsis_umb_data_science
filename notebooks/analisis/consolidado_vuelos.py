import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

def conectar_bd():
    """Conexión a la base de datos"""
    return create_engine('postgresql://postgres:Iforero2011.@localhost:5432/flights')

def obtener_consolidados(aeropuerto):
    """Obtiene consolidados principales de la tabla flights"""
    engine = conectar_bd()
    
    # Consulta SQL para obtener consolidados
    query = """
    SELECT 
        -- Consolidado general
        COUNT(*) as total_vuelos,
        COUNT(DISTINCT origen) as total_aeropuertos_origen,
        COUNT(DISTINCT destino) as total_aeropuertos_destino,
        
        -- Distribución por tipo de operación para el aeropuerto específico
        SUM(CASE WHEN destino = %(aeropuerto)s THEN 1 ELSE 0 END) as total_aterrizajes,
        SUM(CASE WHEN origen = %(aeropuerto)s THEN 1 ELSE 0 END) as total_despegues,
        
        -- Distribución por tipo de vuelo
        SUM(CASE WHEN tipo_vuelo = 'G' THEN 1 ELSE 0 END) as vuelos_general,
        SUM(CASE WHEN tipo_vuelo = 'M' THEN 1 ELSE 0 END) as vuelos_militar,
        SUM(CASE WHEN tipo_vuelo = 'N' THEN 1 ELSE 0 END) as vuelos_nacional,
        SUM(CASE WHEN tipo_vuelo = 'S' THEN 1 ELSE 0 END) as vuelos_servicio,
        SUM(CASE WHEN tipo_vuelo = 'X' THEN 1 ELSE 0 END) as vuelos_extranjero,
        
        -- Estadísticas temporales
        MIN(fecha) as primera_fecha,
        MAX(fecha) as ultima_fecha
    FROM public.fligths
    WHERE origen = %(aeropuerto)s OR destino = %(aeropuerto)s;
    """
    
    return pd.read_sql_query(query, engine, params={'aeropuerto': aeropuerto})

def imprimir_reporte(datos, aeropuerto):
    print(f"\n=== CONSOLIDADO DE OPERACIONES AÉREAS - {aeropuerto} ===")
    print("\nESTADÍSTICAS GENERALES:")
    print(f"Total de operaciones: {datos['total_vuelos'].iloc[0]:,}")
    print(f"Período: {datos['primera_fecha'].iloc[0]} a {datos['ultima_fecha'].iloc[0]}")
    
    print("\nDISTRIBUCIÓN POR TIPO DE OPERACIÓN:")
    total_vuelos = datos['total_vuelos'].iloc[0]
    aterrizajes = datos['total_aterrizajes'].iloc[0]
    despegues = datos['total_despegues'].iloc[0]
    
    print(f"Aterrizajes: {aterrizajes:,} ({(aterrizajes/total_vuelos)*100:.1f}%)")
    print(f"Despegues: {despegues:,} ({(despegues/total_vuelos)*100:.1f}%)")
    
    print("\nDISTRIBUCIÓN POR TIPO DE VUELO:")
    print("G = Aviación General")
    print("M = Vuelos Militares")
    print("N = Vuelos Nacionales")
    print("S = Vuelos de Servicio")
    print("X = Vuelos Extranjeros")
    
    tipos = {
        'General (G)': 'vuelos_general',
        'Militar (M)': 'vuelos_militar',
        'Nacional (N)': 'vuelos_nacional',
        'Servicio (S)': 'vuelos_servicio',
        'Extranjero (X)': 'vuelos_extranjero'
    }
    
    for tipo, campo in tipos.items():
        valor = datos[campo].iloc[0]
        porcentaje = (valor/total_vuelos*100) if total_vuelos > 0 else 0
        print(f"{tipo}: {valor:,} ({porcentaje:.1f}%)")
    
    print(f"Aeropuertos origen: {datos['total_aeropuertos_origen'].iloc[0]}")
    print(f"Aeropuertos destino: {datos['total_aeropuertos_destino'].iloc[0]}")
    
    print("\nDISTRIBUCIÓN POR CATEGORÍA DE AERONAVE:")
    print(f"Ligeras: {datos['vuelos_ligeros']:,} ({datos['vuelos_ligeros']/datos['total_vuelos']*100:.1f}%)")
    print(f"Medias: {datos['vuelos_medios']:,} ({datos['vuelos_medios']/datos['total_vuelos']*100:.1f}%)")
    print(f"Pesadas: {datos['vuelos_pesados']:,} ({datos['vuelos_pesados']/datos['total_vuelos']*100:.1f}%)")

if __name__ == "__main__":
    try:
        # Definir el aeropuerto para el análisis
        aeropuerto = 'SKRG'  # Ejemplo: Aeropuerto José María Córdova
        
        # Generar reporte
        consolidados = obtener_consolidados(aeropuerto)
        imprimir_reporte(consolidados, aeropuerto)
        
    except Exception as e:
        print(f"Error al procesar los datos: {str(e)}")