# Makefile
.PHONY: up down build rebuild logs backend-logs db-logs redis-logs test migrate

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

rebuild:
	docker-compose down && docker-compose up -d --build

logs:
	docker-compose logs -f

backend-logs:
	docker-compose logs -f backend

db-logs:
	docker-compose logs -f db

redis-logs:
	docker-compose logs -f redis

test:
	docker-compose exec backend pytest -v

migrate:
	docker-compose exec backend alembic upgrade head

shell:
	docker-compose exec backend bash

db-shell:
	docker-compose exec db psql -U $$(grep POSTGRES_USER .env | cut -d '=' -f2) $$(grep POSTGRES_DB .env | cut -d '=' -f2)

format:
	docker-compose exec backend black .
	docker-compose exec backend isort .

lint:
	docker-compose exec backend black --check .
	docker-compose exec backend isort --check .
	docker-compose exec backend flake8 .
