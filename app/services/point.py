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
        try:
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

            self.point_repository.session.commit()
            self.point_repository.session.refresh(point)

            return self._point_to_schema(point)
        except Exception as e:
            self.point_repository.session.rollback()
            raise e

    def get_point(self, *, point_id: int) -> PointSchema:
        point = self.point_repository.get(id=point_id)
        if not point:
            raise NotFoundException(detail=f"Point with ID {point_id} not found")

        return self._point_to_schema(point)

    def get_points(
        self, *, page_params: PageParams, category_id: Optional[int] = None
    ) -> PagedResponse[PointSchema]:

        skip = (page_params.page - 1) * page_params.limit

        if category_id:
            total = self.point_repository.count_by_category(category_id=category_id)
        else:
            total = self.point_repository.count()

        if category_id:
            points = self.point_repository.get_by_category(
                category_id=category_id, skip=skip, limit=page_params.limit
            )
        else:
            points = self.point_repository.get_multi(skip=skip, limit=page_params.limit)

        point_schemas = [self._point_to_schema(p) for p in points]

        return PagedResponse.create(
            items=point_schemas,
            total=total,
            page=page_params.page,
            limit=page_params.limit,
        )

    def update_point(self, *, point_id: int, point_in: PointUpdate) -> PointSchema:
        try:
            point = self.point_repository.get(id=point_id)
            if not point:
                raise NotFoundException(detail=f"Point with ID {point_id} not found")

            if point_in.category_id is not None:
                category = self.category_repository.get(id=point_in.category_id)
                if not category and point_in.category_id is not None:
                    raise BadRequestException(
                        detail=f"Category with ID {point_in.category_id} not found"
                    )

            if point_in.latitude is not None and point_in.longitude is not None:
                point = self.point_repository.update_coordinates(
                    point_id=point_id,
                    latitude=point_in.latitude,
                    longitude=point_in.longitude,
                )

            update_data = point_in.model_dump(
                exclude={"latitude", "longitude"}, exclude_unset=True
            )
            if update_data:
                point = self.point_repository.update(db_obj=point, obj_data=update_data)

            self.point_repository.session.commit()
            self.point_repository.session.refresh(point)

            return self._point_to_schema(point)
        except Exception as e:
            self.point_repository.session.rollback()
            raise e

    def delete_point(self, *, point_id: int) -> PointSchema:
        try:
            point = self.point_repository.get(id=point_id)
            if not point:
                raise NotFoundException(detail=f"Point with ID {point_id} not found")

            point = self.point_repository.delete(id=point_id)

            self.point_repository.session.commit()

            return self._point_to_schema(point)
        except Exception as e:
            self.point_repository.session.rollback()
            raise e

    def get_nearby_points(
        self, *, lat: float, lng: float, radius: float, limit: int = 100
    ) -> List[NearbyPoint]:
        # Todo: enforcing max radius limits

        point_distance_tuples = self.point_repository.get_nearby(
            lat=lat, lng=lng, radius=radius, limit=limit
        )

        return [self._point_tuple_to_nearby_schema(t) for t in point_distance_tuples]

    def get_nearest_points(
        self, *, lat: float, lng: float, limit: int = 5
    ) -> List[NearbyPoint]:
        point_distance_tuples = self.point_repository.get_nearest(
            lat=lat, lng=lng, limit=limit
        )

        return [self._point_tuple_to_nearby_schema(t) for t in point_distance_tuples]

    def get_points_within_polygon(
        self, *, polygon_wkt: str, limit: int = 100
    ) -> List[PointSchema]:
        if not polygon_wkt.startswith("POLYGON"):
            raise BadRequestException(detail="Invalid polygon WKT format")

        points = self.point_repository.get_within_polygon(
            polygon_wkt=polygon_wkt, limit=limit
        )

        return [self._point_to_schema(p) for p in points]

    def _point_to_schema(self, point) -> PointSchema:
        data = {
            "id": point.id,
            "name": point.name,
            "description": point.description,
            "category_id": point.category_id,
            "created_at": point.created_at,
            "updated_at": point.updated_at,
            "coordinates": point_to_geojson(point.geometry),
        }

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
