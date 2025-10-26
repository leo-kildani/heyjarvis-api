# ---------- build stage ----------
FROM python:3.12-slim AS builder
ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /wheels
COPY requirements.txt /wheels/requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
 && pip wheel -r /wheels/requirements.txt -w /wheels \
 && apt-get purge -y build-essential && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/*

# ---------- runtime stage ----------
FROM python:3.12-slim

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# tini for proper signal handling in containers
RUN apt-get update && apt-get install -y --no-install-recommends tini curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install from prebuilt wheels (fast & reproducible)
COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels -r /wheels/requirements.txt

# Copy your source *after* deps to leverage layer caching
COPY . /app

# Create non-root user
RUN useradd -m appuser
USER appuser

EXPOSE 8000

# Use tini as PID 1
ENTRYPOINT ["/usr/bin/tini","--"]
ENV PYTHONPATH="/app"
# Gunicorn + Uvicorn workers
CMD ["gunicorn","-c","gunicorn_conf.py","app.main:app"]
