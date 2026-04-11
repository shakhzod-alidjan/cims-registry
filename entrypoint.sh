#!/bin/sh
set -e

echo "=== IT Registry entrypoint ==="

echo "→ Waiting for database..."
until python -c "
import os, sys, time
import psycopg2
try:
    psycopg2.connect(
        dbname=os.environ.get('DB_NAME','it_registry'),
        user=os.environ.get('DB_USER','postgres'),
        password=os.environ.get('DB_PASSWORD',''),
        host=os.environ.get('DB_HOST','db'),
        port=os.environ.get('DB_PORT','5432'),
        connect_timeout=3
    )
    print('Database ready')
except Exception as e:
    print(f'Waiting: {e}')
    sys.exit(1)
"; do
    sleep 2
done

echo "→ Running migrations..."
python manage.py migrate --noinput

echo "→ Collecting static files..."
python manage.py collectstatic --noinput

echo "→ Starting server..."
exec "$@"
