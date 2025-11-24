from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.short_url import ShortURL
from app.models.click import Click
from app.crud.click import get_analytics

router = APIRouter(prefix="/analytics")

@router.get("/{code}")
async def get_analytics_route(
    code: str,
    db: AsyncSession = Depends(get_db)
):
    analytics = await get_analytics(code, db)
    return analytics