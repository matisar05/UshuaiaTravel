# Análisis de Arquitectura y Estructura del Proyecto: UshuaiaTravel

Este documento detalla la estructura, arquitectura y los componentes implementados en el proyecto UshuaiaTravel. El sistema es una aplicación web full-stack compuesta por un backend robusto en Django y un frontend moderno en React.

---

## 1. Visión General (Top-Down)

El proyecto sigue una arquitectura cliente-servidor clásica, donde la responsabilidad de la lógica de negocio, recolección de datos y persistencia recae sobre el backend, mientras que el frontend se encarga de la presentación y la experiencia de usuario (SPA).

### Estructura de Directorios Principal

*   **Raíz del proyecto**: Contiene archivos de configuración general.
    *   `.env` y `.env.example`: Variables de entorno.
    *   `requirements.txt`: Dependencias del backend (Python).
    *   `db.sqlite3`: Base de datos de desarrollo.
    *   `manage.py`: Script principal de gestión de Django.
    *   `README.md`, `RAILWAY_DEPLOY.md`, `RENDER_DEPLOY.md`: Documentación e instrucciones de despliegue.
*   **`ushuaia_travel/`**: Es el directorio de configuración central del proyecto Django. Contiene los ajustes globales (`settings.py`), el enrutador principal (`urls.py`) y las configuraciones de servidor (`wsgi.py`/`asgi.py`).
*   **`hotels/`**: Es la aplicación (app) principal del backend. Contiene toda la lógica de negocio, modelos de datos, serializers y vistas para la API.
*   **`scrapers/`**: Un módulo independiente de Python diseñado específicamente para la extracción de datos de precios en diferentes plataformas utilizando web scraping.
*   **`frontend/`**: El cliente de interfaz de usuario construido en React, TypeScript, Vite y TailwindCSS.

---

## 2. Análisis Detallado (Archivo por Archivo)

### A. Backend - Aplicación Principal (`hotels/`)

Esta aplicación gestiona la información de los alojamientos y provee la API REST consumida por el frontend.

*   **`models.py`**
    *   **`Hotel`**: El modelo central. Guarda información detallada del alojamiento.
        *   *Campos clave*: `name`, `description`, `address`, `location_type` (centro, afueras, montaña), `hotel_type` (hotel, hostel, cabaña, etc.), `stars`, `pet_friendly`, `amenities` (como JSON), `contact_info` (JSON), `images` (URLs en JSON), y coordenadas `latitude`/`longitude`.
        *   *Métodos*: `get_min_price()` y `get_price_range()` para calcular dinámicamente los costos basándose en la tabla de precios.
    *   **`Price`**: Registra los precios obtenidos para cada hotel.
        *   *Campos clave*: Llave foránea a `Hotel`, `platform` (Booking, Airbnb, TripAdvisor, local, direct), `price_per_night`, `currency`, `room_type`, `is_available` y `last_checked`.

*   **`views.py`** (Controladores de la API)
    *   **`HotelFilter`**: Extiende de `django_filters.FilterSet` para proveer filtrado complejo, como la capacidad de filtrar por precios mínimos o máximos evaluando la relación con el modelo `Price`.
    *   **`HotelViewSet`**: Endpoint principal de la API (`ReadOnlyModelViewSet`). Provee capacidades de búsqueda, filtrado y ordenamiento. Contiene acciones personalizadas (rutas extra):
        *   `@action compare_prices`: Agrupa los precios de un hotel por plataforma para mostrarlos en el comparador.
        *   `@action featured`: Devuelve el top 10 de hoteles mejor calificados (4+ estrellas).
    *   **`PriceViewSet`**: Endpoint para visualizar precios individuales.

*   **`serializers.py`**
    *   Controla la serialización de los modelos a JSON (y viceversa). Implementa `HotelListSerializer` (para las vistas de listado con información reducida) y `HotelDetailSerializer` (para la vista de detalle con toda la información y lista de precios asociados).

*   **`admin.py`**
    *   Configura la interfaz de administración nativa de Django para poder realizar operaciones CRUD (Crear, Leer, Actualizar, Borrar) de manera manual sobre los Hoteles y Precios.

### B. Backend - Módulo de Scraping (`scrapers/`)

Se encarga de la recolección automatizada de precios y disponibilidad.

*   **`base.py`**
    *   Contiene la clase abstracta `BaseScraper`.
    *   Utiliza **Playwright** para levantar navegadores headless que pueden interactuar con páginas web dinámicas.
    *   *Funcionalidades clave*: Manejo de esperas (`wait_polite`), navegación segura con captura de errores (`safe_navigate`, `safe_click`), extracción de texto (`safe_text`), y un potente método `normalize_price()` para limpiar textos de precios, manejando la casuística de separadores de miles y decimales latinos/argentinos (ARS).

*   **Scrapers Específicos** (`booking_scraper.py`, `airbnb_scraper.py`, `tripadvisor_scraper.py`)
    *   Heredan de `BaseScraper` y contienen la lógica particular para leer el DOM de cada plataforma y recolectar los datos estandarizados que luego son inyectados en el modelo `Price`.

### C. Frontend (`frontend/src/`)

El frontend está desarrollado bajo una arquitectura moderna orientada a componentes.

*   **Configuración y Dependencias (`package.json`)**
    *   **Core**: React 19, TypeScript, React Router v7.
    *   **Data Fetching**: `@tanstack/react-query` v5 y `axios` para peticiones HTTP eficientes y con sistema de caché.
    *   **Estilos y UI**: TailwindCSS, `@headlessui/react` y `lucide-react` para iconos.
    *   **Build Tool**: Vite.

*   **`api/`**
    *   `client.ts`: Configura la instancia principal de Axios con la URL base del backend.
    *   `hotels.ts`: Define las funciones asíncronas para llamar a los endpoints del backend (`/api/hotels/`, `/api/hotels/{id}/`, `/api/hotels/featured/`).

*   **`hooks/`**
    *   `useHotels.ts`: Abstracción de estado usando React Query. Contiene hooks personalizados (`useHotels`, `useHotel`, `useFeaturedHotels`) para que los componentes de React puedan consumir datos de forma reactiva sin preocuparse por manejar `useEffect` o estados de carga (`isLoading`, `isError`).

*   **`pages/`** (Vistas principales)
    *   `HomePage`: Página de inicio (Landing page).
    *   `HotelsPage`: Directorio principal de alojamientos, integra los componentes de búsqueda y filtrado de DRF.
    *   `HotelDetailPage`: Vista profunda de un hotel. Muestra la galería de imágenes, amenidades y el comparador de precios utilizando el endpoint `compare_prices`.
    *   `DonatePage`: Página para gestión de donaciones.

*   **`components/`** (Elementos reutilizables)
    *   Organizados en tres subcarpetas clave:
        *   `common/`: Botones genéricos, barras de progreso, inputs, alertas.
        *   `hotels/`: Tarjetas de presentación de hoteles (`HotelCard`), grillas de listado, y widgets de comparación de precios.
        *   `layout/`: Estructuras maestras como la barra de navegación (Navbar), encabezado (Header) y pie de página (Footer).

---

## 3. Conclusión Arquitectónica

UshuaiaTravel cuenta con una arquitectura muy sólida y escalable. La separación de responsabilidades está claramente definida:
1.  **Django** actúa como una API pura y robusta, delegando el peso del renderizado visual al cliente.
2.  **React + React Query** manejan el estado del lado del cliente de forma fluida y optimizada.
3.  **Playwright Scrapers** permiten una fuente de recolección de datos dinámica que puede integrarse fácilmente mediante tareas asíncronas (como Celery) o cron jobs.
