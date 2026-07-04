import httpx
from fastapi import APIRouter, Depends, Request
from app.config import settings
from app.services.provider import OpenMeteoProvider
from app.services.weather_service import WeatherService
from app.api.controllers import WeatherController
from app.models.weather import WeatherResponse, HealthResponse

router = APIRouter()

def get_weather_controller(request: Request) -> WeatherController:
    # Look for provider in request.app.state, fallback to dynamic if not set (for standalone tests)
    provider = getattr(request.app.state, "weather_provider", None)
    if provider is None:
        client = getattr(request.app.state, "http_client", None)
        if client is None:
            client = httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS)
        provider = OpenMeteoProvider(client, cache_ttl_seconds=settings.CACHE_TTL_SECONDS)
    service = WeatherService(provider)
    return WeatherController(service)

@router.get("/v1/weather/current", response_model=WeatherResponse)
async def get_current_weather(
    controller: WeatherController = Depends(get_weather_controller)
) -> WeatherResponse:
    """
    Get the current weather information for the configured coordinates.
    """
    return await controller.get_current_weather()

@router.get("/health", response_model=HealthResponse)
def get_health(
    controller: WeatherController = Depends(get_weather_controller)
) -> HealthResponse:
    """
    Get health check status.
    """
    return controller.get_health()
