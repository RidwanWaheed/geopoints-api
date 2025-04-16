from contextlib import contextmanager
from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.db.unit_of_work import UnitOfWork
from app.services.category import CategoryService
from app.services.point import PointService
from app.services.user import UserService
from app.config import settings
from app.core.exceptions import AuthenticationException
from app.db.unit_of_work import UnitOfWork
from app.models.user import User
from app.schemas.user import TokenData
from app.services.user import UserService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

# Create a singleton UnitOfWork instance
_uow = UnitOfWork()


def get_uow() -> UnitOfWork:
    """Provide a Unit of Work instance"""
    return _uow


# Update FastAPI shutdown event to close the session when app shuts down
def cleanup_uow():
    _uow.close()


# Service dependencies
def get_point_service(
    uow: UnitOfWork = Depends(get_uow),
) -> Generator[PointService, None, None]:
    """Provide a Point service with initialized repositories"""
    with uow.start() as active_uow:
        yield PointService(repository=active_uow.points)


def get_category_service(
    uow: UnitOfWork = Depends(get_uow),
) -> Generator[CategoryService, None, None]:
    """Provide a Category service with initialized repositories"""
    with uow.start() as active_uow:
        yield CategoryService(repository=active_uow.categories)


def get_user_service(uow: UnitOfWork = Depends(get_uow)) -> Generator[UserService, None, None]:
    """Provide a User service with initialized repositories"""
    with uow.start() as active_uow:
        yield UserService(repository=active_uow.users)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    uow: UnitOfWork = Depends(get_uow)
) -> User:
    """Get the current user from the JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise AuthenticationException(detail="Invalid authentication credentials")
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise AuthenticationException(detail="Invalid authentication credentials")
    
    with uow.start() as active_uow:
        user = active_uow.users.get(id=int(token_data.user_id))
        if user is None:
            raise AuthenticationException(detail="User not found")
        if not user.is_active:
            raise AuthenticationException(detail="Inactive user")
    
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get the current active user"""
    if not current_user.is_active:
        raise AuthenticationException(detail="Inactive user")
    return current_user

def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get the current superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user