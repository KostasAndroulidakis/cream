from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.services.auth import get_current_user_id
from app.services.logos import LogoSource, get_logo_source
from app.services.websites import is_domain

router = APIRouter()

# Logos rarely change: the browser keeps each for a week
CACHE_CONTROL = "private, max-age=604800"


@router.get("/{domain}", responses={200: {"content": {"image/png": {}}}, 404: {}})
def get_logo(
    domain: str,
    _user_id: int = Depends(get_current_user_id),
    source: LogoSource = Depends(get_logo_source),
):
    """A website's logo (e.g. a merchant's), or 404 so the app shows the initial instead."""
    logo = source.fetch(domain) if is_domain(domain) else None
    if logo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No logo")
    return Response(content=logo.content, media_type=logo.media_type, headers={"Cache-Control": CACHE_CONTROL})
