from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import io
import zipfile
import json
from app.db.database import get_db
from app.services.earthquake_service import EarthquakeService
from app.services.api_service import ApiService
from app.schemas.earthquake import Earthquake, EarthquakeCreate, EarthquakeUpdate, EarthquakeResponse

router = APIRouter()

@router.get("/", response_model=EarthquakeResponse)
async def read_earthquakes(
    db: Session = Depends(get_db),
    skip: int = Query(0, alias="page", ge=0),
    limit: int = Query(10, alias="per_page", ge=1, le=30000),
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
    from_year: Optional[int] = Query(None),
    to_year: Optional[int] = Query(None),
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
        from_year=from_year,
        to_year=to_year,
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

@router.get("/all", response_model=List[Earthquake])
def get_all_earthquakes(db: Session = Depends(get_db)):
    """
    Get all earthquakes without any filters or pagination
    Returns complete list of all earthquakes in the database
    """
    return EarthquakeService.get_all_earthquakes_simple(db)

@router.get("/statistics/by-year")
def get_statistics_by_year(db: Session = Depends(get_db)):
    """
    Get earthquake count grouped by year
    Returns: [{"year": "2024", "count": 150}, ...]
    """
    return EarthquakeService.get_earthquakes_by_year(db)

@router.get("/statistics/by-month")
def get_statistics_by_month(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None, description="Filter by specific year")
):
    """
    Get earthquake count grouped by month
    Optional year parameter to filter by specific year
    Returns: [{"year": "2024", "month": "12", "count": 25}, ...]
    """
    return EarthquakeService.get_earthquakes_by_month(db, year)

@router.get("/statistics/magnitude-by-month")
def get_magnitude_statistics_by_month(
    db: Session = Depends(get_db),
    from_year: Optional[int] = Query(None, description="Start year for filtering"),
    to_year: Optional[int] = Query(None, description="End year for filtering")
):
    """
    Get highest (maximum) magnitude grouped by year and month for chart visualization
    Returns data suitable for multi-line chart (like the example with 2023, 2024, 2025)
    Shows the strongest earthquake in each month
    
    Example: /earthquakes/statistics/magnitude-by-month?from_year=2023&to_year=2025
    
    Returns: [
        {"year": "2023", "month": "01", "max_magnitude": 4.5, "count": 10},
        {"year": "2023", "month": "02", "max_magnitude": 4.3, "count": 15},
        ...
    ]
    """
    return EarthquakeService.get_magnitude_statistics_by_month(db, from_year, to_year)

@router.get("/statistics/count-by-month")
def get_count_statistics_by_month(
    db: Session = Depends(get_db),
    from_year: Optional[int] = Query(None, description="Start year for filtering"),
    to_year: Optional[int] = Query(None, description="End year for filtering")
):
    """
    Get earthquake count grouped by year and month for chart visualization
    Returns data suitable for multi-line chart (like the example with 2023, 2024, 2025)
    Perfect for showing earthquake frequency trends over time
    
    Example: /earthquakes/statistics/count-by-month?from_year=2023&to_year=2025
    
    Returns: [
        {"year": "2023", "month": "01", "count": 25},
        {"year": "2023", "month": "02", "count": 30},
        {"year": "2024", "month": "01", "count": 28},
        ...
    ]
    """
    return EarthquakeService.get_count_statistics_by_month(db, from_year, to_year)

@router.get("/coordinates")
def get_all_coordinates(db: Session = Depends(get_db)):
    """
    Get all earthquake coordinates with metadata for shapefile/GIS export
    Returns ALL earthquakes with their coordinates and key attributes
    Suitable for creating shapefiles, GeoJSON, or other GIS formats
    
    Example: /earthquakes/coordinates
    
    Returns: [
        {
            "id": 1,
            "latitude": 41.2995,
            "longitude": 69.2401,
            "magnitude": 4.5,
            "depth": 10.0,
            "date": "15.03.2024",
            "time": "14:30:00",
            "epicenter": "Tashkent region",
            "earthquake_id": "EQ123456"
        },
        ...
    ]
    """
    return EarthquakeService.get_all_coordinates(db)

