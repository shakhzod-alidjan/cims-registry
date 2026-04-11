#!/bin/sh
set -e

echo "=== CIMS Registry starting ==="
echo "→ Collecting static files..."
python manage.py collectstatic --noinput

echo "→ Running migrations..."
python manage.py migrate --noinput

echo "→ Starting server..."
exec "$@"
