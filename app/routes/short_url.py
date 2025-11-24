from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.short_url import ShortenRequest, ShortenResponse
from app.crud.short_url import create_short_url, get_access_code
from app.core.database import get_db
from app.core.rate_limiter import rate_limit
from app.core.config import BASE_URL

router = APIRouter(prefix="/shorten", tags=["Shortener"])


@router.post("", response_model=ShortenResponse)
async def create_shortener(
    payload: ShortenRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    # Apply rate limit
    client_ip = request.client.host
    rate_limit(client_ip)

    try:
        short_url = await create_short_url(
            db=db,
            original_url=payload.original_url,
            ttl_seconds=payload.ttl_seconds,
            custom_alias=payload.custom_alias
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    access_code = get_access_code(short_url)
    final_url = f"{BASE_URL}/{access_code}"

    return ShortenResponse(short_url=final_url)
