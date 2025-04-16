from contextlib import contextmanager
from typing import Generator

from fastapi import Depends

from app.db.unit_of_work import UnitOfWork
from app.services.category import CategoryService
from app.services.point import PointService


def get_uow() -> UnitOfWork:
    """Provide a Unit of Work instance"""
    return UnitOfWork()


# Service dependencies
def get_point_service(uow: UnitOfWork = Depends(get_uow)) -> Generator[PointService, None, None]:
    """Provide a Point service with initialized repositories"""
    with uow.start() as active_uow:
        yield PointService(repository=active_uow.points)


def get_category_service(uow: UnitOfWork = Depends(get_uow)) -> Generator[CategoryService, None, None]:
    """Provide a Category service with initialized repositories"""
    with uow.start() as active_uow:
        yield CategoryService(repository=active_uow.categories)