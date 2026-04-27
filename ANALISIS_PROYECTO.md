# Análisis de Arquitectura y Estructura del Proyecto: UshuaiaTravel (v2.0)

Este documento detalla la estructura, arquitectura avanzada y los componentes implementados en el proyecto UshuaiaTravel. El sistema ha evolucionado hacia una plataforma SaaS premium altamente escalable, resiliente y orientada a eventos, compuesta por un backend robusto en Django y un frontend optimizado en Next.js.

---

## 1. Visión General (Top-Down)

El proyecto sigue una arquitectura de microservicios contenerizados (Docker Compose), donde la responsabilidad se divide estrictamente:
- **Backend**: Lógica de negocio compleja, geolocalización, tareas asíncronas y extracción de datos.
- **Frontend**: Renderizado híbrido (SSR/ISR), internacionalización y telemetría de usuario.
- **Infraestructura de Datos**: Base de datos relacional con capacidades espaciales y caché en memoria.

### Infraestructura de Servicios (Docker)
*   **`core-api`**: Servidor principal de Django expuesto en el puerto 8000. Utiliza un *Multi-Stage Dockerfile* para optimizar el tamaño de la imagen en producción.
*   **`worker-scraper`**: Nodo de procesamiento en segundo plano utilizando **Celery**. Se encarga de las tareas pesadas (scraping, envío de emails) sin bloquear la API principal.
*   **`db`**: Base de datos **PostgreSQL con PostGIS** (imagen `postgis:14-3.3-alpine`) para soporte de búsquedas geolocalizadas.
*   **`redis`**: Broker de mensajes para Celery y sistema de caché ultrarrápido para las respuestas de la API de DRF.
*   **`frontend`**: Cliente construido en **Next.js** expuesto en el puerto 3000.

---

## 2. Análisis Detallado de Arquitectura y Patrones

### A. Backend - El Núcleo (`hotels/` y `ushuaia_travel/`)

Esta aplicación gestiona la lógica empresarial avanzada bajo estrictos patrones de diseño de software.

*   **Modelos y Base de Datos Avanzada (`models.py`)**
    *   **Patrón `BaseModel` y Soft Delete**: Todos los modelos heredan de un modelo base abstracto que provee auditoría de fechas (`created_at`, `updated_at`) y borrado lógico (`deleted_at`), previniendo la pérdida accidental de datos históricos mediante un `SoftDeleteManager`.
    *   **`Hotel`**: Modelo central optimizado. Incorpora `PointField` de PostGIS para búsquedas por radio geográfico, y `SearchVectorField` (con `GinIndex`) para búsquedas de texto completo (Full-Text Search).
    *   **`PriceAlert`**: Nuevo modelo orientado a eventos, almacena umbrales de precios para notificar a los usuarios.

*   **Capa de Servicios y Señales (`services.py` y `signals.py`)**
    *   **Patrón Service Layer**: La lógica de cálculo complejo (como el rango de precios y mínimos) se extrajo a `HotelService`. Esto desacopla las reglas de negocio de los modelos y las vistas.
    *   **Orientación a Eventos (Signals)**: Al insertarse o modificarse un precio, un *signal* de Django dispara automáticamente el recálculo en el caché del hotel sin que la vista intervenga.

*   **Vistas Optimizadas y Caché (`views.py`)**
    *   **Prevención N+1**: Los `ViewSets` utilizan agresivamente `prefetch_related` (ej. `Prefetch('prices', ...)` y `amenities`) para resolver jerarquías de datos complejas en 2 consultas a la base de datos en lugar de cientos.
    *   **Caché en Redis**: Los endpoints pesados (como la lista de hoteles filtrada) están decorados con `@method_decorator(cache_page)` para servir respuestas en milisegundos directamente desde la memoria RAM.

*   **Tareas Asíncronas y Automatización (`tasks.py`)**
    *   **Celery Beat**: Configurado en `settings.py` para disparar el scraping de plataformas a las 3:00 AM (`scrape-booking-daily`).
    *   **Alertas de Precio**: Tareas asíncronas (`check_price_drops_and_notify`) evalúan caídas de precio y notifican vía correo electrónico mediante SendGrid/SES.

*   **Seguridad, Red y Nube (`settings.py`)**
    *   **AWS S3**: Integración nativa con `django-storages` para alojar *media* y *staticfiles* en la nube.
    *   **Throttling en DRF**: Límites de peticiones estrictos (100/día anónimos, 1000/día usuarios) para mitigar el raspado abusivo de nuestra API por terceros.
    *   **CORS y SSL**: Políticas de orígenes cruzados restringidas a los dominios autorizados y redirección segura obligatoria.

### B. Módulo de Scraping Resiliente (`scrapers/`)

*   **Aislamiento de Contextos**: El `BookingScraper` evolucionó para manejar iteraciones de extracción complejas utilizando `context.new_page()` de Playwright. Esto permite abrir instancias de navegación limpias e independientes por cada hotel, evitando la polución de cookies y previniendo la pérdida de la página de resultados principal de búsqueda.

### C. Frontend - Next.js App Router (`frontend/`)

El cliente transicionó de una SPA clásica a un ecosistema Server-Side para potenciar el SEO orgánico.

*   **Generación Estática Incremental (ISR) y Rutas Dinámicas**
    *   `app/hotels/[id]/page.tsx`: Las páginas de detalle de hotel son generadas en el servidor durante la construcción (build-time) mediante `generateStaticParams`, garantizando tiempos de carga ínfimos (First Contentful Paint). La revalidación automática (`revalidate = 3600`) asegura que la información de precios no envejezca más de una hora.
*   **Lazy Loading Dinámico de Componentes Críticos**
    *   Componentes pesados o dependientes del objeto global `window` (como los mapas de Leaflet/Mapbox) se cargan diferidos (`next/dynamic` con `ssr: false`), eliminando el bloqueo del hilo principal de ejecución.
*   **Cliente HTTP Resiliente (`api/client.ts`)**
    *   Instancia global configurada para interceptar errores de red (`429 Too Many Requests`) y gestionar *timeouts* estrictos.
*   **Internacionalización (i18n)**
    *   Middleware estructural de Next.js (`next-intl/middleware`) que inyecta enrutamiento según la preferencia de idioma del navegador del turista (ES, EN, PT).
*   **Telemetría y Analítica Integrada**
    *   Integración pasiva con **PostHog** mediante un proveedor global de contexto en el layout maestro (`RootLayout`). Permite mapas de calor, grabación de sesiones y embudos de conversión sin comprometer la métrica *Core Web Vitals*.

---

## 3. Conclusión Arquitectónica

UshuaiaTravel ha madurado hasta convertirse en un entorno "Enterprise-Ready". La aplicación es capaz de:
1.  **Soportar Picos de Tráfico (Alta Concurrencia):** Gracias a Redis, Caché de API y Generación Estática (ISR).
2.  **Mantenerse Confiable:** Separando procesos costosos mediante Celery Workers y protegiendo la base de datos de consultas N+1.
3.  **Proveer una Base Sólida para el Negocio Local:** Preparada para monetizar mediante sistema Multi-Lenguaje, métricas precisas (PostHog), almacenamiento Geoespacial (PostGIS) y orquestación multi-nube con AWS S3.
