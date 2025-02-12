import pandas as pd
from datetime import datetime
from pathlib import Path

class ExcelFlightTransformer:
    def __init__(self, file_path):
        self.file_path = file_path

    def transform_flights(self):
        df = pd.read_excel(self.file_path)
        flights = []
        for _, row in df.iterrows():
            # Estandarizar campos y manejar campos adicionales
            flight_data = {
                "callsign": row.get('callsign', ''),
                "matricula": row.get('matricula', ''),
                "tipo_aeronave": row.get('tipo_aeronave', ''),
                "empresa": row.get('empresa', ''),
                "numero_vuelo": row.get('numero_vuelo', ''),
                "tipo_vuelo": row.get('tipo_vuelo', ''),
                "tiempo_inicial": pd.to_datetime(row.get('tiempo_inicial', datetime.now())),
                "origen": row.get('origen', ''),
                "pista_origen": row.get('pista_origen', None),
                "sid": row.get('sid', None),
                "fecha_salida": pd.to_datetime(row.get('fecha_salida', datetime.now().date())),
                "hora_salida": pd.to_datetime(row.get('hora_salida', datetime.now().time())),
                "destino": row.get('destino', ''),
                "pista_destino": row.get('pista_destino', None),
                "fecha_llegada": pd.to_datetime(row.get('fecha_llegada', datetime.now().date())),
                "hora_llegada": pd.to_datetime(row.get('hora_llegada', datetime.now().time())),
                "nivel": row.get('nivel', None),
                "ambito": row.get('ambito', None),
                "nombre_origen": row.get('nombre_origen', ''),
                "nombre_destino": row.get('nombre_destino', '')
            }
            flights.append(flight_data)
        return flights
