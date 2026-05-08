"""
Common FastAPI dependencies for routes in `app/api/routes/`.

Currently empty. This module reserves the import path. As we add cross-cutting
concerns, put them here:

- Rate limiters (per-IP / per-session)
- Request-trace context (request_id propagation for logs)
- Auth (post-MVP — none in hackathon)

Routes import from here as:
    from app.api.deps import some_dep
"""

from __future__ import annotations
