# app/spatial/queries.py
from typing import List, Tuple, TypeVar

from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import from_shape
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
    Add a distance calculation to a query using direct geography casting
    """
    # Cast directly to geography for accurate Earth distance calculation
    return query.add_columns(
        func.ST_Distance(
            cast(func.geography(model_class.geometry), "geography"),
            cast(func.geography(point_geom), "geography")
        ).label("distance")
    )

def filter_by_distance(
    query: Query, model_class, point_geom: WKBElement, radius: float
) -> Query:
    """
    Filter a query by distance using ST_DWithin with geography casting
    """
    # Use geography type casts for proper distance calculations
    return query.filter(
        func.ST_DWithin(
            cast(func.geography(model_class.geometry), "geography"),
            cast(func.geography(point_geom), "geography"),
            radius
        )
    )

def nearest_neighbor_query(query: Query, model_class, point_geom: WKBElement) -> Query:
    """
    Optimize query for nearest neighbor search using KNN GiST index
    """
    # The <-> operator is the KNN distance operator
    return query.order_by(model_class.geometry.distance_centroid(point_geom))
