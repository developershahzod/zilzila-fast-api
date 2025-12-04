from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.db.database import Base

class Earthquake(Base):
    __tablename__ = "earthquakes"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, index=True)
    time = Column(String)
    latitude = Column(String)
    longitude = Column(String)
    depth = Column(String)
    magnitude = Column(Float)
    color = Column(String)
    epicenter = Column(String)
    description = Column(Text, nullable=True)
    is_influence = Column(Boolean, nullable=True)
    seisprog_id = Column(Integer, nullable=True)
    is_perceptabily = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    earthquake_id = Column(Integer, nullable=True, unique=True, index=True)
    magnitude_type = Column(String, nullable=True)
    epicenter_ru = Column(String, nullable=True)
    epicenter_en = Column(String, nullable=True)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
