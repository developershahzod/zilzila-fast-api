from fastapi import APIRouter
from app.api.endpoints import earthquakes

api_router = APIRouter()
api_router.include_router(earthquakes.router, prefix="/earthquakes", tags=["earthquakes"])
