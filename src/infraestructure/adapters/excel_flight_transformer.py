# tsis_umb_data_science/src/infraestructure/adapters/excel_flight_transformer.py
import pandas as pd
from datetime import datetime, time
from pathlib import Path

class ExcelFlightTransformer:
    def __init__(self, file_path):
        self.file_path = file_path

    def transform_flights(self):
        df = pd.read_excel(self.file_path)
        flights = []
        for _, row in df.iterrows():
            # Estandarizar campos y manejar campos adicionales
            # Obtener fecha y hora de salida y llegada
            fecha_salida = pd.to_datetime(row.get('fecha_salida', datetime.now().date()))
            hora_salida = row.get('hora_salida', datetime.now().time())
            if not isinstance(hora_salida, time):
                hora_salida = pd.to_datetime(hora_salida).time()

            fecha_llegada = pd.to_datetime(row.get('fecha_llegada', datetime.now().date()))
            hora_llegada = row.get('hora_llegada', datetime.now().time())
            if not isinstance(hora_llegada, time):
                hora_llegada = pd.to_datetime(hora_llegada).time()

            # Combinar fecha y hora en un objeto datetime
            datetime_salida = datetime.combine(fecha_salida.date(), hora_salida)
            datetime_llegada = datetime.combine(fecha_llegada.date(), hora_llegada)

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
                "fecha_salida": fecha_salida,
                "hora_salida": datetime_salida,
                "destino": row.get('destino', ''),
                "pista_destino": row.get('pista_destino', None),
                "fecha_llegada": fecha_llegada,
                "hora_llegada": datetime_llegada,
                "nivel": row.get('nivel', None),
                "ambito": row.get('ambito', None),
                "nombre_origen": row.get('nombre_origen', ''),
                "nombre_destino": row.get('nombre_destino', '')
            }
            flights.append(flight_data)
        return flights
