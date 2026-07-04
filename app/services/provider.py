import time
import logging
import httpx
from abc import ABC, abstractmethod
from app.models.weather import WeatherResponse

logger = logging.getLogger(__name__)

class WeatherProviderError(Exception):
    """Exception raised for errors in the weather provider."""
    pass

class WeatherProvider(ABC):
    @abstractmethod
    async def get_weather(self, latitude: float, longitude: float) -> WeatherResponse:
        """
        Fetch the current weather for the given coordinates.
        """
        pass

class OpenMeteoProvider(WeatherProvider):
    def __init__(self, client: httpx.AsyncClient, cache_ttl_seconds: int = 0):
        self.client = client
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cache = {}  # key: (lat, lon) -> (timestamp, WeatherResponse)

    async def get_weather(self, latitude: float, longitude: float) -> WeatherResponse:
        now = time.time()
        cache_key = (latitude, longitude)

        if self.cache_ttl_seconds > 0 and cache_key in self._cache:
            timestamp, cached_data = self._cache[cache_key]
            if now - timestamp < self.cache_ttl_seconds:
                logger.info(f"Serving weather data from cache for coordinates: {latitude}, {longitude}")
                return cached_data

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m",
            "daily": "precipitation_probability_max",
            "timezone": "auto"
        }

        try:
            logger.info(f"Querying Open-Meteo API for coordinates: {latitude}, {longitude}")
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Extract fields
            temp = float(data["current"]["temperature_2m"])
            precip = int(data["daily"]["precipitation_probability_max"][0])

            result = WeatherResponse(temperature=temp, precipitation_probability=precip)

            if self.cache_ttl_seconds > 0:
                self._cache[cache_key] = (now, result)

            return result
        except httpx.TimeoutException as e:
            logger.error(f"Timeout querying weather provider: {e}")
            raise WeatherProviderError("Weather provider connection timed out.") from e
        except httpx.RequestError as e:
            logger.error(f"HTTP request error querying weather provider: {e}")
            raise WeatherProviderError("Weather provider is unreachable.") from e
        except (KeyError, IndexError, TypeError, ValueError) as e:
            logger.error(f"Invalid response format from weather provider: {e}")
            raise WeatherProviderError("Weather provider returned invalid data format.") from e
