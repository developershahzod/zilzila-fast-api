from sqlalchemy.orm import Session
from sqlalchemy import func, case, Integer
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
        from_year: Optional[int] = None,
        to_year: Optional[int] = None,
        sort: str = "datetime_desc"
    ):
        query = db.query(Earthquake)
        
        if epicenter:
            query = query.filter(Earthquake.epicenter.ilike(f"%{epicenter}%"))
        
        # Convert date from DD.MM.YYYY to YYYY.MM.DD format for proper comparison
        date_converted_for_filter = func.concat(
            func.substring(Earthquake.date, 7, 4),  # Year (YYYY)
            '.',
            func.substring(Earthquake.date, 4, 2),  # Month (MM)
            '.',
            func.substring(Earthquake.date, 1, 2)   # Day (DD)
        )
        
        if from_date:
            # Convert from_date from DD.MM.YYYY to YYYY.MM.DD
            from_date_parts = from_date.split('.')
            if len(from_date_parts) == 3:
                from_date_converted = f"{from_date_parts[2]}.{from_date_parts[1]}.{from_date_parts[0]}"
                query = query.filter(date_converted_for_filter >= from_date_converted)
        
        if to_date:
            # Convert to_date from DD.MM.YYYY to YYYY.MM.DD
            to_date_parts = to_date.split('.')
            if len(to_date_parts) == 3:
                to_date_converted = f"{to_date_parts[2]}.{to_date_parts[1]}.{to_date_parts[0]}"
                query = query.filter(date_converted_for_filter <= to_date_converted)
        
        if from_magnitude is not None:
            query = query.filter(Earthquake.magnitude >= from_magnitude)
        
        if to_magnitude is not None:
            query = query.filter(Earthquake.magnitude <= to_magnitude)
        
        if from_depth is not None:
            query = query.filter(Earthquake.depth >= from_depth)
        
        if to_depth is not None:
            query = query.filter(Earthquake.depth <= to_depth)
        
        if from_latitude is not None:
            query = query.filter(Earthquake.latitude >= from_latitude)
        
        if to_latitude is not None:
            query = query.filter(Earthquake.latitude <= to_latitude)
        
        if from_longitude is not None:
            query = query.filter(Earthquake.longitude >= from_longitude)
        
        if to_longitude is not None:
            query = query.filter(Earthquake.longitude <= to_longitude)
        
        # Year filter - extract year from date field (DD.MM.YYYY format)
        if from_year is not None:
            year_from_date = func.substring(Earthquake.date, 7, 4)
            query = query.filter(func.cast(year_from_date, Integer) >= from_year)
        
        if to_year is not None:
            year_from_date = func.substring(Earthquake.date, 7, 4)
            query = query.filter(func.cast(year_from_date, Integer) <= to_year)
        
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

    @staticmethod
    def get_earthquakes_by_year(db: Session):
        """
        Get earthquake count grouped by year
        Returns list of {year: str, count: int} ordered by year desc
        """
        # Extract year from date field (DD.MM.YYYY format, year is at position 7-10)
        year_expr = func.substring(Earthquake.date, 7, 4)
        
        results = db.query(
            year_expr.label('year'),
            func.count(Earthquake.id).label('count')
        ).group_by(year_expr).order_by(year_expr.desc()).all()
        
        return [{"year": row.year, "count": row.count} for row in results]

    @staticmethod
    def get_earthquakes_by_month(db: Session, year: Optional[int] = None):
        """
        Get earthquake count grouped by month
        If year is provided, filter by that year
        Returns list of {year: str, month: str, count: int} ordered by year desc, month desc
        """
        # Extract year and month from date field (DD.MM.YYYY format)
        year_expr = func.substring(Earthquake.date, 7, 4)
        month_expr = func.substring(Earthquake.date, 4, 2)
        
        query = db.query(
            year_expr.label('year'),
            month_expr.label('month'),
            func.count(Earthquake.id).label('count')
        )
        
        # Filter by year if provided
        if year is not None:
            query = query.filter(func.cast(year_expr, Integer) == year)
        
        results = query.group_by(year_expr, month_expr).order_by(
            year_expr.desc(), 
            month_expr.desc()
        ).all()
        
        return [{"year": row.year, "month": row.month, "count": row.count} for row in results]

    @staticmethod
    def get_magnitude_statistics_by_month(db: Session, from_year: Optional[int] = None, to_year: Optional[int] = None):
        """
        Get highest magnitude grouped by year and month for chart visualization
        Returns data suitable for multi-line chart with years as separate lines
        Format: [{"year": "2023", "month": "01", "max_magnitude": 4.5, "count": 10}, ...]
        """
        # Extract year and month from date field (DD.MM.YYYY format)
        year_expr = func.substring(Earthquake.date, 7, 4)
        month_expr = func.substring(Earthquake.date, 4, 2)
        
        query = db.query(
            year_expr.label('year'),
            month_expr.label('month'),
            func.max(Earthquake.magnitude).label('max_magnitude'),
            func.count(Earthquake.id).label('count')
        )
        
        # Filter by year range if provided
        if from_year is not None:
            query = query.filter(func.cast(year_expr, Integer) >= from_year)
        
        if to_year is not None:
            query = query.filter(func.cast(year_expr, Integer) <= to_year)
        
        results = query.group_by(year_expr, month_expr).order_by(
            year_expr.asc(), 
            month_expr.asc()
        ).all()
        
        return [{
            "year": row.year, 
            "month": row.month, 
            "max_magnitude": round(float(row.max_magnitude), 2) if row.max_magnitude else 0,
            "count": row.count
        } for row in results]

    @staticmethod
    def get_count_statistics_by_month(db: Session, from_year: Optional[int] = None, to_year: Optional[int] = None):
        """
        Get earthquake count grouped by year and month for chart visualization
        Returns data suitable for multi-line chart with years as separate lines
        Format: [{"year": "2023", "month": "01", "count": 25}, ...]
        """
        # Extract year and month from date field (DD.MM.YYYY format)
        year_expr = func.substring(Earthquake.date, 7, 4)
        month_expr = func.substring(Earthquake.date, 4, 2)
        
        query = db.query(
            year_expr.label('year'),
            month_expr.label('month'),
            func.count(Earthquake.id).label('count')
        )
        
        # Filter by year range if provided
        if from_year is not None:
            query = query.filter(func.cast(year_expr, Integer) >= from_year)
        
        if to_year is not None:
            query = query.filter(func.cast(year_expr, Integer) <= to_year)
        
        results = query.group_by(year_expr, month_expr).order_by(
            year_expr.asc(), 
            month_expr.asc()
        ).all()
        
        return [{
            "year": row.year, 
            "month": row.month, 
            "count": row.count
        } for row in results]
