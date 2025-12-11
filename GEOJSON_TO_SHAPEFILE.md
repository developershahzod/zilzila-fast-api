# GeoJSON to Shapefile Conversion Guide

## New API Endpoint

### GET `/api/earthquakes/geojson`
Returns all earthquake data in GeoJSON format, ready for GIS applications.

**Example:**
```
http://localhost:8005/api/earthquakes/geojson
```

## How to Use

### Option 1: Direct Import to QGIS (Easiest)

1. Download the GeoJSON file:
   ```bash
   curl http://localhost:8005/api/earthquakes/geojson -o earthquakes.geojson
   ```

2. Open QGIS

3. Drag and drop `earthquakes.geojson` into QGIS

4. Done! The layer will appear on your map

### Option 2: Convert to Shapefile using ogr2ogr

```bash
# Download GeoJSON
curl http://localhost:8005/api/earthquakes/geojson -o earthquakes.geojson

# Convert to Shapefile
ogr2ogr -f "ESRI Shapefile" earthquakes.shp earthquakes.geojson

# This creates:
# - earthquakes.shp (geometry)
# - earthquakes.shx (index)
# - earthquakes.dbf (attributes)
# - earthquakes.prj (projection)
```

### Option 3: Using Python (geopandas)

```python
import geopandas as gpd
import requests

# Fetch GeoJSON from API
response = requests.get('http://localhost:8005/api/earthquakes/geojson')
geojson_data = response.json()

# Convert to GeoDataFrame
gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])

# Save as Shapefile
gdf.to_file('earthquakes.shp')

# Or save as other formats
gdf.to_file('earthquakes.gpkg', driver='GPKG')  # GeoPackage
gdf.to_file('earthquakes.geojson', driver='GeoJSON')  # GeoJSON
```

### Option 4: Using ArcGIS

1. Download GeoJSON file
2. Open ArcGIS Pro
3. Go to: **Map** → **Add Data** → **Data from Path**
4. Select the `.geojson` file
5. Right-click layer → **Data** → **Export Features** → Choose "Shapefile"

## GeoJSON Format

The API returns standard GeoJSON with:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [longitude, latitude]
      },
      "properties": {
        "id": 1,
        "earthquake_id": "EQ123456",
        "date": "15.03.2024",
        "time": "14:30:00",
        "magnitude": 4.5,
        "depth": 10.0,
        "epicenter": "Tashkent region",
        "magnitude_type": "mb",
        "color": "#ff0000",
        "is_perceptabily": true
      }
    }
  ]
}
```

## Attributes Included

- `id` - Database ID
- `earthquake_id` - External earthquake ID
- `date` - Date (DD.MM.YYYY)
- `time` - Time (HH:MM:SS)
- `magnitude` - Earthquake magnitude
- `depth` - Depth in km
- `epicenter` - Epicenter location
- `epicenter_ru` - Epicenter (Russian)
- `epicenter_en` - Epicenter (English)
- `magnitude_type` - Type of magnitude (mb, ML, etc.)
- `color` - Color code for visualization
- `is_perceptabily` - Whether earthquake was felt

## Coordinate System

- **Format:** WGS84 (EPSG:4326)
- **Coordinates:** [longitude, latitude] (GeoJSON standard)
- **Units:** Decimal degrees

## Tools Required

### Install ogr2ogr (GDAL)

**macOS:**
```bash
brew install gdal
```

**Ubuntu/Debian:**
```bash
sudo apt-get install gdal-bin
```

**Windows:**
Download from: https://gdal.org/download.html

### Install Python packages

```bash
pip install geopandas requests
```
