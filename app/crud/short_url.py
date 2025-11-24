from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.short_url import ShortURL
from app.utils.code_generator import generate_code

async def create_short_url(
    db: AsyncSession,
    original_url: str,
    ttl_seconds: int | None = None,
    custom_alias: str | None = None
) -> ShortURL:

    # Check if alias is available
    if custom_alias:
        existing = await db.execute(
            select(ShortURL).where(ShortURL.custom_alias == custom_alias)
        )
        if existing.scalar_one_or_none():
            raise ValueError("Alias already in use")

    # Generate a unique short code with limited retries to avoid collisions
    max_attempts = 5
    short_code = None
    for _ in range(max_attempts):
        candidate = generate_code()
        existing_code = await db.execute(
            select(ShortURL).where(ShortURL.short_code == candidate)
        )
        if not existing_code.scalar_one_or_none():
            short_code = candidate
            break
    if short_code is None:
        raise ValueError("Failed to generate a unique short code; please retry")

    # Calculate expiration
    expires_at = None
    if ttl_seconds:
        expires_at = datetime.now() + timedelta(seconds=ttl_seconds)

    short_url = ShortURL(
        original_url=str(original_url),# Ensure original_url is stored as a string
        short_code=short_code,
        custom_alias=custom_alias,
        expires_at=expires_at
    )

    db.add(short_url)
    await db.commit()
    await db.refresh(short_url)
    return short_url


def get_access_code(short_url: ShortURL) -> str:
    """Use alias if available; otherwise use generated short_code."""
    if short_url.custom_alias:
        return short_url.custom_alias
    return short_url.short_code

async def get_short_url(db: AsyncSession, code: str) -> ShortURL | None:
    """Find by either short_code or custom_alias."""
    result = await db.execute(
        select(ShortURL).where(
            or_(
                ShortURL.short_code == code,
                ShortURL.custom_alias == code
            )
        )
    )
    return result.scalar_one_or_none()
