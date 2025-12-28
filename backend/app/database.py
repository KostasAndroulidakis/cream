import logging
from datetime import datetime, timezone
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session

from app.config import settings

logger = logging.getLogger(__name__)

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def utc_now() -> datetime:
    """Return current UTC datetime. Single source of truth for timestamp defaults."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    """Mixin providing created_at and updated_at timestamp columns."""

    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now)


def get_db() -> Generator[Session, None, None]:
    """Dependency that provides a database session.

    Yields a session and ensures proper cleanup on both success and failure.
    Logs any errors that occur during session cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error("Database error occurred: %s", str(e))
        db.rollback()
        raise
    finally:
        try:
            db.close()
        except SQLAlchemyError as e:
            logger.error("Error closing database session: %s", str(e))
