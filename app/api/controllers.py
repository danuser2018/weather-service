from app.services.weather_service import WeatherService
from app.models.weather import WeatherResponse, HealthResponse

class WeatherController:
    def __init__(self, service: WeatherService):
        self.service = service

    async def get_current_weather(self) -> WeatherResponse:
        return await self.service.get_current_weather()

    def get_health(self) -> HealthResponse:
        return HealthResponse(status="UP")
