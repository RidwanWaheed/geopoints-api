from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_current_user, get_user_service
from app.models.user import User
from app.schemas.user import Token, User as UserSchema, UserCreate
from app.services.user import UserService

router = APIRouter()

@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service)
):
    """OAuth2 compatible token login, get an access token for future requests"""
    user = service.authenticate(email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return service.create_token(user_id=user.id)

@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register_user(
    *,
    user_in: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """Register a new user"""
    return service.create(obj_in=user_in)

@router.get("/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user"""
    return current_user