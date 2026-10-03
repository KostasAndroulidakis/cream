"""Thin client for the Enable Banking API (https://enablebanking.com/docs/api/reference/)."""

import logging
import time
from collections.abc import Iterator
from datetime import date, datetime
from functools import lru_cache
from typing import Any, Protocol

import httpx2 as httpx
from fastapi import HTTPException, status
from jose import jwt

from app.config import settings

JWT_ISSUER = "enablebanking.com"
JWT_AUDIENCE = "api.enablebanking.com"
JWT_ALGORITHM = "RS256"
# The provider accepts tokens valid for at most one hour
JWT_LIFETIME_SECONDS = 3600
REQUEST_TIMEOUT_SECONDS = 30
# Enable Banking's transactions strategy for "everything the bank still has"
LONGEST_STRATEGY = "longest"

Json = dict[str, Any]

logger = logging.getLogger(__name__)


def _error_reason(response: httpx.Response) -> str | None:
    """The provider's own explanation of an error (its `message`, else `error`), if the body has one."""
    try:
        body = response.json()
    except ValueError:
        return None
    if not isinstance(body, dict):
        return None
    reason = body.get("message") or body.get("error")
    return str(reason) if reason else None


class BankProviderError(HTTPException):
    """The bank or the Open Banking provider failed or refused the request."""

    def __init__(self, detail: str = "The bank didn't respond. Try again later."):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)


class BankClient(Protocol):
    """What CREAM needs from an Open Banking provider (lets tests swap in a fake)."""

    def list_aspsps(self, country: str) -> list[Json]: ...

    def start_authorization(
        self, aspsp_name: str, country: str, state: str, valid_until: datetime, redirect_url: str
    ) -> str: ...

    def create_session(self, code: str) -> Json: ...

    def delete_session(self, session_id: str) -> None: ...

    def get_balances(self, account_uid: str) -> list[Json]: ...

    def iter_transactions(self, account_uid: str, date_from: date, longest: bool = False) -> Iterator[Json]: ...


class EnableBankingClient:
    def __init__(self, app_id: str, private_key: str, base_url: str):
        self._app_id = app_id
        self._private_key = private_key
        self._http = httpx.Client(base_url=base_url, timeout=REQUEST_TIMEOUT_SECONDS)

    def _token(self) -> str:
        now = int(time.time())
        claims = {"iss": JWT_ISSUER, "aud": JWT_AUDIENCE, "iat": now, "exp": now + JWT_LIFETIME_SECONDS}
        return jwt.encode(claims, self._private_key, algorithm=JWT_ALGORITHM, headers={"kid": self._app_id})

    def _request(self, method: str, path: str, **kwargs: Any) -> Json:
        try:
            response = self._http.request(
                method, path, headers={"Authorization": f"Bearer {self._token()}"}, **kwargs
            )
        except httpx.HTTPError as exc:
            raise BankProviderError() from exc
        if response.is_error:
            reason = _error_reason(response)
            logger.warning("Enable Banking %s %s failed (%s): %s", method, path, response.status_code, response.text)
            raise BankProviderError(f"Bank provider error ({response.status_code}){f': {reason}' if reason else ''}")
        return response.json() if response.content else {}

    def list_aspsps(self, country: str) -> list[Json]:
        return self._request("GET", "/aspsps", params={"country": country, "psu_type": "personal"})["aspsps"]

    def start_authorization(
        self, aspsp_name: str, country: str, state: str, valid_until: datetime, redirect_url: str
    ) -> str:
        body = {
            "access": {"valid_until": valid_until.isoformat()},
            "aspsp": {"name": aspsp_name, "country": country},
            "state": state,
            "redirect_url": redirect_url,
            "psu_type": "personal",
        }
        return self._request("POST", "/auth", json=body)["url"]

    def create_session(self, code: str) -> Json:
        return self._request("POST", "/sessions", json={"code": code})

    def delete_session(self, session_id: str) -> None:
        self._request("DELETE", f"/sessions/{session_id}")

    def get_balances(self, account_uid: str) -> list[Json]:
        return self._request("GET", f"/accounts/{account_uid}/balances")["balances"]

    def iter_transactions(self, account_uid: str, date_from: date, longest: bool = False) -> Iterator[Json]:
        """Booked and pending transactions since date_from, page by page.

        `longest`: the provider finds the earliest transaction the bank still gives and fetches from there,
        date_from only a hint; instead of refusing a period the bank no longer serves (WRONG_TRANSACTIONS_PERIOD).
        """
        params: dict[str, str] = {"date_from": date_from.isoformat()}
        if longest:
            params["strategy"] = LONGEST_STRATEGY
        while True:
            page = self._request("GET", f"/accounts/{account_uid}/transactions", params=params)
            yield from page.get("transactions", [])
            continuation_key = page.get("continuation_key")
            if not continuation_key:
                return
            params["continuation_key"] = continuation_key


@lru_cache
def _configured_client() -> EnableBankingClient:
    private_key = settings.enablebanking_key_path.read_text()  # type: ignore[union-attr]
    return EnableBankingClient(settings.enablebanking_app_id, private_key, settings.enablebanking_api_url)  # type: ignore[arg-type]


def get_bank_client() -> BankClient:
    """FastAPI dependency: the provider client, or 503 when bank sync isn't configured."""
    if not settings.enablebanking_app_id or not settings.enablebanking_key_path:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Bank connections aren't set up")
    return _configured_client()
