# IT Registry

Корпоративная система управления IT-активами: лицензии, интернет-договоры, DNS/домены, Cloud-серверы.

## Стек

- **Backend:** Django 5.1 + PostgreSQL 17 + Redis
- **Tasks:** Celery + Celery Beat (уведомления, отчёты)
- **API:** Django REST Framework + JWT
- **Deploy:** Docker Compose + Nginx + GitHub Actions

---

## Быстрый старт (локально)

```bash
# 1. Клонировать репозиторий
git clone https://github.com/YOUR_ORG/it_registry.git
cd it_registry

# 2. Создать .env файл
cp .env.example .env
# Отредактировать .env — вписать DB пароль, SECRET_KEY и т.д.

# 3. Запустить
docker compose up -d

# 4. Применить миграции
docker compose exec web python manage.py migrate

# 5. Создать суперпользователя
docker compose exec web python manage.py createsuperuser

# 6. Создать объекты (Sites) через Admin
# Открыть: http://localhost/admin/

# 7. (опционально) Импортировать данные из Excel
docker compose exec web python manage.py import_excel /app/data/Corporate_BP_Registry.xlsx
```

Открыть: **http://localhost/**

---

## Деплой на сервер

### Требования на сервере
- Ubuntu 22.04+
- Docker + Docker Compose
- Git

### Первый деплой

```bash
# На сервере
sudo mkdir -p /opt/it_registry
sudo chown $USER:$USER /opt/it_registry
cd /opt/it_registry

git clone https://github.com/YOUR_ORG/it_registry.git .
cp .env.example .env
nano .env   # заполнить все значения

docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

### GitHub Actions Secrets

В репозитории → Settings → Secrets добавить:

| Secret | Описание |
|--------|----------|
| `SERVER_HOST` | IP или домен сервера |
| `SERVER_USER` | SSH пользователь |
| `SERVER_SSH_KEY` | Приватный SSH ключ |
| `SERVER_PORT` | SSH порт (по умолчанию 22) |

После настройки — каждый `push` в `main` автоматически деплоится.

---

## Импорт из Excel

```bash
# Импортировать все листы
python manage.py import_excel data/registry.xlsx

# Только конкретный объект
python manage.py import_excel data/registry.xlsx --site MMG

# Проверка без сохранения
python manage.py import_excel data/registry.xlsx --dry-run
```

---

Добавить новый объект: Django Admin → Core → Sites → Add.

---

## Роли

| Роль | Доступ |
|------|--------|
| Admin | Все объекты, CRUD всего, Django Admin |
| Editor | Только свой объект, добавить/редактировать |
| Viewer | Только просмотр и скачивание |

---

## Celery задачи (автоматические)

| Задача | Расписание |
|--------|-----------|
| Проверка лицензий | Каждый день 09:00 |
| Проверка доменов | Каждый день 09:05 |
| Проверка ISP договоров | Каждый день 09:10 |
| Еженедельный отчёт | Понедельник 08:00 |

---

## API

Swagger документация: `http://localhost/api/docs/`

Основные эндпоинты:
- `GET /api/sites/` — список объектов
- `GET /api/licenses/` — лицензии (фильтр: `?site=1`)
- `GET /api/internet/` — договоры ISP
- `GET /api/dns/` — домены
- `GET /api/cloud/` — серверы

JWT авторизация: `POST /api/token/` → получить токен → передавать как `Authorization: Bearer <token>`
