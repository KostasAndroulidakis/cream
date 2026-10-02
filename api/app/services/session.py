"""Session cookie handling: the JWT lives in an httpOnly cookie, never in JavaScript."""

from typing import Literal

from fastapi import Response
from fastapi.security import APIKeyCookie

from app.config import settings

# Cookie is only sent to API routes, never cross-site (CSRF protection)
SESSION_COOKIE_PATH = "/api"
SESSION_COOKIE_SAMESITE: Literal["strict"] = "strict"
SECONDS_PER_MINUTE = 60

session_cookie = APIKeyCookie(
    name=settings.auth_cookie_name,
    auto_error=False,
    description="Session JWT set by POST /api/v1/auth/login",
)


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=token,
        max_age=settings.access_token_expire_minutes * SECONDS_PER_MINUTE,
        path=SESSION_COOKIE_PATH,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite=SESSION_COOKIE_SAMESITE,
    )


def clear_session_cookie(response: Response) -> None:
    # Attributes must match the original cookie for browsers to remove it
    response.delete_cookie(
        key=settings.auth_cookie_name,
        path=SESSION_COOKIE_PATH,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite=SESSION_COOKIE_SAMESITE,
    )
