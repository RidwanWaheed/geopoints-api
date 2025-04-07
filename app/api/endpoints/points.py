from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.dependencies import get_db
from app.api.deps import get_point_service
from app.services.point import PointService
from app.schemas.pagination import PagedResponse, PageParams
from app.schemas.point import Point, PointCreate, PointUpdate, NearbyPoint


router = APIRouter()

@router.post("/", response_model=Point, status_code=status.HTTP_201_CREATED)
def create_point(
    *,
    point_in: PointCreate,
    db: Session = Depends(get_db),
    service: PointService = Depends(get_point_service)
):
     """Create a new point"""
     return service.create(db=db, obj_in=point_in)

@router.get("/", response_model=PagedResponse[Point])
def read_points(
     *,
     pagination: PageParams = Depends(),
     category_id: Optional[int] = None,
     db: Session = Depends(get_db),
     service: PointService = Depends(get_point_service)
):
     """Retrieve points with optional category filter and pagination"""
     # Get total count
     total = service.count(db=db, category_id=category_id)

     # Get paginated items
     items = service.get_multi(
         db=db,
         skip=(pagination.page - 1) * pagination.limit,
         limit=pagination.limit,
         category_id=category_id
         )
     
     # Return paginated response
     return PagedResponse.create(
         items=items,
         total=total,
         page=pagination.page,
         limit=pagination.limit
     )

@router.get("/nearby", response_model=List[NearbyPoint])
def get_nearby_points(
     *,
     lat: float = Query(..., ge=-90, le=90),
     lng: float = Query(..., ge=-180, le=180),
     radius: float = Query(..., ge=0, le=100000),
     limit: int = Query(100, ge=1, le=1000),
     db: Session = Depends(get_db),
     service: PointService = Depends(get_point_service)
):
      """Get points within a radius of a location"""
      return service.get_nearby(db=db, lat=lat, lng=lng, radius=radius, limit=limit)

@router.get("/{point_id}", response_model=Point)
def read_point(
     *,
     point_id: int,
     db: Session = Depends(get_db),
     service: PointService = Depends(get_point_service)
):
      """Get a specific point by id"""
      point = service.get(db=db, id=point_id)
      if not point:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Point not found"
        )
      return point

@router.put("/{point_id}", response_model=Point)
def update_point(
     *,
     point_id: int,
     point_in: PointUpdate,
     db: Session = Depends(get_db),
     service: PointService = Depends(get_point_service)
):
      """Update a point"""
      point = service.get(db=db, id=point_id)
      if not point:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Point not found"
        )
      return service.update(db=db, db_obj=point, obj_in=point_in)

@router.delete("/{point_id}", response_model=Point)
def delete_point(
     *,
     point_id: int,
     db: Session = Depends(get_db),
     service: PointService = Depends(get_point_service)
):
      """Delete a point"""
      point = service.get(db=db, id=point_id)
      if not point:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Point not found"
        )
      return service.remove(db=db, id=point_id)

@router.post("/within", response_model=List[Point])
def get_points_within_polygon(
    *,
    polygon: str = Query(..., description="WKT polygon string"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    service: PointService = Depends(get_point_service)
):
    """Get points within a polygon boundary"""
    return service.get_within_polygon(db=db, polygon=polygon, limit=limit)

@router.get("/nearest", response_model=List[NearbyPoint])
def get_nearest_points(
    *,
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    limit: int = Query(5, ge=1, le=100),
    db: Session = Depends(get_db),
    service: PointService = Depends(get_point_service)
):
    """Get the nearest points to a location"""
    return service.get_nearest(db=db, lat=lat, lng=lng, limit=limit)