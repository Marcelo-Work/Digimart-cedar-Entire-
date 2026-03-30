#!/bin/bash
set -e

echo "=== Application Starting ==="

mkdir -p /app/data

echo "Running migrations..."
python manage.py migrate --noinput

SEED_PATH=${SEED_SCRIPT:-scripts/seed_public.py}

if [ -f "$SEED_PATH" ]; then
    echo "Seeding database with $SEED_PATH..."
    COUNT=$(python manage.py shell -c "from api.models import User; print(User.objects.count())")
    if [ "$COUNT" -eq 0 ]; then
        python manage.py shell < $SEED_PATH
    else
        echo "Database already seeded, skipping."
    fi
else
    echo "⚠️ Seed script not found: $SEED_PATH"
fi

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:3000 --workers 2 --access-logfile - --error-logfile - config.wsgi:application