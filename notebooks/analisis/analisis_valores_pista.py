import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import concurrent.futures

class AnalisisValoresPista:
    def __init__(self):
        self.engine = self.conectar_bd()
        self.tiempos_ocupacion = {
            'aterrizaje': {
                'ligera': 60,  # segundos
                'media': 75,
                'pesada': 90
            },
            'despegue': {
                'ligera': 45,
                'media': 60,
                'pesada': 75
            }
        }
    def conectar_bd(self):
        """
        Establece conexión con la base de datos PostgreSQL
        """
        return create_engine('postgresql://postgres:Iforero2011.@localhost:5432/flights')
    def obtener_datos_operaciones(self, fecha_inicio, fecha_fin, aeropuerto):
        """Consulta optimizada con precálculo de categorías y tiempos"""
        query = """
            WITH vuelos_aeropuerto AS (
                SELECT 
                    fecha,
                    tipo_vuelo,
                    tipo_aeronave,
                    CASE 
                        WHEN tipo_vuelo IN ('G') THEN 'ligera'
                        WHEN tipo_vuelo IN ('X') THEN 'pesada'
                        ELSE 'media'
                    END as categoria,
                    CASE
                        WHEN tipo_vuelo = 'A' THEN
                            CASE 
                                WHEN tipo_vuelo IN ('G') THEN 60
                                WHEN tipo_vuelo IN ('X') THEN 90
                                ELSE 75
                            END
                        ELSE
                            CASE 
                                WHEN tipo_vuelo IN ('G') THEN 45
                                WHEN tipo_vuelo IN ('X') THEN 75
                                ELSE 60
                            END
                    END as tiempo_ocupacion
                FROM public.fligths
                WHERE fecha BETWEEN %(fecha_inicio)s AND %(fecha_fin)s
                    AND (origen = %(aeropuerto)s OR destino = %(aeropuerto)s)
            )
            SELECT 
                fecha,
                tipo_vuelo,
                tipo_aeronave,
                categoria,
                tiempo_ocupacion,
                EXTRACT(HOUR FROM fecha) as hora
            FROM vuelos_aeropuerto
        """
        return pd.read_sql_query(query, self.engine, params={
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'aeropuerto': aeropuerto
        })

    def calcular_capacidad_pista_detallada(self, df):
        """Cálculo optimizado de capacidad"""
        if len(df) == 0:
            return {
                'capacidad_hora': 0,
                'mix_operaciones': pd.Series(),
                'tiempo_promedio': 0,
                'separacion_promedio': 0
            }
        
        # Cálculos vectorizados para mix de operaciones
        mix_operaciones = df.groupby(['tipo_vuelo', 'categoria']).size()
        total_operaciones = len(df)
        proporciones = mix_operaciones / total_operaciones
        
        # Tiempo promedio vectorizado
        tiempo_promedio = df['tiempo_ocupacion'].mean()
        
        # Matriz de separación usando numpy
        categorias = ['ligera', 'media', 'pesada']
        matriz_sep = np.array([
            [3, 3, 3],  # ligera -> [ligera, media, pesada]
            [3, 3, 5],  # media  -> [ligera, media, pesada]
            [6, 5, 4]   # pesada -> [ligera, media, pesada]
        ])
        
        # Calcular proporciones por categoría
        prop_cat = df['categoria'].map({
            'ligera': 0,
            'media': 1,
            'pesada': 2
        }).value_counts(normalize=True).reindex([0,1,2], fill_value=0)
        
        # Calcular separación promedio vectorizada
        separacion_promedio = (matriz_sep * np.outer(prop_cat, prop_cat)).sum()
        
        # Capacidad teórica
        max_valor = max(tiempo_promedio, separacion_promedio)
        capacidad_hora = 3600 / max_valor if max_valor > 0 else 0
        
        return {
            'capacidad_hora': capacidad_hora,
            'mix_operaciones': proporciones,
            'tiempo_promedio': tiempo_promedio,
            'separacion_promedio': separacion_promedio
        }

    def generar_reporte_completo(self, fecha_inicio, fecha_fin, aeropuerto):
        """Reporte optimizado"""
        df = self.obtener_datos_operaciones(fecha_inicio, fecha_fin, aeropuerto)
        
        if len(df) == 0:
            return self._generar_reporte_vacio(aeropuerto)
        
        # Cálculos en paralelo usando concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_capacidad = executor.submit(self.calcular_capacidad_pista_detallada, df)
            future_tiempos = executor.submit(self.calcular_tiempos_ocupacion, df)
            future_distribucion = executor.submit(self.analizar_distribucion_horaria, df)
            
            capacidad_detallada = future_capacidad.result()
            tiempos = future_tiempos.result()
            distribucion = future_distribucion.result()
        
        return {
            'tiempos': tiempos,
            'distribucion': distribucion,
            'capacidad_detallada': capacidad_detallada
        }
    def calcular_TPS(self, tiempo_conflicto, tiempo_coordinacion):
        """
        Calcula el Tiempo Promedio de Sector (TPS)
        """
        return tiempo_conflicto + tiempo_coordinacion
    def calcular_TFC(self, tiempo_comunicacion, numero_comunicaciones):
        """
        Calcula el Tiempo de Fase de Conflicto (TFC)
        """
        return tiempo_comunicacion * numero_comunicaciones
    def calcular_SCV(self, velocidad_crucero, distancia_sector):
        """
        Calcula el Tiempo de Sobrevuelo (SCV)
        """
        return (distancia_sector / velocidad_crucero) * 3600  # convertir a segundos
    def calcular_capacidad_horaria(self, TPS, factor_ocupacion=0.8):
        """
        Calcula la Capacidad Horaria (CH)
        CH = (3600/TPS) * factor_ocupacion
        """
        return (3600/TPS) * factor_ocupacion
    def calcular_numero_referencia_capacidad(self, TPS, SCV):
        """
        Calcula el Número de Referencia de la Capacidad de Sector (N)
        N = SCV/TPS
        """
        return SCV/TPS
    def analisis_capacidad_sector(self, datos_sector):
        """
        Realiza análisis completo de capacidad de sector
        """
        # Cálculos básicos
        tps = self.calcular_TPS(
            datos_sector['tiempo_conflicto'],
            datos_sector['tiempo_coordinacion']
        )
        
        tfc = self.calcular_TFC(
            datos_sector['tiempo_comunicacion'],
            datos_sector['numero_comunicaciones']
        )
        
        scv = self.calcular_SCV(
            datos_sector['velocidad_crucero'],
            datos_sector['distancia_sector']
        )
        
        # Cálculos derivados
        capacidad_horaria = self.calcular_capacidad_horaria(tps)
        numero_referencia = self.calcular_numero_referencia_capacidad(tps, scv)
        
        return {
            'TPS': tps,
            'TFC': tfc,
            'SCV': scv,
            'capacidad_horaria': capacidad_horaria,
            'numero_referencia': numero_referencia
        }
    def _generar_reporte_vacio(self, aeropuerto):
        """Genera un reporte vacío cuando no hay datos"""
        return {
            'tiempos': pd.DataFrame(),
            'distribucion': pd.Series(),
            'capacidad_detallada': {
                'capacidad_hora': 0,
                'mix_operaciones': pd.Series(),
                'tiempo_promedio': 0,
                'separacion_promedio': 0
            }
        }

    def calcular_tiempos_ocupacion(self, df):
        """Calcula tiempos de ocupación optimizado"""
        if len(df) == 0:
            return pd.DataFrame()
            
        return df.groupby(['tipo_vuelo', 'tipo_aeronave']).agg({
            'tiempo_ocupacion': ['count', 'mean']
        }).reset_index()

    def analizar_distribucion_horaria(self, df):
        """Analiza la distribución horaria optimizada"""
        if len(df) == 0:
            return pd.Series()
            
        return df.groupby('hora').size()

    def _generar_graficos(self, tiempos, distribucion):
        """Genera gráficos del reporte"""
        if len(tiempos) == 0 or len(distribucion) == 0:
            return
            
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Gráfico de tiempos por tipo de operación
        if not tiempos.empty:
            tiempos.plot(kind='bar', ax=ax1)
            ax1.set_title('Tiempos de Ocupación por Tipo de Operación')
            ax1.set_xlabel('Tipo de Operación')
            ax1.set_ylabel('Cantidad de Operaciones')
        
        # Gráfico de distribución horaria
        if not distribucion.empty:
            distribucion.plot(kind='line', ax=ax2)
            ax2.set_title('Distribución Horaria de Operaciones')
            ax2.set_xlabel('Hora del Día')
            ax2.set_ylabel('Número de Operaciones')
        
        plt.tight_layout()
        plt.show()
