# app/spatial/queries.py
from typing import List, Tuple, TypeVar

from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import from_shape
from geoalchemy2.types import Geography
from shapely.geometry import Point as ShapelyPoint
from sqlalchemy import cast, func
from sqlalchemy.orm import Query

from app.core.constants import SpatialRefSys

ModelType = TypeVar("ModelType")


def point_to_ewkb(lat: float, lng: float):
    """Convert lat/lng to PostGIS EWKB format"""
    shapely_point = ShapelyPoint(lng, lat)
    return from_shape(shapely_point, srid=SpatialRefSys.WGS84)


def add_distance_to_query(query: Query, model_class, point_geom: WKBElement) -> Query:
    """
    Add a distance calculation to a query using Geography type
    """

    # Ensure model's geometry is treated as Geography
    model_geom_geog = cast(model_class.geometry, Geography)

    # Cast the input point_geom to Geography
    point_geom_geog = cast(func.ST_GeomFromEWKB(point_geom), Geography)

    return query.add_columns(
        func.ST_Distance(model_geom_geog, point_geom_geog).label("distance")
    )


def filter_by_distance(
    query: Query, model_class, point_geom: WKBElement, radius: float
) -> Query:
    """
    Filter a query by distance using ST_DWithin with Geography
    """
    model_geom_geog = cast(model_class.geometry, Geography)
    point_geom_geog = cast(func.ST_GeomFromEWKB(point_geom), Geography)

    return query.filter(func.ST_DWithin(model_geom_geog, point_geom_geog, radius))


def nearest_neighbor_query(query: Query, model_class, point_geom: WKBElement) -> Query:
    """
    Optimize query for nearest neighbor search using KNN <-> operator and Geography
    """
    model_geom_geog = cast(model_class.geometry, Geography)
    point_geom_geog = cast(func.ST_GeomFromEWKB(point_geom), Geography)

    # The <-> operator is the KNN distance operator, now on Geography
    return query.order_by(model_geom_geog.distance_centroid(point_geom_geog))
