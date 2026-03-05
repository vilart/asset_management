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

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]