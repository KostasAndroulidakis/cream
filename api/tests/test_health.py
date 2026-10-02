from app.schemas import HealthResponse, ServiceStatus

HEALTH_URL = "/api/v1/health"


class TestHealth:
    def test_health_ok(self, client):
        response = client.get(HEALTH_URL)

        assert response.status_code == 200
        assert response.json() == {"api": "ok", "database": "ok"}

    def test_health_database_down(self, client, monkeypatch):
        monkeypatch.setattr(
            "app.api.health.get_health",
            lambda db: HealthResponse(api=ServiceStatus.OK, database=ServiceStatus.DOWN),
        )

        response = client.get(HEALTH_URL)

        assert response.status_code == 503
        assert response.json() == {"api": "ok", "database": "down"}

    def test_health_requires_no_auth(self, client):
        response = client.get(HEALTH_URL)

        assert response.status_code != 401