@router.get("/geojson")
def get_geojson_coordinates(db: Session = Depends(get_db)):
    """
    Get all earthquake coordinates in GeoJSON format for shapefile export
    GeoJSON is the standard format for GIS data and can be directly imported into:
    - QGIS (drag and drop)
    - ArcGIS
    - Google Earth
    - Mapbox
    - Or converted to shapefile using: ogr2ogr -f "ESRI Shapefile" output.shp input.geojson
    
    Example: /earthquakes/geojson
    
    Returns GeoJSON FeatureCollection:
    {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [69.2401, 41.2995]
                },
                "properties": {
                    "id": 1,
                    "earthquake_id": "EQ123456",
                    "date": "15.03.2024",
                    "time": "14:30:00",
                    "magnitude": 4.5,
                    "depth": 10.0,
                    "epicenter": "Tashkent region",
                    ...
                }
            }
        ]
    }
    """
    return EarthquakeService.get_geojson_coordinates(db)

@router.get("/download/geojson")
def download_geojson(db: Session = Depends(get_db)):
    """
    Download all earthquake data as a GeoJSON file
    This endpoint returns a downloadable .geojson file that can be:
    - Imported directly into QGIS, ArcGIS, Google Earth
    - Converted to shapefile using ogr2ogr
    
    Example: /earthquakes/download/geojson
    """
    geojson_data = EarthquakeService.get_geojson_coordinates(db)
    
    # Convert to JSON string
    geojson_string = json.dumps(geojson_data, ensure_ascii=False, indent=2)
    
    # Create file-like object
    file_like = io.BytesIO(geojson_string.encode('utf-8'))
    
    return StreamingResponse(
        file_like,
        media_type="application/geo+json",
        headers={
            "Content-Disposition": "attachment; filename=earthquakes.geojson"
        }
    )

@router.get("/download/shapefile")
def download_shapefile_zip(db: Session = Depends(get_db)):
    """
    Download all earthquake data as a zipped shapefile package
    Returns a ZIP file containing:
    - earthquakes.geojson (can be converted to shapefile)
    - README.txt (instructions for conversion)
    
    The GeoJSON file can be:
    1. Directly imported into QGIS (drag and drop)
    2. Converted to shapefile using: ogr2ogr -f "ESRI Shapefile" earthquakes.shp earthquakes.geojson
    
    Example: /earthquakes/download/shapefile
    """
    geojson_data = EarthquakeService.get_geojson_coordinates(db)
    
    # Create a ZIP file in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add GeoJSON file
        geojson_string = json.dumps(geojson_data, ensure_ascii=False, indent=2)
        zip_file.writestr('earthquakes.geojson', geojson_string)
        
        # Add README with instructions
        readme_content = """Earthquake Data - Shapefile Package
=====================================

This package contains earthquake data in GeoJSON format.

FILES:
------
- earthquakes.geojson : Earthquake data in GeoJSON format

HOW TO USE:
-----------

Option 1: Import to QGIS (Easiest)
1. Open QGIS
2. Drag and drop 'earthquakes.geojson' into QGIS
3. Done!

Option 2: Convert to Shapefile
Run this command:
  ogr2ogr -f "ESRI Shapefile" earthquakes.shp earthquakes.geojson

This will create:
- earthquakes.shp (geometry)
- earthquakes.shx (index)
- earthquakes.dbf (attributes)
- earthquakes.prj (projection)

Option 3: Import to ArcGIS
1. Open ArcGIS Pro
2. Add Data -> Data from Path
3. Select 'earthquakes.geojson'
4. Right-click layer -> Export Features -> Shapefile

COORDINATE SYSTEM:
------------------
WGS84 (EPSG:4326)
Coordinates: [longitude, latitude]

ATTRIBUTES:
-----------
- id: Database ID
- earthquake_id: External earthquake ID
- date: Date (DD.MM.YYYY)
- time: Time (HH:MM:SS)
- magnitude: Earthquake magnitude
- depth: Depth in km
- epicenter: Epicenter location
- magnitude_type: Type of magnitude
- color: Color code for visualization

For more information, visit: http://localhost:8005/docs
"""
        zip_file.writestr('README.txt', readme_content)
    
    # Reset buffer position
    zip_buffer.seek(0)
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=earthquakes_shapefile.zip"
        }
    )

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
