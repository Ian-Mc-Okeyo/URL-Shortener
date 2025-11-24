from sqlalchemy import Column, String, Integer, DateTime, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime

class ShortURL(Base):
    __tablename__ = "short_urls"

    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String, unique=True, index=True)
    original_url = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.now)
    expires_at = Column(TIMESTAMP, nullable=True)
    custom_alias = Column(String, unique=True, nullable=True)
