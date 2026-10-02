"""Health check business logic."""

import logging

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.schemas import HealthResponse, ServiceStatus

logger = logging.getLogger(__name__)


def is_database_reachable(db: Session) -> bool:
    """Return True if the database answers a trivial query."""
    try:
        db.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError as e:
        logger.error("Database health check failed: %s", str(e))
        return False


def get_health(db: Session) -> HealthResponse:
    """Build the health report for the API and its dependencies."""
    database = ServiceStatus.OK if is_database_reachable(db) else ServiceStatus.DOWN
    return HealthResponse(api=ServiceStatus.OK, database=database)
