"""
FastAPI entry point.

Run from the backend/ directory:
    uv run uvicorn app.main:app --reload --port 8000

Verify it's up:
    curl http://localhost:8000/health
    # → {"status":"ok","env":"dev"}

Defines:
- `app` — the FastAPI instance uvicorn loads
- CORS — allow requests from the chrome extension
- `/health` — sanity-check route (no logic, returns OK)
- Lifespan — runs once at startup / once at shutdown
  (setup logging now; later: warm Chroma client, load XGBoost model, etc.)

API routes themselves live in `app/api/routes/` (Group 2C — not yet created).
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import ask_why, counter, mirror, perceive, perceive_text, stream
from app.config import settings
from app.core.logging import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Run once on startup, then once on shutdown (after `yield`)."""
    setup_logging()
    logger.info("Freewall backend starting (env=%s)", settings.env)
    # TODO (Phase 1): warm Chroma client, load XGBoost model
    yield
    logger.info("Freewall backend shutting down")


app = FastAPI(
    title="Freewall Backend",
    version="0.1.0",
    description="Multi-agent cognitive defense backend.",
    lifespan=lifespan,
)

# CORS — Vercel demo site + localhost dev + Chrome extension (Path B optional).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Override FastAPI's default HTTPException response shape.

    Default behavior wraps everything in `{"detail": ...}`. Our wire contract
    (docs/API_CONTRACTS.md) specifies `{"error": {"code", "message"}}` for
    all non-2xx responses — so when route handlers raise
    `HTTPException(detail={"error": {...}})`, we unwrap one layer here.

    For other detail shapes (FastAPI's own validation errors, plain strings),
    fall through to the default `{"detail": ...}` shape.
    """
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/health")
async def health() -> dict[str, str]:
    """Sanity check. `curl localhost:8000/health` to verify backend is up."""
    return {"status": "ok", "env": settings.env}


# Wire route modules. Each router carries its own prefix (defined in the route file).
app.include_router(perceive.router)
app.include_router(perceive_text.router)
app.include_router(stream.router)
app.include_router(ask_why.router)
app.include_router(counter.router)
app.include_router(mirror.router)
