from pydantic import BaseModel

class WeatherResponse(BaseModel):
    temperature: float
    precipitation_probability: int

class ErrorResponse(BaseModel):
    error: str
    message: str
    status: int

class HealthResponse(BaseModel):
    status: str
