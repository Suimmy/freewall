"""
Logging setup. Call `setup_logging()` once at app startup (lifespan in main.py).

Other modules do `import logging; logger = logging.getLogger(__name__)` —
they don't need to know about this file.
"""

from __future__ import annotations

import logging
import sys

from app.config import settings


def setup_logging() -> None:
    """Configure root logger. Idempotent — safe to call multiple times."""
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    root = logging.getLogger()
    # Strip any existing handlers (e.g., uvicorn's defaults) so format is consistent.
    for h in root.handlers[:]:
        root.removeHandler(h)

    handler = logging.StreamHandler(sys.stdout)
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    root.addHandler(handler)
    root.setLevel(level)

    # Quiet down noisy libs — they spam DEBUG/INFO that drowns ours.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.INFO)
