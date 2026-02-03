"""
Authentication API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from app.models.user import UserCreate, UserLogin, UserResponse, Token
from app.services import auth_service, db_service
from app.dependencies import get_current_user
from config import get_settings

router = APIRouter()
settings = get_settings()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate):
    """
    Register a new user.
    """
    # Check if email exists
    if db_service.user_exists_by_email(user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )
    
    # Check if username exists
    if db_service.user_exists_by_username(user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username already exists."
        )
    
    user = auth_service.create_user(
        email=user_in.email,
        username=user_in.username,
        password=user_in.password,
        full_name=user_in.full_name
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user."
        )
    
    return user

@router.post("/login", response_model=Token)
async def login(user_in: UserLogin):
    """
    Login and return a JWT access token.
    """
    user = auth_service.authenticate_user(user_in.email, user_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    Get the profile of the currently logged-in user.
    """
    return current_user

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout the current user (stateless, mainly for frontend).
    """
    return {"message": "Successfully logged out"}
