from fastapi import HTTPException
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.short_url import ShortURL
from app.models.click import Click


async def log_click(
    db: AsyncSession,
    short_url: ShortURL,
    ip: str,
    user_agent: str | None,
):
    click = Click(
        short_url_id=short_url.id,
        ip_address=ip,
        user_agent=user_agent,
    )
    db.add(click)
    await db.commit()

# get analytics
async def get_analytics(code: str, db: AsyncSession):
    # Find the URL
    query = select(ShortURL).where(ShortURL.short_code == code)
    result = await db.execute(query)
    url = result.scalar_one_or_none()

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    # Count visits
    count_query = select(func.count()).select_from(Click).where(
        Click.short_url_id == url.id
    )
    total_clicks = (await db.execute(count_query)).scalar()

    # Last visit
    last_visit_query = select(Click.timestamp).where(
        Click.short_url_id == url.id
    ).order_by(Click.timestamp.desc()).limit(1)

    last_visit = (await db.execute(last_visit_query)).scalar()

    # All visits
    visits_query = select(Click).where(
        Click.short_url_id == url.id
    ).order_by(Click.timestamp.desc())

    visits = (await db.execute(visits_query)).scalars().all()

    return {
        "short_code": code,
        "original_url": url.original_url,
        "total_clicks": total_clicks,
        "last_visit": last_visit,
        "visits": [
            {
                "visited_at": v.timestamp,
                "user_agent": v.user_agent,
                "ip_address": v.ip_address
            }
            for v in visits
        ]
    }