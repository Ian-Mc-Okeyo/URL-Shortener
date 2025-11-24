from pydantic import BaseModel, HttpUrl
from typing import Optional

class ShortenRequest(BaseModel):
    original_url: HttpUrl
    ttl_seconds: Optional[int] = None
    custom_alias: Optional[str] = None
    variant_url: Optional[HttpUrl] = None  # secondary URL for A/B testing
    split_percent: Optional[int] = None    # percentage of traffic to primary (0-100)

class ShortenResponse(BaseModel):
    short_url: str
