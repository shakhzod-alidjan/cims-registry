.PHONY: help build up down logs shell migrate superuser import static test

help:
	@echo "IT Registry — команды управления"
	@echo ""
	@echo "  make up          — запустить все сервисы"
	@echo "  make down        — остановить"
	@echo "  make build       — пересобрать Docker образы"
	@echo "  make logs        — логи всех сервисов"
	@echo "  make shell       — Django shell"
	@echo "  make migrate     — применить миграции"
	@echo "  make superuser   — создать суперпользователя"
	@echo "  make import f=path/to/file.xlsx — импорт из Excel"
	@echo "  make static      — собрать статику"
	@echo "  make test        — запустить тесты"

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

logs-web:
	docker compose logs -f web

logs-celery:
	docker compose logs -f celery

shell:
	docker compose exec web python manage.py shell

bash:
	docker compose exec web bash

migrate:
	docker compose exec web python manage.py migrate

makemigrations:
	docker compose exec web python manage.py makemigrations

superuser:
	docker compose exec web python manage.py createsuperuser

import:
	docker compose exec web python manage.py import_excel $(f)

import-dry:
	docker compose exec web python manage.py import_excel $(f) --dry-run

static:
	docker compose exec web python manage.py collectstatic --noinput

test:
	docker compose exec web python manage.py test --verbosity=2

restart:
	docker compose restart web celery celery-beat

ps:
	docker compose ps
