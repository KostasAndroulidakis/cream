import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.models import Category, CategoryType
from app.services.banking.client import get_bank_client
from app.services.categorization.system_categories import UNCATEGORIZED_KEY
from tests.bank_fakes import FakeBankClient

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

LOGIN_URL = "/api/v1/auth/login"
SIGNUP_URL = "/api/v1/auth/signup"
REVIEW_INBOX_URL = "/api/v1/transactions/needs-review"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.fixture
def registered_user(client, test_user_data):
    """Create and return a registered user."""
    response = client.post(SIGNUP_URL, json=test_user_data)
    assert response.status_code == 201
    return response.json()


def login_session_headers(client, username: str, password: str) -> dict[str, str]:
    """Log in and return headers carrying that user's session cookie.

    The client's cookie jar is cleared so each request's identity is explicit.
    """
    response = client.post(LOGIN_URL, json={"username": username, "password": password})
    assert response.status_code == 200
    token = response.cookies[settings.auth_cookie_name]
    client.cookies.clear()
    return {"Cookie": f"{settings.auth_cookie_name}={token}"}


@pytest.fixture
def auth_headers(client, test_user_data, registered_user):
    """Session headers for the default test user."""
    return login_session_headers(client, test_user_data["username"], test_user_data["password"])


@pytest.fixture
def second_user_data():
    """Second user for testing access denial."""
    return {
        "username": "otheruser",
        "email": "other@example.com",
        "password": "otherpassword123",
        "first_name": "Other",
        "last_name": "User",
    }


@pytest.fixture
def second_auth_headers(client, second_user_data):
    """Session headers for the second user."""
    response = client.post(SIGNUP_URL, json=second_user_data)
    assert response.status_code == 201
    return login_session_headers(client, second_user_data["username"], second_user_data["password"])


@pytest.fixture
def bank(client):
    """A fake Open Banking provider in place of Enable Banking."""
    fake = FakeBankClient()
    app.dependency_overrides[get_bank_client] = lambda: fake
    return fake


@pytest.fixture
def uncategorized(db_session):
    """The system category imported transactions fall back to."""
    category = Category(user_id=None, name="Uncategorized", type=CategoryType.EXPENSE, key=UNCATEGORIZED_KEY)
    db_session.add(category)
    db_session.commit()
    return category
