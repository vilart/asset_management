# STAGE 1 : Builder
FROM python:3.12-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# GCC and postgresql related libs
RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements
COPY requirements.txt .

# pip wheels to only compile no install
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# STAGE 2 : Runner
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Adding nonroot user for security
RUN addgroup --system appgroup && adduser --system --group appuser

# Lightweight lib for postgresql
RUN apt-get update \
    && apt-get install -y libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy built packages from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install from .whl files
RUN pip install --no-cache /wheels/*

# Copy rest of the code
COPY . .

# Collect static files
RUN SECRET_KEY="dummy" DB_HOST="dummy" DB_NAME="dummy" DB_USER="dummy" DB_PASSWORD="dummy" DB_PORT="dummy" python manage.py collectstatic --noinput

# Change owner of directory app to new user
RUN chown -R appuser:appgroup /app

# Change user from root
USER appuser

EXPOSE 8000

#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["gunicorn", "asset_management.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]