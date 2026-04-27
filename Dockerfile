FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Configurar variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias de Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Asegurarse de que los navegadores requeridos estén instalados
RUN playwright install chromium

# Copiar el código del proyecto
COPY . /app/

# Exponer el puerto
EXPOSE 8000

# Comando por defecto para producción (Gunicorn)
# docker-compose sobreescribirá este comando para desarrollo
CMD ["gunicorn", "ushuaia_travel.wsgi:application", "--bind", "0.0.0.0:8000"]
