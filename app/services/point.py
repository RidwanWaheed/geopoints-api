from typing import List, Optional

from geoalchemy2.shape import to_shape
from geojson_pydantic import Point as GeoJSONPoint
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.point import Point
from app.repositories.point import PointRepository
from app.schemas.point import NearbyPoint
from app.schemas.point import Point as PointSchema
from app.schemas.point import PointCreate, PointUpdate
from app.spatial.utils import point_to_geojson


class PointService:
    def __init__(self, repository: PointRepository):
        self.repository = repository

    def create(self, db: Session, *, obj_in: PointCreate) -> PointSchema:
        """Create a new point"""
        db_obj = self.repository.create_with_coords(db=db, obj_in=obj_in)

        # Convert SQLAlchemy model to a dictionary
        db_dict = {c.name: getattr(db_obj, c.name) for c in db_obj.__table__.columns}

        # Convert geometry to GeoJSON format and add to dictionary
        db_dict["coordinates"] = point_to_geojson(db_obj.geometry)

        # Remove geometry as it's not in the Pydantic schema
        db_dict.pop("geometry", None)

        # Add category if available
        if db_obj.category:
            db_dict["category"] = {
                "id": db_obj.category.id,
                "name": db_obj.category.name,
                "description": db_obj.category.description,
                "color": db_obj.category.color,
            }

        # Create Pydantic model
        return PointSchema(**db_dict)

    def get(self, db: Session, *, id: int) -> Optional[PointSchema]:
        """Get point by ID"""
        db_obj = self.repository.get(db=db, id=id)
        if not db_obj:
            return None

        # Convert to dict and add coordinates
        db_dict = {c.name: getattr(db_obj, c.name) for c in db_obj.__table__.columns}
        db_dict["coordinates"] = point_to_geojson(db_obj.geometry)
        db_dict.pop("geometry", None)

        # Add category if available
        if db_obj.category:
            db_dict["category"] = {
                "id": db_obj.category.id,
                "name": db_obj.category.name,
                "description": db_obj.category.description,
                "color": db_obj.category.color,
            }

        return PointSchema(**db_dict)

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None
    ) -> List[PointSchema]:
        """Get multiple points with optional category filter"""
        if category_id:
            db_objs = self.repository.get_by_category(
                db=db, category_id=category_id, skip=skip, limit=limit
            )
        else:
            db_objs = self.repository.get_multi(db=db, skip=skip, limit=limit)

        results = []
        for db_obj in db_objs:
            # Convert to dict and add coordinates
            db_dict = {
                c.name: getattr(db_obj, c.name) for c in db_obj.__table__.columns
            }
            db_dict["coordinates"] = point_to_geojson(db_obj.geometry)
            db_dict.pop("geometry", None)

            # Add category if available
            if db_obj.category:
                db_dict["category"] = {
                    "id": db_obj.category.id,
                    "name": db_obj.category.name,
                    "description": db_obj.category.description,
                    "color": db_obj.category.color,
                }

            results.append(PointSchema(**db_dict))

        return results

    def update(self, db: Session, *, db_obj: Point, obj_in: PointUpdate) -> PointSchema:
        """Update a point"""
        updated_obj = self.repository.update(db=db, db_obj=db_obj, obj_in=obj_in)

        # Convert to dict and add coordinates
        db_dict = {
            c.name: getattr(updated_obj, c.name) for c in updated_obj.__table__.columns
        }
        db_dict["coordinates"] = point_to_geojson(updated_obj.geometry)
        db_dict.pop("geometry", None)

        # Add category if available
        if updated_obj.category:
            db_dict["category"] = {
                "id": updated_obj.category.id,
                "name": updated_obj.category.name,
                "description": updated_obj.category.description,
                "color": updated_obj.category.color,
            }

        return PointSchema(**db_dict)

    def remove(self, db: Session, *, id: int) -> PointSchema:
        """Remove a point"""
        db_obj = self.repository.remove(db=db, id=id)

        # Convert to dict and add coordinates
        db_dict = {c.name: getattr(db_obj, c.name) for c in db_obj.__table__.columns}
        db_dict["coordinates"] = point_to_geojson(db_obj.geometry)
        db_dict.pop("geometry", None)

        # Add category if available
        if db_obj.category:
            db_dict["category"] = {
                "id": db_obj.category.id,
                "name": db_obj.category.name,
                "description": db_obj.category.description,
                "color": db_obj.category.color,
            }

        return PointSchema(**db_dict)

    def get_nearby(
        self, db: Session, *, lat: float, lng: float, radius: float, limit: int = 100
    ) -> List[NearbyPoint]:
        """Get points within a specified radius of a location"""
        results = []
        point_tuples = self.repository.get_nearby(
            db=db, lat=lat, lng=lng, radius=radius, limit=limit
        )

        for point_obj, distance in point_tuples:
            # Convert to dict and add coordinates
            point_dict = {
                c.name: getattr(point_obj, c.name) for c in point_obj.__table__.columns
            }
            point_dict["coordinates"] = point_to_geojson(point_obj.geometry)
            point_dict.pop("geometry", None)

            # Add category if available
            if point_obj.category:
                point_dict["category"] = {
                    "id": point_obj.category.id,
                    "name": point_obj.category.name,
                    "description": point_obj.category.description,
                    "color": point_obj.category.color,
                }

            # Add distance
            point_dict["distance"] = distance

            # Create NearbyPoint
            results.append(NearbyPoint(**point_dict))

        return results

    def count(self, db: Session, *, category_id: Optional[int] = None) -> int:
        """Count total points with optional category filter"""
        query = db.query(func.count(Point.id))
        if category_id:
            query = query.filter(Point.category_id == category_id)
        return query.scalar()

    # Add these methods to your app/services/point.py file

    def get_within_polygon(
        self, db: Session, *, polygon: str, limit: int = 100
    ) -> List[PointSchema]:
        """Get points within a polygon defined in WKT format"""
        # Query points using PostGIS ST_Within
        point_objs = self.repository.get_within_polygon(
            db=db, polygon=polygon, limit=limit
        )

        results = []
        for point_obj in point_objs:
            # Convert to dict and add coordinates
            point_dict = {
                c.name: getattr(point_obj, c.name) for c in point_obj.__table__.columns
            }
            point_dict["coordinates"] = point_to_geojson(point_obj.geometry)
            point_dict.pop("geometry", None)

            # Add category if available
            if point_obj.category:
                point_dict["category"] = {
                    "id": point_obj.category.id,
                    "name": point_obj.category.name,
                    "description": point_obj.category.description,
                    "color": point_obj.category.color,
                }

            results.append(PointSchema(**point_dict))

        return results

    def get_nearest(
        self, db: Session, *, lat: float, lng: float, limit: int = 5
    ) -> List[NearbyPoint]:
        """Get the nearest points to a location"""
        results = []
        point_tuples = self.repository.get_nearest(db=db, lat=lat, lng=lng, limit=limit)

        for point_obj, distance in point_tuples:
            # Convert to dict and add coordinates
            point_dict = {
                c.name: getattr(point_obj, c.name) for c in point_obj.__table__.columns
            }
            point_dict["coordinates"] = point_to_geojson(point_obj.geometry)
            point_dict.pop("geometry", None)

            # Add category if available
            if point_obj.category:
                point_dict["category"] = {
                    "id": point_obj.category.id,
                    "name": point_obj.category.name,
                    "description": point_obj.category.description,
                    "color": point_obj.category.color,
                }

            # Add distance
            point_dict["distance"] = distance

            # Create NearbyPoint
            results.append(NearbyPoint(**point_dict))

        return results
