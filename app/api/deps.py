from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.point import PointService
from app.services.category import CategoryService
from app.repositories.point import PointRepository
from app.repositories.category import CategoryRepository


# Repository dependencies
def get_point_repository() -> PointRepository:
    return PointRepository()

def get_category_repository() -> CategoryRepository:
    return CategoryRepository()

# Service dependencies
def get_point_service(
        repo: PointRepository = Depends(get_point_repository),
) -> PointService:
    return PointService(repository=repo)

def get_category_service(
        repo: CategoryRepository = Depends(get_category_repository),
) -> CategoryService:
    return CategoryService(repository=repo)