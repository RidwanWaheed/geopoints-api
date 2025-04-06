from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from geojson_pydantic import Point as GeoJSONPoint

from app.schemas.category import Category


# Shared properties
class PointBase(BaseModel):
    name: str
    description: Optional[str] = None

# Properties to receive on point creation
class PointCreate(PointBase):
    latitude: float
    longitude: float
    category_id: Optional[int] = None

# Properties to receive on point update
class PointUpdate(PointBase):
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category_id: Optional[int] = None

# Properties shared by models stored in DB
class PointInDBBase(PointBase):
    id: int
    category_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

# Properties to return to client
class Point(PointInDBBase):
    coordinates: GeoJSONPoint
    category: Optional[Category] = None

# Additional properties for nearby points
class NearbyPoint(Point):
    distance: float


