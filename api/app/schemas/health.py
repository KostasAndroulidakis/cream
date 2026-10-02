"""Health check response schemas."""

from enum import StrEnum

from pydantic import BaseModel


class ServiceStatus(StrEnum):
    """Availability of a single service component."""

    OK = "ok"
    DOWN = "down"


class HealthResponse(BaseModel):
    """Availability of the API and its dependencies."""

    api: ServiceStatus
    database: ServiceStatus
