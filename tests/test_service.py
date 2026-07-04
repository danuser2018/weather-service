import pytest
import time
import httpx
from unittest.mock import AsyncMock, MagicMock
from app.services.provider import OpenMeteoProvider, WeatherProviderError
from app.services.weather_service import WeatherService
from app.models.weather import WeatherResponse

@pytest.mark.asyncio
async def test_provider_success():
    mock_client = MagicMock(spec=httpx.AsyncClient)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "current": {"temperature_2m": 28.3},
        "daily": {"precipitation_probability_max": [20]}
    }
    mock_client.get = AsyncMock(return_value=mock_response)

    provider = OpenMeteoProvider(mock_client, cache_ttl_seconds=0)
    weather = await provider.get_weather(40.4168, -3.7038)

    assert weather.temperature == 28.3
    assert weather.precipitation_probability == 20
    mock_client.get.assert_called_once()

@pytest.mark.asyncio
async def test_provider_timeout_exception():
    mock_client = MagicMock(spec=httpx.AsyncClient)
    mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

    provider = OpenMeteoProvider(mock_client, cache_ttl_seconds=0)
    with pytest.raises(WeatherProviderError) as excinfo:
        await provider.get_weather(40.4168, -3.7038)
    assert "timed out" in str(excinfo.value)

@pytest.mark.asyncio
async def test_provider_request_error():
    mock_client = MagicMock(spec=httpx.AsyncClient)
    mock_client.get = AsyncMock(side_effect=httpx.RequestError("Request failed"))

    provider = OpenMeteoProvider(mock_client, cache_ttl_seconds=0)
    with pytest.raises(WeatherProviderError) as excinfo:
        await provider.get_weather(40.4168, -3.7038)
    assert "unreachable" in str(excinfo.value)

@pytest.mark.asyncio
async def test_provider_invalid_format():
    mock_client = MagicMock(spec=httpx.AsyncClient)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "current": {}
    }
    mock_client.get = AsyncMock(return_value=mock_response)

    provider = OpenMeteoProvider(mock_client, cache_ttl_seconds=0)
    with pytest.raises(WeatherProviderError) as excinfo:
        await provider.get_weather(40.4168, -3.7038)
    assert "invalid data format" in str(excinfo.value)

@pytest.mark.asyncio
async def test_provider_cache_ttl():
    mock_client = MagicMock(spec=httpx.AsyncClient)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "current": {"temperature_2m": 25.0},
        "daily": {"precipitation_probability_max": [10]}
    }
    mock_client.get = AsyncMock(return_value=mock_response)

    provider = OpenMeteoProvider(mock_client, cache_ttl_seconds=5)
    
    # First call: queries provider
    weather1 = await provider.get_weather(40.4168, -3.7038)
    assert weather1.temperature == 25.0
    assert mock_client.get.call_count == 1

    # Second call: served from cache
    weather2 = await provider.get_weather(40.4168, -3.7038)
    assert weather2.temperature == 25.0
    assert mock_client.get.call_count == 1

    # Simulate cache expiration
    cache_key = (40.4168, -3.7038)
    provider._cache[cache_key] = (time.time() - 10, weather1)

    # Third call: cache expired, queries provider again
    weather3 = await provider.get_weather(40.4168, -3.7038)
    assert weather3.temperature == 25.0
    assert mock_client.get.call_count == 2
