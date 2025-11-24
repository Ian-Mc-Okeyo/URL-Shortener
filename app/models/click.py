from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime

class Click(Base):
    __tablename__ = "clicks"

    id = Column(Integer, primary_key=True)
    short_url_id = Column(Integer, ForeignKey("short_urls.id"))
    user_agent = Column(String)
    ip_address = Column(String)
    timestamp = Column(TIMESTAMP, default=datetime.now)
    is_bot = Column(Boolean, default=False)