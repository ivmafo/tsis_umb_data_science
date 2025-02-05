# tests/test_flight.py
import pytest
from datetime import datetime
from domain.entities.flight import Flight
from application.use_cases.create_flight import CreateFlightUseCase
from unittest.mock import Mock

def test_create_flight_with_all_fields():
    mock_repo = Mock()
    mock_repo.save.return_value = Flight(
        callsign="AVA101",
        matricula="HK-4567",
        tipo_aeronave="Boeing 737",
        empresa="Avianca",
        numero_vuelo="101",
        tipo_vuelo="Comercial",
        tiempo_inicial=datetime(2023, 1, 1, 8, 0),
        origen="SKRG",
        pista_origen="01L",
        sid="GEMPA1",
        fecha_salida=datetime(2023, 1, 1, 8, 15),
        hora_salida=datetime(2023, 1, 1, 8, 15),
        destino="SKBO",
        pista_destino="19R",
        fecha_llegada=datetime(2023, 1, 1, 9, 30),
        hora_llegada=datetime(2023, 1, 1, 9, 30),
        nivel="FL350",
        ambito="Nacional",
        nombre_origen="Aeropuerto José María Córdova",
        nombre_destino="Aeropuerto El Dorado"
    )

    use_case = CreateFlightUseCase(mock_repo)
    result = use_case.execute({
            "id": "1",
            "callsign": "AVA101",
            "matricula": "HK-4567",
            "tipo_aeronave": "Boeing 737",
            "empresa": "Avianca",
            "numero_vuelo": "101",
            "tipo_vuelo": "Comercial",
            "tiempo_inicial": datetime(2023, 1, 1, 8, 0),
            "origen": "SKRG",
            "pista_origen": "01L",
            "sid": "GEMPA1",
            "fecha_salida": datetime(2023, 1, 1, 8, 15),
            "hora_salida": datetime(2023, 1, 1, 8, 15),
            "destino": "SKBO",
            "pista_destino": "19R",
            "fecha_llegada": datetime(2023, 1, 1, 9, 30),
            "hora_llegada": datetime(2023, 1, 1, 9, 30),
            "nivel": "FL350",
            "ambito": "Nacional",
            "nombre_origen": "Aeropuerto José María Córdova",
            "nombre_destino": "Aeropuerto El Dorado"
        })

    assert result.callsign 