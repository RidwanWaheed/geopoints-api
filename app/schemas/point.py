from datetime import datetime
from typing import Optional

from geojson_pydantic import Point as GeoJSONPoint
from pydantic import BaseModel, Field

from app.schemas.category import Category


class PointBase(BaseModel):
    name: str = Field(
        ...,
        description="Name of the point of interest",
        example="Berlin Cathedral",
        min_length=1,
        max_length=100,
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of the point",
        example="Historic cathedral in Berlin city center",
    )


class PointCreate(PointBase):
    latitude: float = Field(
        ...,
        description="Latitude coordinate in WGS84",
        example=52.5192,
        ge=-90.0,
        le=90.0,
    )
    longitude: float = Field(
        ...,
        description="Longitude coordinate in WGS84",
        example=13.4016,
        ge=-180.0,
        le=180.0,
    )
    category_id: Optional[int] = Field(
        None, description="ID of the associated category", example=3, ge=1
    )


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
