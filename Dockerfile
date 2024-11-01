# Use Python 3.12 slim base image
FROM python:3.12-slim

# Set basic environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=elektrum.settings \
    SECURE_SSL_REDIRECT=False

WORKDIR /app

# Install system dependencies first - these rarely change
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Install poetry - this rarely changes
RUN pip install poetry \
    && poetry config virtualenvs.create false

# Copy just the dependency files first
COPY pyproject.toml poetry.lock ./

# Install Python dependencies - this only reruns if dependencies change
RUN poetry install --only main

RUN mkdir -p /app/application/staticfiles

# Copy application code - this changes frequently
COPY application application/
COPY docker/entrypoint.sh /entrypoint.sh

# Make entrypoint script executable
RUN chmod +x /entrypoint.sh

# Set working directory to application folder
WORKDIR /app/application

# Expose port 8080
EXPOSE 8080

# Use entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

# Start Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "3", "elektrum.wsgi:application"]