# Código principal de ejecución
if __name__ == "__main__":
    try:
        # Crear instancia del analizador
        analisis = AnalisisValoresPista()
        
        # Parámetros de análisis
        fecha_inicio = '2000-01-01'
        fecha_fin = '2024-01-07'  # Una semana de análisis
        aeropuerto = 'SKRG'
        
        # Generar reporte
        resultados = analisis.generar_reporte_completo(fecha_inicio, fecha_fin, aeropuerto)
        
        # Imprimir resultados detallados
        print("\n====================================================")
        print(f"    ANÁLISIS DE CAPACIDAD AEROPORTUARIA - {aeropuerto}")
        print("====================================================")
        print(f"\nPeríodo analizado: {fecha_inicio} a {fecha_fin}")
        
        print("\nCAPACIDAD DE PISTA")
        print("------------------")
        cap = resultados['capacidad_detallada']
        print(f"Capacidad máxima: {cap['capacidad_hora']:.0f} operaciones/hora")
        print("  Fórmula: 3600 / max(tiempo_promedio, separación_promedio)")
        print("  → 3600 segundos (1 hora) dividido por el mayor valor entre:")
        print(f"    - Tiempo promedio de ocupación: {cap['tiempo_promedio']:.1f} segundos")
        print(f"    - Separación promedio: {cap['separacion_promedio']:.1f} NM")
        
        print(f"\nTiempo promedio en pista: {cap['tiempo_promedio']:.0f} segundos")
        print("  Cálculo: Promedio ponderado según tipo de operación:")
        print("  Aterrizajes (A):")
        print("    → Ligeras: 60s × frecuencia de uso")
        print("    → Medias:  75s × frecuencia de uso")
        print("    → Pesadas: 90s × frecuencia de uso")
        print("  Despegues (D):")
        print("    → Ligeras: 45s × frecuencia de uso")
        print("    → Medias:  60s × frecuencia de uso")
        print("    → Pesadas: 75s × frecuencia de uso")
        
        print(f"\nSeparación promedio requerida: {cap['separacion_promedio']:.1f} NM")
        print("  Cálculo: Suma ponderada de la matriz de separación según mix de tráfico")
        print("  Matriz de separación mínima (NM):")
        print("  Precedente → Siguiente | Ligera  Media  Pesada")
        print("  Ligera               |    3      3      3")
        print("  Media                |    3      3      5")
        print("  Pesada              |    6      5      4")
        
        print("\nDISTRIBUCIÓN DE TRÁFICO")
        print("----------------------")
        mix = cap['mix_operaciones']
        print("Cálculo: (Número de operaciones por tipo / Total de operaciones) × 100")
        print("\nCategorías de aeronaves:")
        print("  G = Aviación General (Ligera) - Aeronaves < 7,000 kg")
        print("  M/S = Media - Aeronaves entre 7,000 kg y 136,000 kg")
        print("  X = Pesada - Aeronaves > 136,000 kg")
        print("\nDistribución actual:")
        total_ops = sum(mix.values)  # Calculamos el total de operaciones
        for (tipo, cat), prop in mix.items():
            num_ops = int(prop * total_ops)
            print(f"{tipo:<2} - {cat:<7}: {prop*100:>5.1f}% ({num_ops} operaciones)")
        
        print("\nCAPACIDAD DEL SECTOR")
        print("-------------------")
        sector = analisis.analisis_capacidad_sector({
            'tiempo_conflicto': 120,
            'tiempo_coordinacion': 60,
            'tiempo_comunicacion': 15,
            'numero_comunicaciones': 8,
            'velocidad_crucero': 450,
            'distancia_sector': 100
        })
        print(f"Capacidad del sector: {sector['capacidad_horaria']:.0f} aeronaves/hora")
        print("  Fórmula: (3600/TPS) × factor_ocupación")
        print(f"  → 3600/{sector['TPS']} × 0.8 = {sector['capacidad_horaria']:.1f}")
        
        print(f"\nTiempo promedio de sector (TPS): {sector['TPS']} segundos")
        print("  Fórmula: tiempo_conflicto + tiempo_coordinación")
        print("  → 120s + 60s = 180s")
        
        print(f"\nTiempo de fase conflicto (TFC): {sector['TFC']} segundos")
        print("  Fórmula: tiempo_comunicación × número_comunicaciones")
        print("  → 15s × 8 = 120s")
        
        print(f"\nTiempo de sobrevuelo (SCV): {sector['SCV']/60:.1f} minutos")
        print("  Fórmula: (distancia_sector/velocidad_crucero) × 3600")
        print("  → (100 NM/450 nudos) × 3600 = 800s = 13.3 minutos")
    except Exception as e:
        print(f"\nError: {str(e)}")