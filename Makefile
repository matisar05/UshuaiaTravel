# Makefile for Ushuaia Travel

.PHONY: help build up down logs restart shell test clean scraper

help:
	@echo "Comandos disponibles:"
	@echo "  make build    - Construir imágenes Docker"
	@echo "  make up       - Levantar servicios en segundo plano"
	@echo "  make down     - Detener servicios"
	@echo "  make logs     - Ver logs en tiempo real"
	@echo "  make restart  - Reiniciar servicios"
	@echo "  make shell    - Abrir terminal en core-api"
	@echo "  make test     - Ejecutar pruebas del backend"
	@echo "  make scraper  - Ejecutar el scraper de Booking manualmente"
	@echo "  make clean    - Limpiar volúmenes y archivos huérfanos"

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

restart:
	docker compose restart

shell:
	docker compose exec core-api python manage.py shell

test:
	docker compose exec core-api python manage.py test

scraper:
	docker compose exec worker-scraper celery -A ushuaia_travel call hotels.tasks.run_booking_scraper

clean:
	docker compose down -v --remove-orphans
	find . -type d -name "__pycache__" -exec rm -rf {} +
