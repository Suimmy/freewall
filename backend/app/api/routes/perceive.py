"""
POST /perceive — L1 ingest endpoint.

Extension content script sends one PerceptionPayload (one content unit
entering viewport). We acknowledge with 202 immediately and queue the
L2 reasoning pipeline as a background task. Results stream back via
GET /stream/{session_id} as SSE events.

Wire shape: shared/schemas/perception.json
Stub: validates request body, logs, returns 202. No real pipeline yet.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks, status
from pydantic import BaseModel, Field

from app.schemas.perception import PerceptionPayload
from app.services import orchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/perceive", tags=["perceive"])


class PerceiveResponse(BaseModel):
    status: str = Field(default="queued", description="'queued' | 'cached'")
    content_id: str


@router.post("", status_code=status.HTTP_202_ACCEPTED, response_model=PerceiveResponse)
async def perceive(
    payload: PerceptionPayload,
    background_tasks: BackgroundTasks,
) -> PerceiveResponse:
    """
    Receive one content unit. Schedule L2 pipeline. Return immediately.

    202 Accepted means "we have your data, will process async". The actual
    reasoning events stream over SSE on /stream/{session_id}.
    """
    logger.info(
        "perceive received: session=%s content=%s url=%s category=%s",
        payload.session_id,
        payload.content_id,
        payload.url,
        payload.content.category,
    )

    # TODO (Phase 4): Check cache.get(content_id) — if present, replay cached events
    # to SSE and return PerceiveResponse(status="cached", content_id=...).
    # For now, always queue the pipeline.

    # mode='json' converts UUID/AnyUrl/datetime → strings so orchestrator's dict-based
    # internals + cache JSON serialization work without surprise.
    background_tasks.add_task(orchestrator.run_pipeline, payload.model_dump(mode="json"))

    return PerceiveResponse(content_id=payload.content_id)
