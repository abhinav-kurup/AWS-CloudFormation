# Use official Python image
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project
COPY . .

# Expose port for HTTP/WebSocket
EXPOSE 8000

# Set environment variables
ENV DJANGO_SETTINGS_MODULE=core.settings

# (Optional) Collect static files if needed later
# RUN python manage.py collectstatic --noinput

# Run Gunicorn with ASGI support (Uvicorn worker)
CMD ["gunicorn", "core.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "3"]
