# 🚀 Deploy Ushuaia Travel a Render (Gratis)

## 📋 Requisitos

- Cuenta gratis en [Render](https://render.com)
- Repo en GitHub (ya lo tenés: `matisar05/UshuaiaTravel`)

## ⚡ Deploy con un click

Ya creé `render.yaml` en el repo. Hacé así:

1. Entrá a https://dashboard.render.com
2. Click **New** → **Blueprint**
3. Conectá tu repo `matisar05/UshuaiaTravel`
4. Render detecta `render.yaml` solo y crea todo

**Esto crea automáticamente:**
- ✅ PostgreSQL gratis
- ✅ Backend Django + Playwright
- ✅ Frontend React estático
- ✅ Variables de entorno

## ⚙️ Después del deploy

### 1. Configurar variables secretas

En Render dashboard, agregá estas variables al **Web Service** (`ushuaia-travel-api`):

| Variable | Valor |
|---|---|
| `RAPIDAPI_KEY` | Tu key de RapidAPI |
| `MERCADOPAGO_ACCESS_TOKEN` | Token de MercadoPago |
| `MERCADOPAGO_SUCCESS_URL` | `https://ushuaia-travel.onrender.com/donar?status=success` |
| `PAYPAL_CLIENT_ID` | Client ID de PayPal |

### 2. Poblar hoteles

En Render dashboard → `ushuaia-travel-api` → **Shell**:

```bash
python manage.py scrape_hotels --platform booking --max-hotels 20
```

### 3. URLs finales

| Servicio | URL |
|---|---|
| **Frontend** | `https://ushuaia-travel.onrender.com` |
| **API** | `https://ushuaia-travel-api.onrender.com/api/v1/` |
| **Admin** | `https://ushuaia-travel-api.onrender.com/admin` |

## 💰 Dominio propio + AdSense

1. Comprá `ushuaiatravel.com.ar` en [nic.ar](https://nic.ar) ($700 ARS/año)
2. En Render → Static Site → Settings → **Custom Domain** → agregalo
3. En Render → Web Service → Settings → **Custom Domain** → `api.ushuaiatravel.com.ar`
4. Actualizá las env vars:
   - `CORS_ALLOWED_ORIGINS=https://ushuaiatravel.com.ar`
   - `MERCADOPAGO_SUCCESS_URL=https://ushuaiatravel.com.ar/donar?status=success`
5. Aplicá a AdSense con tu dominio

## 🔄 GitHub Actions: scraping mensual

El archivo `.github/workflows/scrape_hotels.yml` corre el 1° de cada mes. Necesitás agregar estos secrets en GitHub:

| Secret | Valor |
|---|---|
| `DATABASE_URL` | URL de la DB de Render |
| `SECRET_KEY` | El mismo de producción |
| `RAPIDAPI_KEY` | Tu key |

---

**¿Problemas?** Abrí un issue en el repo.
