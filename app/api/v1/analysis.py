from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, HttpUrl
import json

from app.services.scrape_service import service as scrape_service
from typing import Optional
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_db
from app.models.parsed_result import ParsedResult
from app.models.product import Product
from app.schemas.parsed_result import ParsedResultRead
from app.core.ws import manager

router = APIRouter()


class AnalysisRequest(BaseModel):
    urls: List[HttpUrl]
    callback_url: Optional[HttpUrl] = None


class AnalysisResponse(BaseModel):
    task_id: str


@router.post("/analysis/run", response_model=AnalysisResponse)
async def run_analysis(req: AnalysisRequest):
    if not req.urls:
        raise HTTPException(status_code=400, detail="No urls provided")

    urls = [str(u) for u in req.urls]
    task_id = scrape_service.launch(urls, callback_url=str(req.callback_url) if req.callback_url else None)
    return {"task_id": task_id}


@router.get("/analysis/status/{task_id}")
async def analysis_status(task_id: str):
    return scrape_service.status(task_id)


@router.get("/analysis/results", response_model=list[ParsedResultRead])
async def analysis_results(product_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    """Return parsed results from the database. Optionally filter by product_id."""
    q = select(ParsedResult)
    if product_id:
        q = q.where(ParsedResult.product_id == product_id)

    res = await db.execute(q.order_by(ParsedResult.parsed_at.desc()))
    items = res.scalars().all()
    return items


@router.post("/analysis/callback")
async def analysis_callback(payload: dict):
    """Webhook endpoint: receives callback from scrape service and broadcasts via WebSocket."""
    # basic validation
    task_id = payload.get("task_id")
    result = payload.get("result")
    if not task_id:
        raise HTTPException(status_code=400, detail="task_id required")

    # broadcast to connected websocket clients
    try:
        await manager.broadcast({"type": "task_completed", "task_id": task_id, "result": result})
    except Exception:
        # do not fail on websocket broadcast errors
        pass

    return {"ok": True}


@router.websocket("/analysis/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for clients to receive task notifications.

    Clients can connect and will receive messages of the form:
    {"type": "task_completed", "task_id": "...", "result": [...]}
    """
    await manager.connect(websocket)
    try:
        while True:
            # keep connection alive; optionally accept client pings/commands
            try:
                data = await websocket.receive_text()
                # ignore or echo
                await websocket.send_text(json.dumps({"type": "pong", "data": data}))
            except WebSocketDisconnect:
                break
            except Exception:
                # ignore other receive errors and continue
                continue
    finally:
        manager.disconnect(websocket)
