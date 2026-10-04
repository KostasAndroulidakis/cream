"""GET /logos/{domain}: logos through the API, from a fake source."""

import pytest

from app.main import app
from app.services.logos import Logo, get_logo_source

LOGOS_URL = "/api/v1/logos"


class FakeLogoSource:
    def __init__(self):
        self.requested: list[str] = []

    def fetch(self, domain):
        self.requested.append(domain)
        return Logo(b"png-bytes", "image/png") if domain == "wolt.com" else None


@pytest.fixture
def logos(client):
    fake = FakeLogoSource()
    app.dependency_overrides[get_logo_source] = lambda: fake
    return fake


def test_known_logo_is_served_and_cached_by_the_browser(client, auth_headers, logos):
    response = client.get(f"{LOGOS_URL}/wolt.com", headers=auth_headers)

    assert response.status_code == 200 and response.content == b"png-bytes"
    assert response.headers["content-type"] == "image/png"
    assert "max-age" in response.headers["cache-control"]


def test_missing_logo_is_404(client, auth_headers, logos):
    assert client.get(f"{LOGOS_URL}/unknown.gr", headers=auth_headers).status_code == 404


def test_not_a_domain_never_reaches_the_source(client, auth_headers, logos):
    assert client.get(f"{LOGOS_URL}/localhost", headers=auth_headers).status_code == 404
    assert logos.requested == []


def test_requires_login(client, logos):
    assert client.get(f"{LOGOS_URL}/wolt.com").status_code == 401
