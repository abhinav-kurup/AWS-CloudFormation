FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and debugging tools
RUN apt-get update && apt-get install -y \
    build-essential \
    net-tools iproute2 curl procps \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=core.settings

CMD ["gunicorn", "core.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "3"]
