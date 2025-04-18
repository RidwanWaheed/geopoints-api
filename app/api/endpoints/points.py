from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_active_user,
    get_current_superuser,
    get_point_service,
)
from app.core.exceptions import NotFoundException
from app.models.user import User
from app.schemas.pagination import PagedResponse, PageParams
from app.schemas.point import NearbyPoint, Point, PointCreate, PointUpdate
from app.services.point import PointService

router = APIRouter()


@router.post("/", response_model=Point, status_code=status.HTTP_201_CREATED)
def create_point(
    *,
    point_in: PointCreate,
    current_user: User = Depends(get_current_active_user),
    service: PointService = Depends(get_point_service),
):
    """Create a new point"""
    return service.create(obj_in=point_in)


@router.get("/", response_model=PagedResponse[Point])
def read_points(
    *,
    pagination: PageParams = Depends(),
    category_id: Optional[int] = None,
    service: PointService = Depends(get_point_service),
):
    """Retrieve points with optional category filter and pagination"""
    # Get total count
    total = service.count(category_id=category_id)

    # Get paginated items
    items = service.get_multi(
        skip=(pagination.page - 1) * pagination.limit,
        limit=pagination.limit,
        category_id=category_id,
    )

    # Return paginated response
    return PagedResponse.create(
        items=items, total=total, page=pagination.page, limit=pagination.limit
    )


@router.get("/nearby", response_model=List[NearbyPoint])
def get_nearby_points(
    *,
    lat: float = Query(..., ge=-90, le=90, description="Latitude coordinate"),
    lng: float = Query(..., ge=-180, le=180, description="Longitude coordinate"),
    radius: float = Query(..., gt=0, le=100000, description="Search radius in meters"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    service: PointService = Depends(get_point_service),
):
    """
    Get points within a specified radius of a location.

    - **lat**: Latitude coordinate in WGS84 (between -90 and 90)
    - **lng**: Longitude coordinate in WGS84 (between -180 and 180)
    - **radius**: Search radius in meters (up to 100km)
    - **limit**: Maximum number of results to return (default: 100)
    """
    return service.get_nearby(lat=lat, lng=lng, radius=radius, limit=limit)


@router.post("/within", response_model=List[Point])
def get_points_within_polygon(
    *,
    polygon: str = Query(..., description="WKT polygon string"),
    limit: int = Query(100, ge=1, le=1000),
    service: PointService = Depends(get_point_service),
):
    """Get points within a polygon boundary"""
    return service.get_within_polygon(polygon=polygon, limit=limit)


@router.get("/nearest", response_model=List[NearbyPoint])
def get_nearest_points(
    *,
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    limit: int = Query(5, ge=1, le=100),
    service: PointService = Depends(get_point_service),
):
    """Get the nearest points to a location"""
    return service.get_nearest(lat=lat, lng=lng, limit=limit)


@router.get("/{point_id}", response_model=Point)
def read_point(*, point_id: int, service: PointService = Depends(get_point_service)):
    """Get a specific point by id"""
    point = service.get(id=point_id)
    if not point:
        raise NotFoundException(detail=f"Point with id {point_id} not found")

    return point


@router.put("/{point_id}", response_model=Point)
def update_point(
    *,
    point_id: int,
    current_user: User = Depends(get_current_active_user),
    point_in: PointUpdate,
    service: PointService = Depends(get_point_service),
):
    """Update a point"""

    # Get the database model instance
    updated_point = service.update(id=point_id, obj_in=point_in)
    if not updated_point:
        raise NotFoundException(detail=f"Point with id {point_id} not found")

    return updated_point


@router.delete("/{point_id}", response_model=Point)
def delete_point(
    *,
    point_id: int,
    current_user: User = Depends(get_current_superuser),
    service: PointService = Depends(get_point_service),
):
    """Delete a point (requires superuser privileges)"""
    point = service.get(id=point_id)
    if not point:
        raise NotFoundException(detail=f"Point with id {point_id} not found")

    return service.remove(id=point_id)
