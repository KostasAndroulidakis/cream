from datetime import date, datetime
from zoneinfo import available_timezones

from pydantic import BaseModel, EmailStr, Field, field_validator

# A birthday before this is a typo, not a person
EARLIEST_BIRTHDAY = date(1900, 1, 1)


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)


class UserRead(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    display_name: str | None
    birthday: date | None
    timezone: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Settings › Profile. Fields left out stay as they are; null clears an optional one."""

    # Names can change but not disappear: null is rejected
    first_name: str = Field(None, min_length=1, max_length=100)
    last_name: str = Field(None, min_length=1, max_length=100)
    display_name: str | None = Field(None, max_length=100)
    birthday: date | None = None
    timezone: str | None = None

    @field_validator("first_name", "last_name", "display_name", mode="before")
    @classmethod
    def strip(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("display_name")
    @classmethod
    def blank_is_none(cls, value: str | None) -> str | None:
        return value or None

    @field_validator("birthday")
    @classmethod
    def plausible_birthday(cls, value: date | None) -> date | None:
        if value is not None and not EARLIEST_BIRTHDAY <= value <= date.today():
            raise ValueError("Birthday must be a past date")
        return value

    @field_validator("timezone")
    @classmethod
    def known_timezone(cls, value: str | None) -> str | None:
        if value is not None and value not in available_timezones():
            raise ValueError("Unknown timezone")
        return value


class LoginRequest(BaseModel):
    username: str
    password: str
