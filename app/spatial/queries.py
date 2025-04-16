# app/spatial/queries.py
from typing import List, Tuple, TypeVar

from geoalchemy2.shape import from_shape
from shapely.geometry import Point as ShapelyPoint
from sqlalchemy import func
from sqlalchemy.orm import Query

from app.core.constants import SpatialRefSys

ModelType = TypeVar("ModelType")


def point_to_ewkb(lat: float, lng: float):
    """Convert lat/lng to PostGIS EWKB format"""
    shapely_point = ShapelyPoint(lng, lat)
    return from_shape(shapely_point, srid=SpatialRefSys.WGS84)


def add_distance_to_query(query: Query, model_class, source_geom) -> Query:
    """
    Add a distance calculation to a query

    Args:
        query: SQLAlchemy query
        model_class: Model with geometry field
        source_geom: Source geometry to measure distance from

    Returns:
        Query with distance column added
    """
    return query.add_columns(
        func.ST_Distance(
            func.ST_Transform(model_class.geometry, SpatialRefSys.WEB_MERCATOR),
            func.ST_Transform(source_geom, SpatialRefSys.WEB_MERCATOR),
        ).label("distance")
    )


def filter_by_distance(query: Query, model_class, source_geom, radius: float) -> Query:
    """
    Filter a query by distance using ST_DWithin

    Args:
        query: SQLAlchemy query
        model_class: Model with geometry field
        source_geom: Source geometry to measure distance from
        radius: Distance in meters

    Returns:
        Filtered query
    """
    return query.filter(
        func.ST_DWithin(
            func.ST_Transform(model_class.geometry, SpatialRefSys.WEB_MERCATOR),
            func.ST_Transform(source_geom, SpatialRefSys.WEB_MERCATOR),
            radius,
        )
    )
