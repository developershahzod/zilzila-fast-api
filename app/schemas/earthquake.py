from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EarthquakeBase(BaseModel):
    date: str
    time: str
    latitude: str
    longitude: str
    depth: str
    magnitude: float
    color: str
    epicenter: str
    description: Optional[str] = None
    is_influence: Optional[bool] = None
    seisprog_id: Optional[int] = None
    is_perceptabily: bool = False
    magnitude_type: Optional[str] = None
    epicenter_ru: Optional[str] = None
    epicenter_en: Optional[str] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

class EarthquakeCreate(EarthquakeBase):
    pass

class EarthquakeUpdate(BaseModel):
    date: Optional[str] = None
    time: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    depth: Optional[str] = None
    magnitude: Optional[float] = None
    color: Optional[str] = None
    epicenter: Optional[str] = None
    description: Optional[str] = None
    is_influence: Optional[bool] = None
    seisprog_id: Optional[int] = None
    is_perceptabily: Optional[bool] = None
    magnitude_type: Optional[str] = None
    epicenter_ru: Optional[str] = None
    epicenter_en: Optional[str] = None
    updated_by: Optional[int] = None

class Earthquake(EarthquakeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    earthquake_id: Optional[int] = None

    class Config:
        orm_mode = True

class EarthquakeResponse(BaseModel):
    data: list[Earthquake]
    total: int
    page: int
    per_page: int
    last_page: int
