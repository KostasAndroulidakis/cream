from pathlib import Path

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

# The repo-root .env is the single source of truth, shared with docker compose
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_prefix="CREAM_", extra="ignore")

    postgres_user: str = Field(validation_alias="POSTGRES_USER")
    postgres_password: str = Field(validation_alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(validation_alias="POSTGRES_DB")
    postgres_host: str = Field("localhost", validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(5432, validation_alias="POSTGRES_PORT")

    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    auth_cookie_name: str = "cream_session"
    # Browsers treat http://localhost as secure, so this stays on in development too
    auth_cookie_secure: bool = True

    # Enable Banking (Open Banking / PSD2). Unset app ID or key path = bank sync disabled.
    enablebanking_app_id: str | None = None
    # Private key lives outside the repo (e.g. ~/.config/cream/), never in git
    enablebanking_key_path: Path | None = None
    enablebanking_api_url: str = "https://api.enablebanking.com"
    enablebanking_redirect_url: str = "http://localhost:5173/connections/callback"
    # Most banks cap consent at 180 days; the provider rejects longer requests
    bank_consent_days: int = 180
    # Where the first sync of an account starts looking. It asks for the "longest" history, so the bank
    # gives everything it still has from there (often 1-3 years, right after the user logs in)
    bank_initial_history_days: int = 730
    # Later syncs re-read a few days back, to catch transactions booked late
    bank_sync_overlap_days: int = 3

    @computed_field
    @property
    def database_url(self) -> str:
        # URL.create escapes special characters in credentials safely
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        ).render_as_string(hide_password=False)


# Fields are populated from environment / .env at runtime, not via __init__ args
settings = Settings()  # pyright: ignore[reportCallIssue]
