# Freewall backend — production Dockerfile (Railway / any Docker host).
# Why Dockerfile not nixpacks: nixpacks' Python+uv autodetect broke on
# `pip install uv==$NIXPACKS_UV_VERSION` (empty interpolation). Dockerfile
# gives us deterministic control over Python version + uv install.

FROM python:3.13-slim

# System deps. `git` not strictly required; libgomp + build-essential in case
# any wheel needs to compile (chromadb, etc) — slim base lacks them.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv (Rust-based, fast Python package manager).
RUN pip install --no-cache-dir uv

# Copy dependency manifests first → leverage Docker layer cache. If only app
# code changes, this layer is reused.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy the rest of the backend (app/, data/, scripts/, etc).
# .dockerignore excludes .venv, __pycache__, tests/, .pytest_cache, etc.
COPY . .

# Railway injects $PORT; default 8000 for local docker run.
EXPOSE 8000

# Single worker — SSE streams are stateful per session.
# Use shell form so $PORT expands at runtime.
CMD uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
