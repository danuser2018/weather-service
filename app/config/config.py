from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional

class Settings(BaseSettings):
    LATITUDE: Optional[float] = None
    LONGITUDE: Optional[float] = None
    REQUEST_TIMEOUT_SECONDS: float = 5.0
    CACHE_TTL_SECONDS: int = 0
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    def validate_required(self) -> None:
        if self.LATITUDE is None or self.LONGITUDE is None:
            raise ValueError("LATITUDE and LONGITUDE must be configured.")

settings = Settings()
