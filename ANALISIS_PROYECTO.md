# Análisis de Arquitectura y Estructura del Proyecto: UshuaiaTravel (v2.1)

Este documento detalla la estructura, arquitectura avanzada y los componentes implementados en UshuaiaTravel. El sistema ha evolucionado hacia una plataforma de costo-cero operativa, altamente eficiente y optimizada para el mercado local de Ushuaia, Argentina.

---

## 1. Visión General (Top-Down)

El proyecto utiliza una arquitectura híbrida optimizada para eficiencia de recursos y escalabilidad:
- **Backend (Django)**: Lógica de negocio, geolocalización (PostGIS) y motor de conversión de moneda.
- **Frontend (React + Vite)**: Aplicación ultra-rápida con capacidades de PWA y soporte offline.
- **Automatización (GitHub Actions)**: Procesamiento pesado de scraping y actualización de datos off-grid (fuera del servidor web).
- **Infraestructura Cloud-Free**: Diseñado para correr en **Render (API)**, **Vercel (Frontend)** y **Supabase (PostgreSQL)** sin costos operativos fijos.

---

## 2. Análisis Detallado de Arquitectura y Patrones

### A. Backend - Inteligencia de Negocio y Conversión
*   **Motor Multi-Moneda (`CurrencyService`)**: Integración con **DolarAPI** para obtener cotizaciones en tiempo real (Oficial, MEP, Blue). Permite al usuario ver precios en ARS o USD dinámicamente.
*   **Geolocalización Avanzada**: Uso de **PostGIS** para almacenamiento y búsqueda de coordenadas de hoteles, permitiendo visualización espacial precisa.
*   **Capa de Servicios**: La lógica de negocio está centralizada en servicios desacoplados, facilitando el mantenimiento y la extensibilidad del sistema de precios.

### B. Frontend - PWA y Diseño Premium
*   **Ecosistema React + Vite**: Migración a un entorno de desarrollo moderno que prioriza la velocidad de carga (HMR) y un bundle optimizado.
*   **Capacidades PWA (Progressive Web App)**: 
    *   **Soporte Offline**: Service Workers configurados para cachear datos de hoteles y assets estáticos, permitiendo el uso de la web sin conexión en zonas remotas de la Patagonia.
    *   **Instalabilidad**: La aplicación puede instalarse en dispositivos móviles como una app nativa.
*   **Componentes Atómicos y Premium**:
    *   **Mapa Interactivo (Leaflet)**: Visualización geoespacial de hoteles con clusters y popups informativos.
    *   **Price Comparison Widget**: Herramienta de visualización que destaca el ahorro entre plataformas (Booking vs. Otros).

### C. Automatización y Scraping de Bajo Costo
*   **Scraping con GitHub Actions**: El proceso de extracción de datos (Playwright) se ha movido a flujos de trabajo de GitHub. Esto elimina la necesidad de mantener Workers de Celery encendidos 24/7, reduciendo el consumo de RAM en el servidor de producción a casi cero.
*   **Alertas Integradas**: El sistema de notificaciones de caída de precios se dispara automáticamente al finalizar el scraping diario, garantizando que el usuario reciba la información sin retrasos.
*   **Stealth Scraping**: Uso de `playwright-stealth` para evadir bloqueos de plataformas de reserva, asegurando la integridad de los datos diarios.

### D. Gestión de Infraestructura
*   **Makefile**: Unificación de comandos para desarrollo local (`make build`, `make up`, `make scraper`).
*   **CI/CD**: Pipeline automatizado para validación de código y despliegue continuo a entornos de producción.

---

## 3. Conclusión Arquitectónica (v2.1)

UshuaiaTravel ha madurado hacia un modelo de **SaaS de Bajo Costo** pero de **Alta Fidelidad**. La arquitectura actual permite:
1.  **Cero Costo Operativo**: Aprovechando las capas gratuitas de Supabase, Render, Vercel y GitHub Actions.
2.  **Resiliencia Geográfica**: Preparada para el entorno de Ushuaia con soporte offline real.
3.  **Diferenciación Competitiva**: Ofreciendo conversión multimoneda y comparativa de precios real que las OTAs tradicionales no proveen para el mercado argentino.
