# Weather Service

## Descripción

**Weather Service** es el microservicio responsable de proporcionar información meteorológica normalizada y desacoplada al asistente de voz Nova.

Su propósito fundamental es actuar como una interfaz de abstracción para servicios externos de clima, evitando que el orquestador u otros componentes conozcan los detalles específicos de las APIs meteorológicas externas. En esta primera versión, el servicio consume la API pública de **Open-Meteo** para consultar la temperatura actual y la probabilidad máxima de precipitación diaria para una ubicación geográfica preconfigurada (latitud y longitud).

Para optimizar el rendimiento y evitar bloqueos por límite de peticiones (rate limiting) del proveedor externo, el servicio implementa una caché simple en memoria basada en TTL.

---

# Objetivos

* Proveer una única fuente de verdad para los datos meteorológicos dentro del asistente.
* Exponer una API REST consistente y estable que cumpla estrictamente con la directiva **ADR-004** del ecosistema.
* Encapsular por completo la comunicación con proveedores externos (Open-Meteo en la versión actual).
* Controlar los tiempos de respuesta mediante un timeout de petición HTTP configurable.
* Evitar sobrecargar el API externo mediante un sistema de almacenamiento en caché en memoria.

---

# Estado del proyecto

Versión actual: **1.0.0 (MVP)**

Características implementadas:

* API REST asíncrona desarrollada en FastAPI.
* Integración con el proveedor meteorológico externo Open-Meteo.
* Sistema de caché en memoria con expiración por TTL (Time-To-Live).
* Manejo estructurado y centralizado de excepciones y respuestas de error conforme a **ADR-004**.
* Configuración completa a través de variables de entorno mediante `pydantic-settings`.
* Contenerización y configuración de Docker y Docker Compose con healthchecks.
* Cobertura de pruebas unitarias y de integración.

Características previstas para versiones futuras:

* Búsqueda meteorológica dinámica pasando latitud/longitud en la URL.
* Búsqueda por nombre de ciudad (integrando servicios de geocodificación).
* Soporte para pronóstico meteorológico extendido (predicción de varios días).
* Incorporación de nuevas métricas: humedad, velocidad del viento, calidad del aire, índice UV y sensación térmica.
* Integración con otros proveedores meteorológicos alternativos (AEMET, OpenWeatherMap) con selección en caliente.

---

# Responsabilidades

Weather Service **debe**:

* consultar al proveedor de clima externo de manera asíncrona;
* validar la presencia de la configuración geográfica mínima;
* cachear las respuestas exitosas de acuerdo con el TTL configurado;
* normalizar los datos recibidos al esquema de respuesta interno;
* enmascarar los errores técnicos del proveedor y responder según el estándar ADR-004.

Weather Service **no debe**:

* almacenar históricos de clima en base de datos persistente;
* gestionar interfaces de usuario o renderizar HTML;
* realizar geocodificación inversa (traducir coordenadas a ciudades) en esta versión;
* autenticar o autorizar llamadas directamente (asumido por la red interna).

---

# Arquitectura

```
                 +----------------------+
                 |      Orquestador     |
                 +----------+-----------+
                            |
                            |
                 REST API (GET /v1/weather/current)
                            |
                            v
                 +----------------------+
                 |    Weather Service   |
                 +----------+-----------+
                            |
                    Caché en memoria (TTL)
                            |
                            v
                 +----------------------+
                 |  OpenMeteoProvider   |
                 +----------+-----------+
                            |
                     Llamada HTTP
                            |
                            v
                 +----------------------+
                 |    Open-Meteo API    |
                 +----------------------+
```

Si en el futuro se decide cambiar de proveedor meteorológico, solo se deberá crear una nueva clase concreta bajo la interfaz `WeatherProvider`, sin alterar la API REST expuesta hacia el orquestador.

---

# Variables de entorno

El servicio se configura mediante las siguientes variables de entorno:

| Variable | Descripción | Valor por defecto |
| :--- | :--- | :--- |
| `LATITUDE` | Latitud geográfica de la ubicación a consultar | *Obligatorio* |
| `LONGITUDE` | Longitud geográfica de la ubicación a consultar | *Obligatorio* |
| `REQUEST_TIMEOUT_SECONDS` | Tiempo límite de espera para peticiones al proveedor externo | `5.0` |
| `CACHE_TTL_SECONDS` | Tiempo de vida en segundos de la caché en memoria (0 para desactivar) | `0` (desactivada) |
| `PORT` | Puerto donde escuchará el servidor Uvicorn | `8000` |
| `HOST` | Dirección host del servidor | `0.0.0.0` |

Ejemplo de archivo `.env`:

```env
LATITUDE=40.4168
LONGITUDE=-3.7038
REQUEST_TIMEOUT_SECONDS=5.0
CACHE_TTL_SECONDS=60
PORT=8000
HOST=0.0.0.0
```

---

# API REST

## 1. Obtener clima actual

```
GET /v1/weather/current
```

### Respuesta Correcta (HTTP 200)

```json
{
  "temperature": 28.3,
  "precipitation_probability": 20
}
```

### Error de Configuración (HTTP 500)

Ocurre si no se configuran las variables `LATITUDE` o `LONGITUDE`.

```json
{
  "error": "INTERNAL_ERROR",
  "message": "Internal server error.",
  "status": 500
}
```

### Error de Proveedor Externo (HTTP 503)

Ocurre si la API de Open-Meteo está caída, devuelve errores HTTP 5xx o expira el timeout configurado.

```json
{
  "error": "WEATHER_PROVIDER_UNAVAILABLE",
  "message": "Weather information is currently unavailable.",
  "status": 503
}
```

---

## 2. Estado de Salud del Servicio

```
GET /health
```

### Respuesta Correcta (HTTP 200)

```json
{
  "status": "UP"
}
```

---

# Estructura del proyecto

```
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

---

# Ejecución local

## 1. Crear entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 3. Configurar entorno

Copia el archivo de ejemplo y edita las coordenadas de tu ubicación:

```bash
cp .env.example .env
```

## 4. Ejecutar el servidor de desarrollo

```bash
python3 -m app.main
```

El servicio estará disponible en `http://localhost:8000`. Puedes consultar la documentación interactiva en `http://localhost:8000/docs`.

---

# Cómo probar el servicio

Puedes usar `curl` para interactuar con los endpoints:

```bash
# Comprobación de salud
curl -i http://localhost:8000/health

# Consulta del clima
curl -i http://localhost:8000/v1/weather/current
```

---

# Ejecución mediante Docker

## Construir la imagen de Docker

```bash
docker build -t weather-service .
```

## Ejecutar el contenedor

```bash
docker run --env-file .env -p 8000:8000 weather-service
```

## Utilizando Docker Compose

Para levantar el servicio de forma aislada y con reinicio automático:

```bash
docker compose up --build -d
```

---

# Tecnologías utilizadas

* **Python 3.11**
* **FastAPI** (Desarrollo del servidor web y rutas asíncronas)
* **Pydantic / Pydantic Settings** (Validación de datos y tipado fuerte)
* **HTTPX** (Cliente HTTP asíncrono para consumir Open-Meteo)
* **Pytest / Pytest-Asyncio** (Suite de pruebas y soporte asíncrono)
* **Docker / Docker Compose** (Empaquetamiento y aislamiento)

---

# Testing

Para ejecutar toda la suite de pruebas unitarias y de integración de manera local, ejecuta:

```bash
python3 -m pytest
```

---

# Licencia

Licencia MIT.