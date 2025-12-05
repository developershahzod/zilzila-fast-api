from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.services.earthquake_service import EarthquakeService
from app.services.api_service import ApiService
from app.schemas.earthquake import Earthquake, EarthquakeCreate, EarthquakeUpdate, EarthquakeResponse

router = APIRouter()

@router.get("/", response_model=EarthquakeResponse)
async def read_earthquakes(
    db: Session = Depends(get_db),
    skip: int = Query(0, alias="page", ge=0),
    limit: int = Query(10, alias="per_page", ge=1, le=10000),
    epicenter: Optional[str] = Query(None),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    from_magnitude: Optional[str] = Query(None),
    to_magnitude: Optional[str] = Query(None),
    from_depth: Optional[str] = Query(None),
    to_depth: Optional[str] = Query(None),
    from_latitude: Optional[str] = Query(None),
    to_latitude: Optional[str] = Query(None),
    from_longitude: Optional[str] = Query(None),
    to_longitude: Optional[str] = Query(None),
    sort: str = Query("datetime_desc")
):
    # Convert empty/whitespace strings to None and parse magnitude values
    from_mag = None
    to_mag = None
    
    if from_magnitude and from_magnitude.strip():
        try:
            from_mag = float(from_magnitude)
        except ValueError:
            pass
    
    if to_magnitude and to_magnitude.strip():
        try:
            to_mag = float(to_magnitude)
        except ValueError:
            pass
    
    earthquakes, total = EarthquakeService.get_earthquakes(
        db, 
        skip=skip * limit, 
        limit=limit,
        epicenter=epicenter,
        from_date=from_date,
        to_date=to_date,
        from_magnitude=from_mag,
        to_magnitude=to_mag,
        from_depth=from_depth,
        to_depth=to_depth,
        from_latitude=from_latitude,
        to_latitude=to_latitude,
        from_longitude=from_longitude,
        to_longitude=to_longitude,
        sort=sort
    )
    
    last_page = (total + limit - 1) // limit if limit > 0 else 0
    
    return {
        "data": earthquakes,
        "total": total,
        "page": skip + 1,
        "per_page": limit,
        "last_page": last_page
    }

@router.get("/{earthquake_id}", response_model=Earthquake)
def read_earthquake(earthquake_id: int, db: Session = Depends(get_db)):
    db_earthquake = EarthquakeService.get_earthquake(db, earthquake_id=earthquake_id)
    if db_earthquake is None:
        raise HTTPException(status_code=404, detail="Earthquake not found")
    return db_earthquake

@router.post("/", response_model=Earthquake)
def create_earthquake(earthquake: EarthquakeCreate, db: Session = Depends(get_db)):
    return EarthquakeService.create_earthquake(db=db, earthquake=earthquake)

@router.put("/{earthquake_id}", response_model=Earthquake)
def update_earthquake(earthquake_id: int, earthquake: EarthquakeUpdate, db: Session = Depends(get_db)):
    db_earthquake = EarthquakeService.update_earthquake(db, earthquake_id=earthquake_id, earthquake=earthquake)
    if db_earthquake is None:
        raise HTTPException(status_code=404, detail="Earthquake not found")
    return db_earthquake

@router.delete("/{earthquake_id}")
def delete_earthquake(earthquake_id: int, db: Session = Depends(get_db)):
    success = EarthquakeService.delete_earthquake(db, earthquake_id=earthquake_id)
    if not success:
        raise HTTPException(status_code=404, detail="Earthquake not found")
    return {"detail": "Earthquake deleted successfully"}

@router.post("/sync")
async def sync_earthquakes(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(100, ge=1, le=100)
):
    try:
        # Fetch data from external API
        api_data = await ApiService.fetch_earthquakes(page=page, per_page=per_page)
        
        # Extract earthquake data from the result object
        result = api_data.get("result", {})
        earthquakes_data = result.get("data", [])
        
        # Save to database
        if earthquakes_data:
            earthquakes, skipped = EarthquakeService.bulk_create_earthquakes(db, earthquakes_data)
            return {
                "detail": f"Successfully synced {len(earthquakes)} earthquakes, skipped {skipped} duplicates",
                "total_synced": len(earthquakes),
                "total_skipped": skipped,
                "total_processed": len(earthquakes_data)
            }
        else:
            return {"detail": "No earthquakes found to sync"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync earthquakes: {str(e)}")
