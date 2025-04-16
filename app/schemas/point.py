from datetime import datetime
from typing import Optional

from geojson_pydantic import Point as GeoJSONPoint
from pydantic import BaseModel

from app.schemas.category import Category


class PointBase(BaseModel):
    name: str
    description: Optional[str] = None


class PointCreate(PointBase):
    latitude: float
    longitude: float
    category_id: Optional[int] = None


class PointUpdate(PointBase):
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category_id: Optional[int] = None


class PointInDBBase(PointBase):
    id: int
    category_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class Point(PointInDBBase):
    coordinates: GeoJSONPoint
    category: Optional[Category] = None


class NearbyPoint(Point):
    distance: float
