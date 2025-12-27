import pytest


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
def second_user_token(client, second_user_data):
    """Create second user and get auth token."""
    client.post("/api/v1/auth/signup", json=second_user_data)
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": second_user_data["username"],
            "password": second_user_data["password"],
        },
    )
    return response.json()["access_token"]


@pytest.fixture
def second_auth_headers(second_user_token):
    """Headers for second user."""
    return {"Authorization": f"Bearer {second_user_token}"}


@pytest.fixture
def category_data():
    """Sample category data."""
    return {
        "name": "Groceries",
        "type": "expense",
    }


@pytest.fixture
def income_category_data():
    """Sample income category data."""
    return {
        "name": "Salary",
        "type": "income",
    }


@pytest.fixture
def created_category(client, auth_headers, category_data):
    """Create and return a category."""
    response = client.post(
        "/api/v1/categories",
        json=category_data,
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def system_default_category(db_session):
    """Create a system default category (user_id = None)."""
    from app.models import Category
    from app.models.category import CategoryType

    category = Category(
        user_id=None,
        name="Default Food",
        type=CategoryType.EXPENSE,
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return {"id": category.id, "name": category.name, "type": category.type.value}


class TestListCategories:
    """Tests for GET /api/v1/categories"""

    def test_list_categories_empty(self, client, auth_headers):
        """Test listing categories when none exist."""
        response = client.get("/api/v1/categories", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    def test_list_categories_returns_user_categories(
        self, client, auth_headers, created_category
    ):
        """Test listing categories returns user's categories."""
        response = client.get("/api/v1/categories", headers=auth_headers)

        assert response.status_code == 200
        categories = response.json()
        assert len(categories) == 1
        assert categories[0]["name"] == created_category["name"]

    def test_list_categories_includes_system_defaults(
        self, client, auth_headers, system_default_category
    ):
        """Test listing categories includes system defaults."""
        response = client.get("/api/v1/categories", headers=auth_headers)

        assert response.status_code == 200
        categories = response.json()
        assert len(categories) == 1
        assert categories[0]["name"] == system_default_category["name"]

    def test_list_categories_user_and_system(
        self, client, auth_headers, created_category, system_default_category
    ):
        """Test listing returns both user categories and system defaults."""
        response = client.get("/api/v1/categories", headers=auth_headers)

        assert response.status_code == 200
        categories = response.json()
        assert len(categories) == 2
        names = [c["name"] for c in categories]
        assert created_category["name"] in names
        assert system_default_category["name"] in names

    def test_list_categories_unauthenticated(self, client):
        """Test listing categories without auth fails."""
        response = client.get("/api/v1/categories")

        assert response.status_code == 401


class TestCreateCategory:
    """Tests for POST /api/v1/categories"""

    def test_create_category_success(self, client, auth_headers, category_data):
        """Test successful category creation."""
        response = client.post(
            "/api/v1/categories",
            json=category_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == category_data["name"]
        assert data["type"] == category_data["type"]
        assert data["parent_id"] is None
        assert "id" in data
        assert "created_at" in data

    def test_create_category_income_type(
        self, client, auth_headers, income_category_data
    ):
        """Test creating income category."""
        response = client.post(
            "/api/v1/categories",
            json=income_category_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        assert response.json()["type"] == "income"

    def test_create_category_with_parent(
        self, client, auth_headers, created_category
    ):
        """Test creating subcategory with parent."""
        child_data = {
            "name": "Fruits",
            "type": "expense",
            "parent_id": created_category["id"],
        }

        response = client.post(
            "/api/v1/categories",
            json=child_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        assert response.json()["parent_id"] == created_category["id"]

    def test_create_category_unauthenticated(self, client, category_data):
        """Test creating category without auth fails."""
        response = client.post("/api/v1/categories", json=category_data)

        assert response.status_code == 401

    def test_create_category_invalid_type(self, client, auth_headers):
        """Test creating category with invalid type fails."""
        response = client.post(
            "/api/v1/categories",
            json={"name": "Bad Category", "type": "invalid"},
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_create_category_missing_fields(self, client, auth_headers):
        """Test creating category with missing fields fails."""
        response = client.post(
            "/api/v1/categories",
            json={"name": "No Type"},
            headers=auth_headers,
        )

        assert response.status_code == 422


class TestGetCategory:
    """Tests for GET /api/v1/categories/{id}"""

    def test_get_category_success(self, client, auth_headers, created_category):
        """Test getting own category."""
        response = client.get(
            f"/api/v1/categories/{created_category['id']}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["id"] == created_category["id"]
        assert response.json()["name"] == created_category["name"]

    def test_get_category_system_default(
        self, client, auth_headers, system_default_category
    ):
        """Test getting system default category."""
        response = client.get(
            f"/api/v1/categories/{system_default_category['id']}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["id"] == system_default_category["id"]
        assert response.json()["name"] == system_default_category["name"]

    def test_get_category_not_found(self, client, auth_headers):
        """Test getting non-existent category."""
        response = client.get("/api/v1/categories/99999", headers=auth_headers)

        assert response.status_code == 404

    def test_get_category_access_denied(
        self, client, auth_headers, second_auth_headers, created_category
    ):
        """Test accessing another user's category is denied."""
        response = client.get(
            f"/api/v1/categories/{created_category['id']}",
            headers=second_auth_headers,
        )

        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    def test_get_category_unauthenticated(self, client, created_category):
        """Test getting category without auth fails."""
        response = client.get(f"/api/v1/categories/{created_category['id']}")

        assert response.status_code == 401


class TestUpdateCategory:
    """Tests for PATCH /api/v1/categories/{id}"""

    def test_update_category_success(self, client, auth_headers, created_category):
        """Test updating own category."""
        response = client.patch(
            f"/api/v1/categories/{created_category['id']}",
            json={"name": "Updated Category"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Updated Category"

    def test_update_category_partial(self, client, auth_headers, created_category):
        """Test partial update only changes specified fields."""
        original_type = created_category["type"]

        response = client.patch(
            f"/api/v1/categories/{created_category['id']}",
            json={"name": "New Name"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["name"] == "New Name"
        assert response.json()["type"] == original_type

    def test_update_category_parent(
        self, client, auth_headers, created_category
    ):
        """Test updating category parent."""
        # Create another category to be parent
        parent_response = client.post(
            "/api/v1/categories",
            json={"name": "Parent Category", "type": "expense"},
            headers=auth_headers,
        )
        parent_id = parent_response.json()["id"]

        response = client.patch(
            f"/api/v1/categories/{created_category['id']}",
            json={"parent_id": parent_id},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["parent_id"] == parent_id

    def test_update_category_access_denied(
        self, client, auth_headers, second_auth_headers, created_category
    ):
        """Test updating another user's category is denied."""
        response = client.patch(
            f"/api/v1/categories/{created_category['id']}",
            json={"name": "Hacked"},
            headers=second_auth_headers,
        )

        assert response.status_code == 403

    def test_update_category_system_default_denied(
        self, client, auth_headers, system_default_category
    ):
        """Test cannot modify system default category."""
        response = client.patch(
            f"/api/v1/categories/{system_default_category['id']}",
            json={"name": "Hacked Default"},
            headers=auth_headers,
        )

        assert response.status_code == 403
        assert "Cannot modify system default category" in response.json()["detail"]

    def test_update_category_not_found(self, client, auth_headers):
        """Test updating non-existent category."""
        response = client.patch(
            "/api/v1/categories/99999",
            json={"name": "Ghost"},
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_update_category_unauthenticated(self, client, created_category):
        """Test updating category without auth fails."""
        response = client.patch(
            f"/api/v1/categories/{created_category['id']}",
            json={"name": "Hacked"},
        )

        assert response.status_code == 401


class TestDeleteCategory:
    """Tests for DELETE /api/v1/categories/{id}"""

    def test_delete_category_success(self, client, auth_headers, created_category):
        """Test deleting own category."""
        response = client.delete(
            f"/api/v1/categories/{created_category['id']}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(
            f"/api/v1/categories/{created_category['id']}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    def test_delete_category_access_denied(
        self, client, auth_headers, second_auth_headers, created_category
    ):
        """Test deleting another user's category is denied."""
        response = client.delete(
            f"/api/v1/categories/{created_category['id']}",
            headers=second_auth_headers,
        )

        assert response.status_code == 403

    def test_delete_category_system_default_denied(
        self, client, auth_headers, system_default_category
    ):
        """Test cannot delete system default category."""
        response = client.delete(
            f"/api/v1/categories/{system_default_category['id']}",
            headers=auth_headers,
        )

        assert response.status_code == 403
        assert "Cannot modify system default category" in response.json()["detail"]

    def test_delete_category_not_found(self, client, auth_headers):
        """Test deleting non-existent category."""
        response = client.delete("/api/v1/categories/99999", headers=auth_headers)

        assert response.status_code == 404

    def test_delete_category_unauthenticated(self, client, created_category):
        """Test deleting category without auth fails."""
        response = client.delete(f"/api/v1/categories/{created_category['id']}")

        assert response.status_code == 401
