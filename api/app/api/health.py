from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import HealthResponse, ServiceStatus
from app.services.health import get_health

router = APIRouter()


@router.get(
    "",
    response_model=HealthResponse,
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": HealthResponse}},
)
def health_check(response: Response, db: Session = Depends(get_db)) -> HealthResponse:
    """Report API and database availability. Public endpoint (no auth)."""
    health = get_health(db)
    if health.database is ServiceStatus.DOWN:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return health
