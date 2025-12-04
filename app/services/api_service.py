import httpx
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional

load_dotenv()

API_URL = os.getenv("API_URL")

class ApiService:
    @staticmethod
    async def fetch_earthquakes(
        sort: str = "datetime_desc",
        epicenter: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        from_magnitude: Optional[str] = None,
        to_magnitude: Optional[str] = None,
        from_depth: Optional[str] = None,
        to_depth: Optional[str] = None,
        from_latitude: Optional[str] = None,
        to_latitude: Optional[str] = None,
        from_longitude: Optional[str] = None,
        to_longitude: Optional[str] = None,
        uzb: int = 0,
        per_page: int = 10,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Fetch earthquakes data from the external API
        """
        params = {
            "sort": sort,
            "epicenter": epicenter or "",
            "from_date": from_date or "",
            "to_date": to_date or "",
            "from_magnitude": from_magnitude or "",
            "to_magnitude": to_magnitude or "",
            "from_depth": from_depth or "",
            "to_depth": to_depth or "",
            "from_latitude": from_latitude or "",
            "to_latitude": to_latitude or "",
            "from_longitude": from_longitude or "",
            "to_longitude": to_longitude or "",
            "uzb": uzb,
            "per_page": per_page,
            "page": page
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(API_URL, params=params)
            response.raise_for_status()
            return response.json()
