# app/spatial/queries.py
from typing import List, Tuple, TypeVar

from geoalchemy2.elements import WKBElement
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


def add_distance_to_query(query: Query, model_class, point_geom: WKBElement) -> Query:
    """
    Add a distance calculation to a query using ST_Distance_Sphere for better performance

    Args:
        query: SQLAlchemy query
        model_class: Model with geometry field
        point_geom: Source geometry to measure distance from

    Returns:
        Query with distance column added in meters
    """
    # Use ST_Distance_Sphere instead of transforming to Web Mercator
    # This is faster and accurate enough for most use cases
    return query.add_columns(
        func.ST_DistanceSphere(model_class.geometry, point_geom).label("distance")
    )


def filter_by_distance(
    query: Query, model_class, point_geom: WKBElement, radius: float
) -> Query:
    """
    Filter a query by distance using ST_DWithin with spheroid calculations

    Args:
        query: SQLAlchemy query
        model_class: Model with geometry field
        point_geom: Source geometry to measure distance from
        radius: Distance in meters

    Returns:
        Filtered query
    """
    # Use a geography cast for proper distance calculations over curved earth
    # This ensures accurate results regardless of location on the globe
    return query.filter(
        func.ST_DWithin(
            func.ST_Transform(model_class.geometry, SpatialRefSys.GEOGRAPHY),
            func.ST_Transform(point_geom, SpatialRefSys.GEOGRAPHY),
            radius,
        )
    )


def nearest_neighbor_query(query: Query, model_class, point_geom: WKBElement) -> Query:
    """
    Optimize query for nearest neighbor search using KNN GiST index with distance_centroid.

    Args:
        query: SQLAlchemy query
        model_class: Model with geometry field
        point_geom: Source geometry to find nearest points from

    Returns:
        Query optimized for KNN search
    """
    # The <-> operator with distance_centroid uses PostgreSQL's KNN GiST index,
    # which is highly optimized for nearest-neighbor searches, especially for point geometries.
    # This method is much faster than ST_Distance for large datasets due to efficient index utilization.
    return query.order_by(model_class.geometry.distance_centroid(point_geom))
