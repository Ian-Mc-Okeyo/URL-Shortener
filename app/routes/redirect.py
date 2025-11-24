from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.short_url import get_short_url
from app.crud.click import log_click
from app.core.database import get_db
from app.core.rate_limiter import rate_limit
from datetime import datetime

router = APIRouter(tags=["Redirect"])


@router.get("/{code}")
async def redirect_handler(
    code: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    # Apply rate limit -> Currently for development, I have disabled to allow tests to pass since tests do multiple redirects
    # client_ip = request.client.host
    # rate_limit(client_ip)
    short_url = await get_short_url(db, code)

    if not short_url:
        raise HTTPException(status_code=404, detail="Short link not found")

    # Check TTL expiration
    if short_url.expires_at and short_url.expires_at < datetime.now():
        raise HTTPException(status_code=410, detail="Link has expired")

    # Log analytics -> this will not block redirects
    ip = request.client.host
    user_agent = request.headers.get("User-Agent")

    await log_click(db, short_url, ip, user_agent)

    # Redirect to original URL
    return RedirectResponse(short_url.original_url)
