# Documento de Refinamiento: Primera Implementación del Weather Service

- **Documento de Origen**: [first_implementation.md](file:///home/danuser2018/workspace/weather-service/doc/features/first_implementation.md)
- **Estado**: Refinado / Listo para revisión de DoR

---

## 1. Resumen y Contexto de Negocio

El **Weather Service** es un nuevo microservicio diseñado para proporcionar información meteorológica normalizada y desacoplada al asistente de voz Nova. Su propósito es actuar como una interfaz de abstracción para servicios externos de clima. En esta primera versión, consumirá la API pública de **Open-Meteo** para consultar la temperatura actual y la probabilidad máxima de precipitación diaria para una ubicación geográfica preconfigurada (latitud y longitud).

Este servicio funciona de manera aislada (no se integra en el orquestador general de Nova en este cambio) y se expone a través de una API REST rápida y ligera.

---

## 2. Análisis de Servicios e Impacto

| Servicio | Tipo de Cambio | Descripción del Impacto |
| :--- | :--- | :--- |
| `weather-service` | **[NEW]** | Creación completa del servicio, incluyendo estructura del código, configuración, endpoints de API REST, dockerización, tests unitarios y de integración, y documentación del proyecto. |
| Otros servicios de Nova | **Ninguno** | Este cambio no tiene impacto en otros servicios ya que no se realiza la integración en el orquestador principal durante esta fase. |

---

## 3. Especificación de Comportamiento (Criterios de Aceptación)

### Escenario 1: Consulta del clima actual de forma exitosa
```gherkin
Scenario: Successful query of current weather
  Given that the service has valid coordinates configured (LATITUDE = "40.4168", LONGITUDE = "-3.7038")
  And the external weather provider (Open-Meteo) returns a temperature of 28.3°C and daily max precipitation probability of 20%
  When a GET request is made to "/v1/weather/current"
  Then the service must respond with HTTP status 200
  And the JSON response body must match:
    """
    {
      "temperature": 28.3,
      "precipitation_probability": 20
    }
    """
  And the JSON response body must NOT contain the "error" field
```

### Escenario 2: El proveedor externo de clima no está disponible
```gherkin
Scenario: External weather provider is unavailable
  Given that the service has valid coordinates configured
  And the external weather provider (Open-Meteo) times out or returns HTTP 5xx errors
  When a GET request is made to "/v1/weather/current"
  Then the service must respond with HTTP status 503
  And the JSON response body must match the ADR-004 error format:
    """
    {
      "error": "WEATHER_PROVIDER_UNAVAILABLE",
      "message": "Weather information is currently unavailable.",
      "status": 503
    }
    """
```

### Escenario 3: Error de configuración o fallo interno
```gherkin
Scenario: Missing mandatory configuration parameters
  Given that the service has NOT defined either LATITUDE or LONGITUDE environment variables
  When a GET request is made to "/v1/weather/current"
  Then the service must respond with HTTP status 500
  And the JSON response body must match the ADR-004 error format:
    """
    {
      "error": "INTERNAL_ERROR",
      "message": "Internal server error.",
      "status": 500
    }
    """
```

---

## 4. Diseño Técnico y Contratos

### Estructura de Directorios
```text
weather-service/
│
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── controllers.py
│   │   ├── routes.py
│   │   └── server.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── weather.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── provider.py
│   │   └── weather_service.py
│   ├── __init__.py
│   └── main.py
│
├── doc/
│   ├── features/
│   │   └── first_implementation.md
│   └── refinements/
│       └── first_implementation_refinement.md
│
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_config.py
│   └── test_service.py
│
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── CHANGELOG.md
└── README.md
```

### Contratos de Datos (English)

#### API Endpoint: `GET /v1/weather/current`

#### Pydantic Model - Response:
```python
from pydantic import BaseModel

class WeatherResponse(BaseModel):
    temperature: float
    precipitation_probability: int
```

#### Pydantic Model - Error (ADR-004 Compliant):
```python
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    error: str
    message: str
    status: int
```
*Nota: Para alinearnos con la directiva arquitectónica del ecosistema (ADR-004: Estandarización de APIs REST) y los demás servicios del asistente (ej. `tts-capability`), utilizaremos la estructura de error plana requerida por el ecosistema en lugar del formato anidado inicialmente propuesto en `first_implementation.md`. Esta decisión supone una desviación deliberada del contrato original del documento de feature, aceptada durante la revisión DoR.*

---

#### API Endpoint: `GET /health`

#### Pydantic Model - Health Response:
```python
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str  # Always "UP"
```

#### Response Example (HTTP 200):
```json
{"status": "UP"}
```

---

## 5. Casos de Borde y Manejo de Errores

1.  **Timeouts en peticiones salientes**:
    - Las peticiones a Open-Meteo utilizarán el parámetro `REQUEST_TIMEOUT_SECONDS` (por defecto 5.0). Si se supera, se capturará `httpx.TimeoutException` y se lanzará un error HTTP 503 con código `WEATHER_PROVIDER_UNAVAILABLE`.
2.  **Respuestas corruptas o inesperadas**:
    - Si el formato del JSON de Open-Meteo cambia o carece de las claves `current.temperature_2m` o `daily.precipitation_probability_max`, se capturará `KeyError` o `IndexError` mapeándolo a una excepción controlada que se traduce en un error HTTP 503 con código `WEATHER_PROVIDER_UNAVAILABLE` para proteger la estabilidad del servicio.
3.  **Sistema de Caché local**:
    - Con el fin de evitar bloqueos por límite de peticiones (rate limiting) de Open-Meteo y optimizar el rendimiento (RNF-002), se implementará una caché simple en memoria en el proveedor.
    - Si `CACHE_TTL_SECONDS` está configurado con un número mayor a 0, se almacenará la respuesta y su timestamp. Las peticiones dentro de ese intervalo de tiempo se servirán directamente de la caché.

---

## 6. Estrategia de Testing

-   **Pruebas de Configuración (`tests/test_config.py`)**:
    - Validar que las variables obligatorias `LATITUDE` y `LONGITUDE` se validen correctamente y lancen excepciones de inicialización si faltan.
-   **Pruebas de Proveedor y Servicio (`tests/test_service.py`)**:
    - Probar la lógica de consulta y formateo usando mocks de la librería `httpx`.
    - Probar el comportamiento de la caché en memoria y el control de expiración TTL.
    - Validar la traducción de excepciones de conexión y timeouts.
-   **Pruebas de API REST (`tests/test_api.py`)**:
    - Probar endpoint `/health` (esperando HTTP 200 `{"status": "UP"}`).
    - Probar endpoint `/v1/weather/current` simulando respuestas del proveedor externa (mock).
    - Verificar respuestas de error estructuradas según ADR-004 en caso de fallo del proveedor (HTTP 503) o error interno (HTTP 500).

---

## 7. Plan de Implementación

-   `[ ]` **Tarea 1: Inicialización del Entorno**
    - Crear `requirements.txt` con `fastapi`, `uvicorn`, `pydantic-settings`, `httpx`, `pytest` y `pytest-asyncio`.
    - Crear `.env.example` y `.env` con las variables `LATITUDE`, `LONGITUDE` y `REQUEST_TIMEOUT_SECONDS` con valores por defecto.
-   `[ ]` **Tarea 2: Capa de Modelado y Configuración**
    - Implementar `app/config/config.py` heredando de `BaseSettings`.
    - Implementar `app/models/weather.py` con los modelos de respuesta de éxito, error y salud.
-   `[ ]` **Tarea 3: Proveedor de Clima (Open-Meteo) y Caché**
    - Implementar la interfaz abstracta `WeatherProvider` en `app/services/provider.py`.
    - Desarrollar la clase concreta `OpenMeteoProvider` con peticiones HTTP asíncronas usando `httpx.AsyncClient` y el mecanismo de caché basado en TTL.
-   `[ ]` **Tarea 4: Capa de Lógica (Service / Controller)**
    - Implementar `app/services/weather_service.py` inyectando el proveedor.
    - Implementar `app/api/controllers.py`.
-   `[ ]` **Tarea 5: Capa de Rutas y Servidor (FastAPI)**
    - Crear `app/api/routes.py` declarando los endpoints y realizando la instanciación de dependencias.
    - Crear `app/api/server.py` configurando los manejadores globales de excepciones para cumplir con ADR-004.
    - Crear `app/main.py` como punto de entrada de la aplicación.
-   `[ ]` **Tarea 6: Contenedorización**
    - Crear el archivo `Dockerfile`.
    - Crear `docker-compose.yml`.
-   `[ ]` **Tarea 7: Pruebas Automatizadas**
    - Crear el suite de pruebas en `tests/test_config.py`, `tests/test_service.py` y `tests/test_api.py`.
    - Ejecutar y validar que pasen todos los tests.
-   `[ ]` **Tarea 8: Documentación y Control de Cambios**
    - Completar el archivo `README.md` del proyecto en español siguiendo el estilo y nivel de detalle de `identity-service`.
    - Registrar los cambios en `CHANGELOG.md` bajo la sección `[Sin publicar]`.
