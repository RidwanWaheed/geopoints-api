from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_active_user,
    get_current_superuser,
    get_point_service,
)
from app.models.user import User
from app.schemas.pagination import PagedResponse, PageParams
from app.schemas.point import NearbyPoint, Point, PointCreate, PointUpdate
from app.services.point import PointService

router = APIRouter()


@router.post("/", response_model=Point, status_code=status.HTTP_201_CREATED)
def create_point(
    point_in: PointCreate,
    current_user: User = Depends(get_current_active_user),
    service: PointService = Depends(get_point_service),
):
    return service.create_point(point_in=point_in)


@router.get("/", response_model=PagedResponse[Point])
def read_points(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    service: PointService = Depends(get_point_service),
):
    page_params = PageParams(page=page, limit=limit)

    return service.get_points(page_params=page_params, category_id=category_id)


@router.get("/nearby", response_model=List[NearbyPoint])
def get_nearby_points(
    lat: float = Query(..., ge=-90, le=90, description="Latitude coordinate"),
    lng: float = Query(..., ge=-180, le=180, description="Longitude coordinate"),
    radius: float = Query(..., gt=0, le=100000, description="Search radius in meters"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    service: PointService = Depends(get_point_service),
):
    return service.get_nearby_points(lat=lat, lng=lng, radius=radius, limit=limit)


@router.post("/within", response_model=List[Point])
def get_points_within_polygon(
    polygon_wkt: str = Query(..., description="WKT polygon string"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    service: PointService = Depends(get_point_service),
):
    return service.get_points_within_polygon(polygon_wkt=polygon_wkt, limit=limit)


@router.get("/nearest", response_model=List[NearbyPoint])
def get_nearest_points(
    lat: float = Query(..., ge=-90, le=90, description="Latitude coordinate"),
    lng: float = Query(..., ge=-180, le=180, description="Longitude coordinate"),
    limit: int = Query(5, ge=1, le=100, description="Maximum number of results"),
    service: PointService = Depends(get_point_service),
):
    return service.get_nearest_points(lat=lat, lng=lng, limit=limit)


@router.get("/{point_id}", response_model=Point)
def read_point(point_id: int, service: PointService = Depends(get_point_service)):
    return service.get_point(point_id=point_id)


@router.put("/{point_id}", response_model=Point)
def update_point(
    point_id: int,
    point_in: PointUpdate,
    current_user: User = Depends(get_current_active_user),
    service: PointService = Depends(get_point_service),
):
    return service.update_point(point_id=point_id, point_in=point_in)


@router.delete("/{point_id}", response_model=Point)
def delete_point(
    point_id: int,
    current_user: User = Depends(get_current_superuser),
    service: PointService = Depends(get_point_service),
):
    return service.delete_point(point_id=point_id)
