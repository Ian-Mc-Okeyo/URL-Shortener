from pydantic import BaseModel, HttpUrl
from typing import Optional

class ShortenRequest(BaseModel):
    original_url: HttpUrl
    ttl_seconds: Optional[int] = None
    custom_alias: Optional[str] = None

class ShortenResponse(BaseModel):
    short_url: str
