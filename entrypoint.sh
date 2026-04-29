#!/bin/bash
set -e

echo "=== UshuaiaTravel Entrypoint ==="

if [ -n "$DATABASE_URL" ] && [[ "$DATABASE_URL" == postgres* ]]; then
    echo "Waiting for PostgreSQL..."
    until python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')" 2>/dev/null; do
        echo "  Database unavailable, retrying in 2s..."
        sleep 2
    done
    echo "PostgreSQL ready."
fi

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear 2>/dev/null || true

HOTEL_COUNT=$(python -c "from hotels.models import Hotel; print(Hotel.objects.count())" 2>/dev/null || echo "0")
if [ "$HOTEL_COUNT" = "0" ]; then
    echo "No hotels found. Running initial scrape from Booking..."
    python manage.py scrape_hotels --max-hotels 3 --platform booking 2>/dev/null || true
    echo "Initial scrape complete."
fi

echo "Starting server..."
if [ "$DJANGO_RUNSERVER" = "true" ]; then
    exec python manage.py runserver 0.0.0.0:${PORT:-8000}
else
    exec gunicorn --bind 0.0.0.0:${PORT:-8000} ushuaia_travel.wsgi:application
fi
