"""Logos by website, fetched from Logo.dev through the API (https://www.logo.dev/docs).

Going through the API keeps the token on the server, keeps the browser from telling the logo service
anything, and caches each logo so it's fetched once.
"""

from dataclasses import dataclass
from typing import Protocol

import httpx2 as httpx

from app.config import settings

# Pixels: twice the largest place a logo shows (56px in Edit merchant), for sharp screens
LOGO_SIZE = 128
REQUEST_TIMEOUT_SECONDS = 10


@dataclass(frozen=True)
class Logo:
    content: bytes
    media_type: str


class LogoSource(Protocol):
    def fetch(self, domain: str) -> Logo | None: ...


class LogoDevSource:
    """Logo.dev's logo for a domain; None when it has none or isn't set up. Remembers every answer."""

    def __init__(self, token: str | None, base_url: str):
        self._token = token
        self._base_url = base_url
        self._cache: dict[str, Logo | None] = {}

    def fetch(self, domain: str) -> Logo | None:
        if not self._token:
            return None
        if domain not in self._cache:
            try:
                response = httpx.get(
                    f"{self._base_url}/{domain}",
                    # fallback=404: no logo at all rather than Logo.dev's generated letter (CREAM draws its own)
                    params={"token": self._token, "size": LOGO_SIZE, "format": "png", "fallback": "404"},
                    timeout=REQUEST_TIMEOUT_SECONDS,
                )
            except httpx.HTTPError:
                return None  # not remembered: the next request tries again
            if response.status_code >= 500:
                return None
            media_type = response.headers.get("content-type", "image/png")
            self._cache[domain] = Logo(response.content, media_type) if response.is_success else None
        return self._cache[domain]


_source = LogoDevSource(settings.logo_dev_token, settings.logo_dev_url)


def get_logo_source() -> LogoSource:
    """FastAPI dependency: where logos come from (tests swap in a fake)."""
    return _source
