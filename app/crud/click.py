from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.models.short_url import ShortURL
from app.models.click import Click
from app.utils.bot_detector import is_bot


async def log_click(
    db: AsyncSession,
    short_url: ShortURL,
    ip: str,
    user_agent: str | None,
):
    bot_flag = is_bot(user_agent)
    click = Click(
        short_url_id=short_url.id,
        ip_address=ip,
        user_agent=user_agent,
        is_bot=bot_flag,
    )
    db.add(click)
    await db.commit()

# get analytics
async def get_analytics(code: str, db: AsyncSession):
    """Return analytics for a short code or custom alias.
    Includes total clicks, first/last timestamps, and user-agent breakdown.
    """
    # Find the URL by short_code OR custom_alias
    query = select(ShortURL).where(
        or_(ShortURL.short_code == code, ShortURL.custom_alias == code)
    )
    result = await db.execute(query)
    url = result.scalar_one_or_none()

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    # Total clicks
    total_clicks_query = select(func.count()).select_from(Click).where(
        Click.short_url_id == url.id
    )
    total_clicks = (await db.execute(total_clicks_query)).scalar() or 0

    # First and last click timestamps
    first_click_query = select(func.min(Click.timestamp)).where(Click.short_url_id == url.id)
    last_click_query = select(func.max(Click.timestamp)).where(Click.short_url_id == url.id)
    first_click = (await db.execute(first_click_query)).scalar()
    last_click = (await db.execute(last_click_query)).scalar()

    # User-Agent breakdown
    ua_query = (
        select(Click.user_agent, func.count())
        .where(Click.short_url_id == url.id)
        .group_by(Click.user_agent)
    )
    ua_rows = await db.execute(ua_query)
    user_agents = {row[0] if row[0] is not None else "Unknown": row[1] for row in ua_rows.all()}

    # Bot vs human counts
    bot_count_query = select(func.count()).select_from(Click).where(
        Click.short_url_id == url.id, Click.is_bot == True  # noqa: E712
    )
    bot_clicks = (await db.execute(bot_count_query)).scalar() or 0
    human_clicks = total_clicks - bot_clicks

    return {
        "short_code": code,
        "original_url": url.original_url,
        "total_clicks": total_clicks,
        "human_clicks": human_clicks,
        "bot_clicks": bot_clicks,
        "first_click": first_click,
        "last_click": last_click,
        "user_agents": user_agents,
    }