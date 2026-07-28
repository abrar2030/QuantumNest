import os
from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional

from app.db.database import get_db
from app.main import get_current_active_user
from app.models.models import User
from app.schemas.schemas import LoginResponse, UserCreate, UserResponse, UserUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

router = APIRouter(tags=["users"])

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)) -> Any:
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    if user.username:
        existing_username = (
            db.query(User).filter(User.username == user.username).first()
        )
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
            )
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        first_name=user.first_name or "",
        last_name=user.last_name or "",
        hashed_password=hashed_password,
        role=user.role.value if user.role else "user",
        tier=user.tier.value if user.tier else "basic",
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    return current_user


@router.get("/", response_model=List[UserResponse])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return db_user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    update_data = user.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    if "role" in update_data and update_data["role"] is not None:
        update_data["role"] = update_data["role"].value
    if "tier" in update_data and update_data["tier"] is not None:
        update_data["tier"] = update_data["tier"].value
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db_user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    db.delete(db_user)
    db.commit()


@router.post("/password-reset/request")
def request_password_reset(email: str, db: Session = Depends(get_db)) -> Any:
    """Request a password reset link.

    Always returns a generic success message so the endpoint cannot be used to
    enumerate registered email addresses. The reset token is a short-lived,
    stateless JWT (no DB migration required). In production this token would
    be emailed to the user by a mail service; outside of production it is
    also returned in the response body for local development/testing.
    """
    user = db.query(User).filter(User.email == email).first()
    reset_token: Optional[str] = None
    if user:
        reset_token = create_access_token(
            data={"sub": user.email, "purpose": "password_reset"},
            expires_delta=timedelta(minutes=15),
        )

    response: dict = {
        "message": "If an account exists for this email, a password reset link has been sent.",
    }
    is_production = os.getenv("ENVIRONMENT", "development").lower() == "production"
    if reset_token and not is_production:
        response["reset_token"] = reset_token
    return response


@router.post("/password-reset/confirm")
def confirm_password_reset(
    token: str,
    new_password: str,
    db: Session = Depends(get_db),
) -> Any:
    """Confirm a password reset using the token issued by /password-reset/request."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="This reset link is invalid or has expired.",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception as exc:
        raise credentials_exception from exc

    if payload.get("purpose") != "password_reset" or not payload.get("sub"):
        raise credentials_exception

    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user:
        raise credentials_exception

    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long.",
        )

    user.hashed_password = get_password_hash(new_password)
    db.commit()
    return {"message": "Your password has been updated. You can now sign in."}


@router.post("/login", response_model=LoginResponse)
def login(
    email: str,
    password: str,
    db: Session = Depends(get_db),
) -> Any:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    role_value = user.role.value if hasattr(user.role, "value") else user.role
    access_token = create_access_token(
        data={"sub": user.email, "id": user.id, "role": role_value},
        expires_delta=access_token_expires,
    )
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role": role_value,
    }
