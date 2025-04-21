# app/api/deps.py
from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.core.exceptions import AuthenticationException
from app.core.security import is_token_blacklisted
from app.database import SessionLocal
from app.models.user import User
from app.repositories.category import CategoryRepository
from app.repositories.point import PointRepository
from app.repositories.user import UserRepository
from app.schemas.user import TokenData
from app.services.category import CategoryService
from app.services.point import PointService
from app.services.user import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")


def get_db() -> Generator[Session, None, None]:
    """Provide a database session with proper error handling"""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        # Always rollback on exception
        db.rollback()
        raise
    finally:
        db.close()


# Repository dependencies
def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """Provide a UserRepository instance"""
    return UserRepository(db)


def get_category_repository(db: Session = Depends(get_db)) -> CategoryRepository:
    """Provide a CategoryRepository instance"""
    return CategoryRepository(db)


def get_point_repository(db: Session = Depends(get_db)) -> PointRepository:
    """Provide a PointRepository instance"""
    return PointRepository(db)


# Service dependencies
def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    """Provide a UserService instance"""
    return UserService(user_repository)


def get_category_service(
    category_repository: CategoryRepository = Depends(get_category_repository),
) -> CategoryService:
    """Provide a CategoryService instance"""
    return CategoryService(category_repository)


def get_point_service(
    point_repository: PointRepository = Depends(get_point_repository),
    category_repository: CategoryRepository = Depends(get_category_repository),
) -> PointService:
    """Provide a PointService instance"""
    return PointService(point_repository, category_repository)


# Authentication dependencies
def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repository: UserRepository = Depends(get_user_repository),
) -> User:
    """Get current user from JWT token"""
    try:
        # Check if token is blacklisted
        if is_token_blacklisted(token):
            raise AuthenticationException(detail="Token has been revoked")

        # Decode token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise AuthenticationException(detail="Invalid authentication credentials")

        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise AuthenticationException(detail="Invalid authentication credentials")

    # Get user from database
    user = user_repository.get(id=int(token_data.user_id))
    if user is None:
        raise AuthenticationException(detail="User not found")

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Verify user is active"""
    if not current_user.is_active:
        raise AuthenticationException(detail="Inactive user")
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Verify user is a superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user
