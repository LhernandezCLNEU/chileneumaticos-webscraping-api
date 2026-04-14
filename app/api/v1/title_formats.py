from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db
from app.models.title_format import TitleFormat
from app.schemas.title_format import TitleFormatCreate, TitleFormatRead, TitleFormatUpdate

router = APIRouter()


@router.post("/title-formats", response_model=TitleFormatRead)
async def create_title_format(payload: TitleFormatCreate, db: AsyncSession = Depends(get_db)):
    tf = TitleFormat(**payload.model_dump())
    db.add(tf)
    await db.commit()
    await db.refresh(tf)
    return tf


@router.get("/title-formats", response_model=List[TitleFormatRead])
async def list_title_formats(db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(TitleFormat).order_by(TitleFormat.priority.desc()))
    items = q.scalars().all()
    return items


@router.get("/title-formats/{item_id}", response_model=TitleFormatRead)
async def get_title_format(item_id: int, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(TitleFormat).where(TitleFormat.id == item_id))
    item = q.scalars().first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TitleFormat not found")
    return item


@router.put("/title-formats/{item_id}", response_model=TitleFormatRead)
async def update_title_format(item_id: int, payload: TitleFormatUpdate, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(TitleFormat).where(TitleFormat.id == item_id))
    item = q.scalars().first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TitleFormat not found")

    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(item, k, v)

    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/title-formats/{item_id}")
async def delete_title_format(item_id: int, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(TitleFormat).where(TitleFormat.id == item_id))
    item = q.scalars().first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TitleFormat not found")
    item.enabled = False
    db.add(item)
    await db.commit()
    return {"ok": True}
