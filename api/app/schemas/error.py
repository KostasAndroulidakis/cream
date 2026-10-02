"""Error response schemas for API documentation."""

from pydantic import BaseModel


class ValidationErrorDetail(BaseModel):
    """A single validation error."""

    field: str
    message: str


class ValidationErrorResponse(BaseModel):
    """Response for validation errors (422)."""

    detail: list[ValidationErrorDetail]


class ErrorResponse(BaseModel):
    """Generic error response."""

    detail: str
