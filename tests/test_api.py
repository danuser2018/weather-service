import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from app.api.server import create_app
from app.config import settings
from app.services.provider import WeatherProviderError
from app.models.weather import WeatherResponse

@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client

def test_get_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_current_weather_success(monkeypatch):
    app = create_app()
    
    mock_provider = AsyncMock()
    mock_provider.get_weather.return_value = WeatherResponse(temperature=28.3, precipitation_probability=20)
    
    monkeypatch.setattr("app.config.settings.LATITUDE", 40.4168)
    monkeypatch.setattr("app.config.settings.LONGITUDE", -3.7038)
    
    app.state.weather_provider = mock_provider
    
    with TestClient(app) as test_client:
        response = test_client.get("/v1/weather/current")
        assert response.status_code == 200
        assert response.json() == {
            "temperature": 28.3,
            "precipitation_probability": 20
        }

def test_get_current_weather_provider_unavailable(monkeypatch):
    app = create_app()
    
    mock_provider = AsyncMock()
    mock_provider.get_weather.side_effect = WeatherProviderError("Provider unavailable")
    
    monkeypatch.setattr("app.config.settings.LATITUDE", 40.4168)
    monkeypatch.setattr("app.config.settings.LONGITUDE", -3.7038)
    
    app.state.weather_provider = mock_provider
    
    with TestClient(app) as test_client:
        response = test_client.get("/v1/weather/current")
        assert response.status_code == 503
        assert response.json() == {
            "error": "WEATHER_PROVIDER_UNAVAILABLE",
            "message": "Weather information is currently unavailable.",
            "status": 503
        }

def test_get_current_weather_missing_configuration(monkeypatch):
    app = create_app()
    
    monkeypatch.setattr("app.config.settings.LATITUDE", None)
    monkeypatch.setattr("app.config.settings.LONGITUDE", None)
    
    with TestClient(app) as test_client:
        response = test_client.get("/v1/weather/current")
        assert response.status_code == 500
        assert response.json() == {
            "error": "INTERNAL_ERROR",
            "message": "Internal server error.",
            "status": 500
        }
