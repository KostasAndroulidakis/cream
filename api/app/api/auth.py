import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserRead, UserUpdate, LoginRequest
from app.services.auth import authenticate_user, create_access_token, create_user, get_current_user
from app.services.session import clear_session_cookie, set_session_cookie

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    return create_user(
        db=db,
        username=user_in.username,
        email=user_in.email,
        password=user_in.password,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
    )


@router.post("/login", response_model=UserRead)
def login(credentials: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Verify credentials and start a session (httpOnly cookie)."""
    user = authenticate_user(db, credentials.username, credentials.password)
    if user is None:
        logger.warning("Login failed for username '%s'", credentials.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    logger.info("User '%s' logged in successfully", credentials.username)
    set_session_cookie(response, create_access_token({"sub": str(user.id)}))
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    """End the session by clearing the cookie."""
    clear_session_cookie(response)


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return user


@router.patch("/me", response_model=UserRead)
def update_me(changes: UserUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Change the current user's profile (Settings › Profile); fields left out stay as they are."""
    for field, value in changes.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user
