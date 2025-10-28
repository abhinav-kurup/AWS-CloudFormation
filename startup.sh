#!/bin/bash
set -e  # exit on errors

# If you need to apply DB migrations
echo "Applying migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# (Optional) You might want to run checks or seed data
# python manage.py check

# Start the application via Gunicorn (or other WSGI server)
echo "Starting Gunicorn..."
# Adjust number of workers/threads as needed
gunicorn core.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --threads 4
