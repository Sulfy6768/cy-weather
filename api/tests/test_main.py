"""
Tests unitaires et d'intégration simples pour l'API CY Weather
"""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from fastapi.testclient import TestClient

from main import app
from src.services.weather_service import WeatherService
from src.models.Weather import CurrentWeatherData, WeatherResponse

# TEST UNITAIRE SIMPLE

def test_wmo_code_conversion():
    service = WeatherService()
    
    assert service._get_weather_description(0) == "Ciel dégagé"
    assert service._get_weather_description(61) == "Pluie légère"
    assert service._get_weather_description(999) == "Conditions inconnues"


def test_model_creation():
    weather = CurrentWeatherData(
        temperature=20.0,
        feels_like=18.5,
        humidity=60,
        pressure=1015.0,
        wind_speed=10.0,
        description="Ensoleillé",
        icon="01d",
    )
    
    assert weather.temperature == 20.0
    assert weather.description == "Ensoleillé"


# TEST D'INTÉGRATION SIMPLE


def test_health_endpoint():
    client = TestClient(app)
    
    response = client.get("/api/health")
    
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_weather_endpoint_without_city():
    client = TestClient(app)
    
    response = client.get("/api/weather/current")
    
    assert response.status_code == 422 


def test_weather_endpoint_with_mock():
    client = TestClient(app)
    
    fake_weather = WeatherResponse(
        city="Paris",
        country="FR",
        timestamp=datetime.now(),
        weather=CurrentWeatherData(
            temperature=15.0,
            feels_like=14.0,
            humidity=65,
            pressure=1013.0,
            wind_speed=10.0,
            description="Nuageux",
            icon="03d",
        ),
    )
    with patch(
        "src.resources.weather_resource.weather_service.get_current_weather",
        new_callable=AsyncMock,
        return_value=fake_weather,
    ):
        response = client.get("/api/weather/current?city=Paris")
        
        assert response.status_code == 200
        data = response.json()
        assert data["city"] == "Paris"
        assert data["weather"]["temperature"] == 15.0 