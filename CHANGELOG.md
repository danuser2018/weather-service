# Registro de cambios

Todos los cambios notables de este proyecto se documentan en este fichero.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y este proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

## Guía de uso

Cada versión se documenta bajo su número de versión y fecha de publicación.
Los cambios se agrupan en las siguientes categorías:

- **Añadido** — nuevas funcionalidades.
- **Cambiado** — cambios en funcionalidades existentes.
- **Obsoleto** — funcionalidades que serán eliminadas en versiones futuras.
- **Eliminado** — funcionalidades eliminadas en esta versión.
- **Corregido** — corrección de errores.
- **Seguridad** — correcciones de vulnerabilidades.

---

## [1.1.0]

### Añadido

- Archivo `.dockerignore` para optimizar el contexto de construcción de la imagen Docker omitiendo entornos locales, directorios de control de versiones y archivos de prueba.

### Cambiado

- Formato de respuesta del endpoint `/health` modificando el valor del campo `status` de `"UP"` a `"ok"`, alineándolo con la directiva estándar del ecosistema Nova.
- Casos de prueba unitarios en `tests/test_api.py` actualizados para validar el nuevo estado `"ok"`.

---

## [1.0.0]

### Añadido

- Fichero `CONTRIBUTING.md` con el flujo de trabajo Trunk Based Development,
  convenciones de commits, guía de Pull Requests y buenas prácticas para
  desarrollo asistido con IA.
- Fichero `CHANGELOG.md` con el formato Keep a Changelog v1.1.0 en castellano.
- Implementación inicial del microservicio `weather-service` expuesto en `/v1/weather/current` y `/health`.
- Estructura base de código organizada en módulos (`api`, `config`, `models`, `services`).
- Clase concreta `OpenMeteoProvider` para consultas HTTP asíncronas a Open-Meteo.
- Mecanismo de caché en memoria con expiración por TTL (`CACHE_TTL_SECONDS`).
- Gestión estructurada y centralizada de excepciones para cumplir con la directiva ADR-004.
- Archivos de configuración para contenerización mediante `Dockerfile` y `docker-compose.yml` (con healthcheck).
- Cobertura de pruebas completa (`tests/test_config.py`, `tests/test_service.py` y `tests/test_api.py`).
- Tarea de automatización de GitHub Actions (`.github/workflows/test.yml`) para lanzar las pruebas al abrir una PR o al hacer push.
- Documentación completa del proyecto redactada en `README.md`.

---

<!-- Plantilla para nuevas versiones:

## [X.Y.Z] - AAAA-MM-DD

### Añadido
-

### Cambiado
-

### Obsoleto
-

### Eliminado
-

### Corregido
-

### Seguridad
-

-->

[Sin publicar]: https://github.com/danuser2018/weather-service/compare/HEAD...HEAD
