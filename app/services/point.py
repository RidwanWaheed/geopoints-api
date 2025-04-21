# app/services/point_service.py
from typing import List, Optional, Tuple

from fastapi import HTTPException, status

from app.core.exceptions import BadRequestException, NotFoundException
from app.core.utils import point_to_geojson
from app.repositories.category import CategoryRepository
from app.repositories.point import PointRepository
from app.schemas.pagination import PagedResponse, PageParams
from app.schemas.point import NearbyPoint
from app.schemas.point import Point as PointSchema
from app.schemas.point import PointCreate, PointUpdate


class PointService:

    def __init__(
        self, point_repository: PointRepository, category_repository: CategoryRepository
    ):
        self.point_repository = point_repository
        self.category_repository = category_repository

    def create_point(self, *, point_in: PointCreate) -> PointSchema:
        if point_in.category_id:
            category = self.category_repository.get(id=point_in.category_id)
            if not category:
                raise BadRequestException(
                    detail=f"Category with ID {point_in.category_id} not found"
                )

        point = self.point_repository.create_with_coordinates(
            name=point_in.name,
            description=point_in.description,
            latitude=point_in.latitude,
            longitude=point_in.longitude,
            category_id=point_in.category_id,
        )

        return self._point_to_schema(point)

    def get_point(self, *, point_id: int) -> PointSchema:
        point = self.point_repository.get(id=point_id)
        if not point:
            raise NotFoundException(detail=f"Point with ID {point_id} not found")

        return self._point_to_schema(point)

    def get_points(
        self, *, page_params: PageParams, category_id: Optional[int] = None
    ) -> PagedResponse[PointSchema]:

        # Calculate pagination offset
        skip = (page_params.page - 1) * page_params.limit

        # Get total count for pagination
        if category_id:
            total = self.point_repository.count_by_category(category_id=category_id)
        else:
            total = self.point_repository.count()

        # Get points based on parameters
        if category_id:
            points = self.point_repository.get_by_category(
                category_id=category_id, skip=skip, limit=page_params.limit
            )
        else:
            points = self.point_repository.get_multi(skip=skip, limit=page_params.limit)

        # Transform to schemas
        point_schemas = [self._point_to_schema(p) for p in points]

        # Create paginated response
        return PagedResponse.create(
            items=point_schemas,
            total=total,
            page=page_params.page,
            limit=page_params.limit,
        )

    def update_point(self, *, point_id: int, point_in: PointUpdate) -> PointSchema:
        # Get existing point
        point = self.point_repository.get(id=point_id)
        if not point:
            raise NotFoundException(detail=f"Point with ID {point_id} not found")

        # Validate category if provided
        if point_in.category_id is not None:
            category = self.category_repository.get(id=point_in.category_id)
            if not category and point_in.category_id is not None:
                raise BadRequestException(
                    detail=f"Category with ID {point_in.category_id} not found"
                )

        # Check if coordinates are being updated
        if point_in.latitude is not None and point_in.longitude is not None:
            # Update coordinates
            point = self.point_repository.update_coordinates(
                point_id=point_id,
                latitude=point_in.latitude,
                longitude=point_in.longitude,
            )

        # Prepare update data for other fields
        update_data = point_in.model_dump(
            exclude={"latitude", "longitude"}, exclude_unset=True
        )
        if update_data:
            point = self.point_repository.update(db_obj=point, obj_data=update_data)

        return self._point_to_schema(point)

    def delete_point(self, *, point_id: int) -> PointSchema:
        """Delete a point"""
        point = self.point_repository.get(id=point_id)
        if not point:
            raise NotFoundException(detail=f"Point with ID {point_id} not found")

        point = self.point_repository.delete(id=point_id)
        return self._point_to_schema(point)

    def get_nearby_points(
        self, *, lat: float, lng: float, radius: float, limit: int = 100
    ) -> List[NearbyPoint]:
        """Get points near a location"""
        # Todo: enforcing max radius limits

        # Get nearby points with distances
        point_distance_tuples = self.point_repository.get_nearby(
            lat=lat, lng=lng, radius=radius, limit=limit
        )

        # Transform to schemas
        return [self._point_tuple_to_nearby_schema(t) for t in point_distance_tuples]

    def get_nearest_points(
        self, *, lat: float, lng: float, limit: int = 5
    ) -> List[NearbyPoint]:
        """Get the nearest points to a location"""
        # Get nearest points with distances
        point_distance_tuples = self.point_repository.get_nearest(
            lat=lat, lng=lng, limit=limit
        )

        # Transform to schemas
        return [self._point_tuple_to_nearby_schema(t) for t in point_distance_tuples]

    def get_points_within_polygon(
        self, *, polygon_wkt: str, limit: int = 100
    ) -> List[PointSchema]:
        """Get points within a polygon"""
        # Validate WKT format
        if not polygon_wkt.startswith("POLYGON"):
            raise BadRequestException(detail="Invalid polygon WKT format")

        # Get points
        points = self.point_repository.get_within_polygon(
            polygon_wkt=polygon_wkt, limit=limit
        )

        # Transform to schemas
        return [self._point_to_schema(p) for p in points]

    def _point_to_schema(self, point) -> PointSchema:
        """Convert a Point model to a Point schema"""

        # Convert to dict with basic fields
        data = {
            "id": point.id,
            "name": point.name,
            "description": point.description,
            "category_id": point.category_id,
            "created_at": point.created_at,
            "updated_at": point.updated_at,
            "coordinates": point_to_geojson(point.geometry),
        }

        # Add category if loaded
        if point.category:
            data["category"] = {
                "id": point.category.id,
                "name": point.category.name,
                "description": point.category.description,
                "color": point.category.color,
            }

        return PointSchema(**data)

    def _point_tuple_to_nearby_schema(self, point_tuple) -> NearbyPoint:
        """Convert a (Point, distance) tuple to a NearbyPoint schema"""
        point, distance = point_tuple

        # First convert to standard point schema
        point_data = self._point_to_schema(point).model_dump()

        # Add distance
        point_data["distance"] = distance

        # Create NearbyPoint
        return NearbyPoint(**point_data)
