from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, HttpUrl

from app.services.scrape_service import service as scrape_service
from typing import Optional
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_db
from app.models.parsed_result import ParsedResult
from app.models.product import Product
from app.schemas.parsed_result import ParsedResultRead

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
