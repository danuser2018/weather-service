from app.config import settings
from app.models.weather import WeatherResponse
from app.services.provider import WeatherProvider

class WeatherService:
    def __init__(self, provider: WeatherProvider):
        self.provider = provider

    async def get_current_weather(self) -> WeatherResponse:
        settings.validate_required()
        return await self.provider.get_weather(settings.LATITUDE, settings.LONGITUDE)
