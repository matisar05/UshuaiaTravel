# 🏔️ Ushuaia Travel

Una plataforma moderna de agregación de información turística para Ushuaia, Argentina. Compara precios de hoteles de múltiples plataformas (Booking, Airbnb, TripAdvisor) en un solo lugar.

![Stack](https://img.shields.io/badge/Django-5.0-green) ![React](https://img.shields.io/badge/React-18-blue) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-lightblue)

## ✨ Características

- 🏨 **Comparación de Precios**: Compara hoteles de Booking, Airbnb, TripAdvisor y sitios locales
- 🔍 **Filtros Avanzados**: Busca por precio, estrellas, ubicación, tipo de alojamiento, pet-friendly
- 🔄 **Actualización Automática**: Scraping programado mensualmente para mantener precios actualizados
- 💰 **Monetización**: Integración con Google AdSense y donaciones (MercadoPago, PayPal)
- 🎨 **Diseño Moderno**: Interfaz con paleta de colores inspirada en el invierno de Ushuaia
- 📱 **Responsive**: Funciona perfectamente en desktop, tablet y móvil
- 🔒 **Seguro**: HTTPS, rate limiting, validación de datos

## 🛠️ Stack Tecnológico

### Backend
- **Django 5.0** - Framework web
- **Django REST Framework** - API REST
- **PostgreSQL** - Base de datos
- **Playwright** - Web scraping
- **WhiteNoise** - Static files

### Frontend
- **React 18** - Librería UI
- **Vite** - Build tool
- **Axios** - HTTP client
- **CSS Moderno** - Estilos personalizados

## 📋 Prerrequisitos

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ (producción) o SQLite (desarrollo)
- npm o yarn

## 🚀 Instalación Local

### 1. Clonar el Repositorio

```bash
git clone <tu-repo>
cd ushuaia-travel
```

### 2. Configurar Backend

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Copiar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Ejecutar migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Instalar Playwright browsers
playwright install

# Correr servidor
python manage.py runserver
```

### 3. Configurar Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Correr dev server
npm run dev
```

### 4. Acceder a la Aplicación

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api
- **Admin Panel**: http://localhost:8000/admin

## 🕷️ Web Scraping

### Scraping Manual

```bash
# Scrapear todos los sitios
python manage.py scrape_hotels

# Scrapear solo Booking
python manage.py scrape_hotels --platform booking

# Dry run (sin guardar)
python manage.py scrape_hotels --dry-run

# Limitar cantidad
python manage.py scrape_hotels --max-hotels 20
```

### Scraping Automático

El scraping automático se ejecuta vía GitHub Actions (ver `.github/workflows/scrape_hotels.yml`).

## 📁 Estructura del Proyecto

```
ushuaia-travel/
├── ushuaia_travel/          # Configuración Django
│   ├── settings.py
│   └── urls.py
├── hotels/                  # App de hoteles
│   ├── models.py           # Modelos Hotel y Price
│   ├── serializers.py      # Serializers DRF
│   ├── views.py            # API endpoints
│   ├── admin.py            # Admin panel
│   └── management/
│       └── commands/
│           └── scrape_hotels.py
├── scrapers/               # Scripts de scraping
│   ├── base.py            # Scraper base
│   └── booking_scraper.py # Booking.com
├── frontend/              # React app
│   ├── src/
│   │   ├── components/   # Componentes React
│   │   ├── pages/        # Páginas
│   │   ├── api/          # Cliente API
│   │   └── index.css     # Estilos globales
│   └── package.json
├── requirements.txt       # Dependencias Python
├── .env.example          # Template variables
└── README.md
```

## 🚀 Deployment

### Render (Gratis - Desarrollo)

Ver [RENDER_DEPLOY.md](RENDER_DEPLOY.md) para instrucciones detalladas.

**Resumen rápido:**
1. Conectar repo a Render
2. Crear PostgreSQL database
3. Crear Web Service
4. Configurar variables de entorno
5. Deploy automático desde GitHub

### Railway (Producción)

Ver [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md) para migración desde Render.

**Ventajas de Railway:**
- Sin "sleep" en apps
- Celery/Redis support
- Mejor performance
- $10-15/mes

## 🔧 Variables de Entorno

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# Scraping
SCRAPER_USER_AGENT=Mozilla/5.0...
SCRAPER_DELAY_MS=2000

# Monetization (opcional)
GOOGLE_ADSENSE_CLIENT=ca-pub-xxxxx
MERCADOPAGO_PUBLIC_KEY=TEST-xxxxx
PAYPAL_CLIENT_ID=xxxxx
```

## 📊 API Endpoints

### Hoteles

```
GET  /api/hotels/                    # Listar hoteles
GET  /api/hotels/{id}/               # Detalle de hotel
GET  /api/hotels/{id}/compare_prices/ # Comparar precios
GET  /api/hotels/featured/           # Hoteles destacados
```

**Filtros disponibles:**
- `hotel_type`: hotel, hostel, apart, cabaña, casa
- `location_type`: centro, afueras, montaña
- `stars`: 0-5
- `min_stars`: mínimo de estrellas
- `pet_friendly`: true/false
- `min_price`: precio mínimo
- `max_price`: precio máximo
- `search`: búsqueda por nombre/dirección

### Precios

```
GET  /api/prices/  # Listar precios
```

## 🎨 Personalización

### Colores del Tema

Edita `frontend/src/index.css`:

```css
:root {
  --color-glacier-blue: #4A90A4;
  --color-snow-white: #F8F9FA;
  --color-mountain-gray: #596B7A;
  --color-warm-orange: #FF6B35;
  --color-forest-green: #2D5F5D;
}
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/amazing-feature`)
3. Commit cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## 📝 Roadmap

- [ ] Módulo de excursiones
- [ ] Módulo de restaurantes
- [ ] Chatbot con IA (Google Gemini)
- [ ] Sistema de usuarios
- [ ] Favoritos y comparaciones guardadas
- [ ] Notificaciones de cambios de precio
- [ ] App móvil (React Native)

## ⚖️ Licencia

Este proyecto es de código abierto. Ver [LICENSE](LICENSE) para más detalles.

## 📧 Contacto

¿Preguntas o sugerencias? Abre un issue en GitHub.

---

**Hecho con ❄️ para el Fin del Mundo**
