from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm

from app.api.deps import get_current_user, get_user_service
from app.core.security import blacklist_token
from app.models.user import User
from app.schemas.user import Token
from app.schemas.user import User as UserSchema
from app.schemas.user import UserCreate
from app.services.user import UserService

router = APIRouter()
security = HTTPBearer()


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service),
):
    user = service.authenticate(email=form_data.username, password=form_data.password)

    return service.create_access_token(user_id=user.id)


@router.post(
    "/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED
)
def register_user(
    user_in: UserCreate, service: UserService = Depends(get_user_service)
):
    return service.create_user(user_in=user_in)


@router.get("/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_user)):
    return UserSchema.model_validate(current_user)


@router.post("/logout")
def logout(
    token: str = Depends(security),
    service: UserService = Depends(get_user_service),
):
    service.logout(token=token)
    return {"message": "Successfully logged out"}
