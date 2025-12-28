import logging
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def check_user_exists(db: Session, username: str | None = None, email: str | None = None) -> str | None:
    """Check if user exists by username or email. Returns the field that exists, or None."""
    from app.models import User

    if username and db.query(User).filter(User.username == username).first():
        return "username"
    if email and db.query(User).filter(User.email == email).first():
        return "email"
    return None


def create_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    first_name: str | None = None,
    last_name: str | None = None,
):
    """Create a new user after checking for duplicates.

    Raises HTTPException if username or email already exists.
    """
    from app.models import User

    # Check for duplicates
    existing = check_user_exists(db, username=username, email=email)
    if existing == "username":
        logger.warning("Signup failed: username '%s' already exists", username)
        raise HTTPException(status_code=400, detail="Username already exists")
    if existing == "email":
        logger.warning("Signup failed: email '%s' already exists", email)
        raise HTTPException(status_code=400, detail="Email already exists")

    # Create user
    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        first_name=first_name,
        last_name=last_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def verify_token(token: str) -> int | None:
    """Verify JWT token and return user_id if valid, None otherwise."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            return None
        return int(user_id)
    except JWTError:
        return None


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """FastAPI dependency to get current user ID from JWT token."""
    user_id = verify_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """FastAPI dependency to get current user from JWT token."""
    from app.models import User

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
