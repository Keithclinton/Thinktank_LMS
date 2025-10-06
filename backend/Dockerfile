FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install setuptools first (fixes pkg_resources issue)
RUN pip install --upgrade pip setuptools==75.1.0

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Simple startup command
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn thinktank.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 120"]