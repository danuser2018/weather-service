import httpx
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.config import settings
from app.api.routes import router
from app.services.provider import OpenMeteoProvider, WeatherProviderError
from app.models.weather import ErrorResponse

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the client with configured timeout if not already present
    client = getattr(app.state, "http_client", None)
    if client is None:
        client = httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS)
        app.state.http_client = client

    # Initialize the weather provider if not already present (allows test mocking)
    if not hasattr(app.state, "weather_provider"):
        app.state.weather_provider = OpenMeteoProvider(client, cache_ttl_seconds=settings.CACHE_TTL_SECONDS)

    yield
    # Clean up the client
    await client.aclose()

def create_app() -> FastAPI:
    """
    Factory function to initialize and configure the FastAPI application.
    """
    app = FastAPI(
        title="Nova Weather Service",
        description="Servicio de clima para Nova",
        version="1.0.0",
        lifespan=lifespan
    )

    @app.exception_handler(WeatherProviderError)
    async def weather_provider_exception_handler(request, exc):
        logger.error(f"Weather provider error: {exc}")
        return JSONResponse(
            status_code=503,
            content=ErrorResponse(
                error="WEATHER_PROVIDER_UNAVAILABLE",
                message="Weather information is currently unavailable.",
                status=503
            ).model_dump()
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request, exc):
        logger.error(f"Configuration or value error: {exc}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="INTERNAL_ERROR",
                message="Internal server error.",
                status=500
            ).model_dump()
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request, exc):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="INTERNAL_ERROR",
                message="Internal server error.",
                status=500
            ).model_dump()
        )

    # Include the main router
    app.include_router(router)

    return app
