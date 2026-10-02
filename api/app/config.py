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


settings = Settings()