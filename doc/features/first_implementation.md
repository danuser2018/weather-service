# Weather Service - Especificación de Requisitos

## 1. Introducción

### 1.1 Objetivo

El **Weather Service** es un microservicio del ecosistema Nova encargado de proporcionar información meteorológica normalizada al resto de servicios.

Su responsabilidad consiste en consultar un proveedor meteorológico externo y transformar la respuesta al modelo interno utilizado por Nova.

En esta primera versión el servicio únicamente proporciona:

- Temperatura actual.
- Probabilidad de precipitación para el día actual.

La ubicación será configurable y común para toda la instalación de Nova.

---

## 2. Alcance

### Incluido

- Consulta del tiempo actual.
- Integración con un proveedor meteorológico externo.
- Exposición mediante una API REST.
- Transformación al modelo interno de Nova.
- Gestión de errores del proveedor.
- Configuración mediante variables de entorno.

### No incluido

- Consulta por ciudad.
- Consulta por coordenadas.
- Consulta por fecha.
- Predicción de varios días.
- Calidad del aire.
- Humedad.
- Viento.
- Sensación térmica.

---

# 3. Requisitos funcionales

## RF-001 Consulta del tiempo actual

El servicio deberá proporcionar la temperatura actual y la probabilidad de precipitación correspondiente a la ubicación configurada.

---

## RF-002 API REST

El servicio expondrá un endpoint REST para obtener la información meteorológica.

---

## RF-003 Modelo de datos estable

La información devuelta por el servicio deberá ser independiente del proveedor utilizado.

Los consumidores del servicio nunca deberán conocer el formato del proveedor externo.

---

## RF-004 Configuración

La ubicación deberá configurarse mediante variables de entorno.

---

## RF-005 Gestión de errores

Si el proveedor externo no estuviera disponible, el servicio deberá devolver un error controlado.

---

## RF-006 Logging

Todas las consultas al proveedor deberán registrarse para facilitar el diagnóstico de incidencias.

No deberán registrarse datos sensibles.

---

# 4. Requisitos no funcionales

## RNF-001 Independencia del proveedor

La implementación deberá encapsular completamente la comunicación con el proveedor meteorológico.

La sustitución del proveedor no deberá afectar al contrato REST del servicio.

---

## RNF-002 Baja latencia

La consulta deberá completarse en el menor tiempo posible.

Se recomienda utilizar timeout configurable.

---

## RNF-003 Configuración

Toda la configuración deberá realizarse mediante variables de entorno.

---

## RNF-004 Contenerización

El servicio deberá ejecutarse como un contenedor Docker.

---

## RNF-005 Observabilidad

El servicio deberá generar logs estructurados compatibles con el resto del ecosistema Nova.

---

## RNF-006 Versionado

La API deberá versionarse desde su primera versión.

---

# 5. Contrato REST

## Endpoint

```
GET /v1/weather/current
```

---

## Parámetros

Esta primera versión no recibe parámetros.

La ubicación será la configurada en el servicio.

---

## Respuesta correcta

HTTP 200

```json
{
    "temperature": 28.3,
    "precipitation_probability": 20
}
```

---

## Modelo de respuesta

| Campo | Tipo | Descripción |
|--------|------|-------------|
| temperature | number | Temperatura en grados Celsius |
| precipitation_probability | integer | Probabilidad de precipitación (0-100) |

---

## Errores

### Error interno

HTTP 500

```json
{
    "error": {
        "code": "INTERNAL_ERROR",
        "message": "Internal server error."
    }
}
```

---

### Proveedor no disponible

HTTP 503

```json
{
    "error": {
        "code": "WEATHER_PROVIDER_UNAVAILABLE",
        "message": "Weather information is currently unavailable."
    }
}
```

---

# 6. Variables de entorno

| Variable | Descripción |
|-----------|-------------|
| LATITUDE | Latitud de la ubicación |
| LONGITUDE | Longitud de la ubicación |
| REQUEST_TIMEOUT_SECONDS | Timeout de las llamadas HTTP |
| CACHE_TTL_SECONDS | Tiempo de vida de la caché (opcional) |

---

# Anexo A. Integración con Open-Meteo

> Este anexo describe la implementación de referencia del servicio. No forma parte del contrato público del Weather Service.

## API utilizada

```
GET https://api.open-meteo.com/v1/forecast
```

### Parámetros

| Parámetro | Valor |
|-----------|-------|
| latitude | LATITUDE |
| longitude | LONGITUDE |
| current | temperature_2m |
| daily | precipitation_probability_max |
| timezone | auto |

---

## Transformación de datos

| Open-Meteo | Modelo Nova |
|-------------|-------------|
| current.temperature_2m | temperature |
| daily.precipitation_probability_max[0] | precipitation_probability |

---

## Gestión de errores

Los errores del proveedor deberán traducirse a los códigos de error definidos por el Weather Service.

Los mensajes del proveedor nunca deberán exponerse directamente al consumidor.

---

# Anexo B. Evolución prevista

El contrato REST permitirá incorporar en versiones futuras capacidades adicionales sin romper la compatibilidad.

Ejemplos:

```
GET /v1/weather/current?date=2026-07-05
```

```
GET /v1/weather/current?city=Madrid
```

```
GET /v1/weather/current?lat=40.4168&lon=-3.7038
```

Así mismo, el modelo de respuesta podrá ampliarse con nuevos campos, como:

- humedad
- velocidad del viento
- sensación térmica
- índice UV
- calidad del aire

manteniendo la compatibilidad hacia atrás.