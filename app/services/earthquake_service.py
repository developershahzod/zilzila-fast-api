from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.models.earthquake import Earthquake
from app.schemas.earthquake import EarthquakeCreate, EarthquakeUpdate
from datetime import datetime
from typing import List, Optional, Dict, Any

class EarthquakeService:
    @staticmethod
    def get_earthquakes(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        epicenter: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        from_magnitude: Optional[float] = None,
        to_magnitude: Optional[float] = None,
        from_depth: Optional[str] = None,
        to_depth: Optional[str] = None,
        from_latitude: Optional[str] = None,
        to_latitude: Optional[str] = None,
        from_longitude: Optional[str] = None,
        to_longitude: Optional[str] = None,
        sort: str = "datetime_desc"
    ):
        query = db.query(Earthquake)
        
        if epicenter:
            query = query.filter(Earthquake.epicenter.ilike(f"%{epicenter}%"))
        
        if from_date:
            query = query.filter(Earthquake.date >= from_date)
        
        if to_date:
            query = query.filter(Earthquake.date <= to_date)
        
        if from_magnitude is not None:
            query = query.filter(Earthquake.magnitude >= from_magnitude)
        
        if to_magnitude is not None:
            query = query.filter(Earthquake.magnitude <= to_magnitude)
        
        if from_depth:
            query = query.filter(Earthquake.depth >= from_depth)
        
        if to_depth:
            query = query.filter(Earthquake.depth <= to_depth)
        
        if from_latitude:
            query = query.filter(Earthquake.latitude >= from_latitude)
        
        if to_latitude:
            query = query.filter(Earthquake.latitude <= to_latitude)
        
        if from_longitude:
            query = query.filter(Earthquake.longitude >= from_longitude)
        
        if to_longitude:
            query = query.filter(Earthquake.longitude <= to_longitude)
        
        total = query.count()
        
        # Convert date from DD.MM.YYYY to YYYY-MM-DD format for proper sorting
        # Using PostgreSQL string functions: substring and concatenation
        date_converted = func.concat(
            func.substring(Earthquake.date, 7, 4),  # Year (YYYY)
            '.',
            func.substring(Earthquake.date, 4, 2),  # Month (MM)
            '.',
            func.substring(Earthquake.date, 1, 2)   # Day (DD)
        )
        
        # Apply sorting based on sort parameter
        if sort == "datetime_asc":
            query = query.order_by(date_converted.asc(), Earthquake.time.asc())
        else:  # datetime_desc (default)
            query = query.order_by(date_converted.desc(), Earthquake.time.desc())
        
        earthquakes = query.offset(skip).limit(limit).all()
        
        return earthquakes, total

    @staticmethod
    def get_earthquake(db: Session, earthquake_id: int):
        return db.query(Earthquake).filter(Earthquake.id == earthquake_id).first()

    @staticmethod
    def create_earthquake(db: Session, earthquake: EarthquakeCreate):
        now = datetime.now()
        db_earthquake = Earthquake(
            **earthquake.dict(),
            created_at=now,
            updated_at=now
        )
        db.add(db_earthquake)
        db.commit()
        db.refresh(db_earthquake)
        return db_earthquake

    @staticmethod
    def update_earthquake(db: Session, earthquake_id: int, earthquake: EarthquakeUpdate):
        db_earthquake = db.query(Earthquake).filter(Earthquake.id == earthquake_id).first()
        if db_earthquake:
            update_data = earthquake.dict(exclude_unset=True)
            update_data["updated_at"] = datetime.now()
            
            for key, value in update_data.items():
                setattr(db_earthquake, key, value)
            
            db.commit()
            db.refresh(db_earthquake)
        return db_earthquake

    @staticmethod
    def delete_earthquake(db: Session, earthquake_id: int):
        db_earthquake = db.query(Earthquake).filter(Earthquake.id == earthquake_id).first()
        if db_earthquake:
            db.delete(db_earthquake)
            db.commit()
            return True
        return False

    @staticmethod
    def bulk_create_earthquakes(db: Session, earthquakes_data: List[Dict[str, Any]]):
        now = datetime.now()
        earthquakes = []
        skipped = 0
        
        for data in earthquakes_data:
            # Get the external API's earthquake ID
            external_id = data.get("id")
            
            # Check if earthquake already exists by external ID
            if external_id:
                existing = db.query(Earthquake).filter(Earthquake.earthquake_id == external_id).first()
                if existing:
                    skipped += 1
                    continue
            
            # Convert keys to snake_case if they are in camelCase
            if "createdBy" in data:
                data["created_by"] = data.pop("createdBy")
            if "updatedBy" in data:
                data["updated_by"] = data.pop("updatedBy")
            
            # Store the external ID in earthquake_id field
            if "id" in data:
                data["earthquake_id"] = data.pop("id")
            
            # Remove created_at and updated_at from data if they exist
            data.pop("created_at", None)
            data.pop("updated_at", None)
                
            # Create earthquake object
            earthquake = Earthquake(
                **data,
                created_at=now,
                updated_at=now
            )
            earthquakes.append(earthquake)
        
        if earthquakes:
            db.add_all(earthquakes)
            db.commit()
        
        return earthquakes, skipped
