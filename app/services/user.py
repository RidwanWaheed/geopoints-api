# app/services/user_service.py
from datetime import datetime, timedelta
from typing import List, Optional

from app.config import settings
from app.core.exceptions import (
    AuthenticationException,
    BadRequestException,
    NotFoundException,
)
from app.core.security import blacklist_token, create_access_token
from app.core.utils import utc_now
from app.repositories.user import UserRepository
from app.schemas.pagination import PagedResponse, PageParams
from app.schemas.user import Token, TokenData
from app.schemas.user import User as UserSchema
from app.schemas.user import UserCreate, UserUpdate


class UserService:

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(self, *, user_in: UserCreate) -> UserSchema:
        try:
            if self.user_repository.email_exists(email=user_in.email):
                raise BadRequestException(detail="Email already registered")

            if self.user_repository.username_exists(username=user_in.username):
                raise BadRequestException(detail="Username already taken")

            user = self.user_repository.create(
                email=user_in.email,
                username=user_in.username,
                password=user_in.password,
                is_active=user_in.is_active if user_in.is_active is not None else True,
                is_superuser=(
                    user_in.is_superuser if user_in.is_superuser is not None else False
                ),
            )

            self.user_repository.session.commit()
            self.user_repository.session.refresh(user)

            return self._user_to_schema(user)
        except Exception as e:
            self.user_repository.session.rollback()
            raise e

    def get_user(self, *, user_id: int) -> UserSchema:
        user = self.user_repository.get(id=user_id)
        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} not found")

        return self._user_to_schema(user)

    def get_users(self, *, page_params: PageParams) -> PagedResponse[UserSchema]:
        skip = (page_params.page - 1) * page_params.limit

        total = self.user_repository.count()
        users = self.user_repository.get_multi(skip=skip, limit=page_params.limit)

        user_schemas = [self._user_to_schema(u) for u in users]

        return PagedResponse.create(
            items=user_schemas,
            total=total,
            page=page_params.page,
            limit=page_params.limit,
        )

    def update_user(self, *, user_id: int, user_in: UserUpdate) -> UserSchema:
        try:
            user = self.user_repository.get(id=user_id)
            if not user:
                raise NotFoundException(detail=f"User with ID {user_id} not found")

            if user_in.email is not None and user_in.email != user.email:
                if self.user_repository.email_exists(
                    email=user_in.email, exclude_id=user_id
                ):
                    raise BadRequestException(detail="Email already registered")

            if user_in.username is not None and user_in.username != user.username:
                if self.user_repository.username_exists(
                    username=user_in.username, exclude_id=user_id
                ):
                    raise BadRequestException(detail="Username already taken")

            update_data = user_in.model_dump(exclude_unset=True)

            # Handle password separately if included
            password = None
            if "password" in update_data:
                password = update_data.pop("password")

            if update_data:
                user = self.user_repository.update(db_obj=user, obj_data=update_data)

            # Update password if provided
            if password:
                # Todo: Password update implementation will need to be added to UserRepository
                pass

            self.user_repository.session.commit()
            self.user_repository.session.refresh(user)

            return self._user_to_schema(user)
        except Exception as e:
            self.user_repository.session.rollback()
            raise e

    def delete_user(self, *, user_id: int) -> UserSchema:
        try:
            user = self.user_repository.get(id=user_id)
            if not user:
                raise NotFoundException(detail=f"User with ID {user_id} not found")

            user = self.user_repository.delete(id=user_id)

            self.user_repository.session.commit()

            return self._user_to_schema(user)
        except Exception as e:
            self.user_repository.session.rollback()
            raise e

    def authenticate(self, *, email: str, password: str) -> UserSchema:
        user = self.user_repository.authenticate(email=email, password=password)
        if not user:
            raise AuthenticationException(detail="Incorrect email or password")

        user = self.user_repository.update_last_login(user_id=user.id)

        return self._user_to_schema(user)

    def create_access_token(
        self, *, user_id: int, expires_delta: Optional[timedelta] = None
    ) -> Token:
        if expires_delta:
            expire = utc_now() + expires_delta
        else:
            expire = utc_now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        token = create_access_token(subject=str(user_id))

        return Token(access_token=token, token_type="bearer")

    def logout(self, *, token: str) -> bool:
        token_str = token.credentials
        blacklist_token(token_str)
        return True

    def _user_to_schema(self, user) -> UserSchema:
        """Convert a User model to a User schema"""
        return UserSchema(
            id=user.id,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            last_login=user.last_login,
        )
