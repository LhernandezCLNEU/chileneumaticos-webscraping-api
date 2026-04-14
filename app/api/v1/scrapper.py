from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db
from app.models.title_format import TitleFormat
from app.schemas.title_format import TitleFormatCreate, TitleFormatRead, TitleFormatUpdate

router = APIRouter()


@router.get("/scrapper", response_model=TitleFormatRead)
async def get_title_format(item_id: int, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(TitleFormat).where(TitleFormat.id == item_id))
    item = q.scalars().first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TitleFormat not found")
    return item
