import pytest


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


CATEGORIES_URL = "/api/v1/categories"
ORDER_URL = f"{CATEGORIES_URL}/order"


@pytest.fixture
def system_group(db_session):
    """A system group with three categories, as the seeded catalog has (IDs in default order)."""
    from app.models import Category
    from app.models.category import CategoryType

    group = Category(user_id=None, name="Food & Dining", type=CategoryType.EXPENSE, is_group=True)
    db_session.add(group)
    db_session.flush()
    children = [
        Category(user_id=None, parent_id=group.id, name=name, type=CategoryType.EXPENSE, icon=icon)
        for name, icon in [("Groceries", "🍏"), ("Restaurants & Bars", "🍽️"), ("Coffee Shops", "☕")]
    ]
    db_session.add_all(children)
    db_session.commit()
    return {"id": group.id, "children": [child.id for child in children]}


def child_ids(client, headers, group_id):
    categories = client.get(CATEGORIES_URL, headers=headers).json()
    return [category["id"] for category in categories if category["parent_id"] == group_id]


class TestCategoryOrder:
    """Tests for PUT /api/v1/categories/order (drag and drop in Settings › Categories)"""

    def test_default_order_is_the_catalogs(self, client, auth_headers, system_group):
        assert child_ids(client, auth_headers, system_group["id"]) == system_group["children"]

    def test_icon_is_listed(self, client, auth_headers, system_group):
        categories = client.get(CATEGORIES_URL, headers=auth_headers).json()

        assert [c["icon"] for c in categories if c["parent_id"] == system_group["id"]] == ["🍏", "🍽️", "☕"]

    def test_reorders_a_group(self, client, auth_headers, system_group):
        new_order = list(reversed(system_group["children"]))

        response = client.put(ORDER_URL, json={"category_ids": new_order}, headers=auth_headers)

        assert response.status_code == 204
        assert child_ids(client, auth_headers, system_group["id"]) == new_order

    def test_reordering_again_replaces_the_order(self, client, auth_headers, system_group):
        a, b, c = system_group["children"]
        client.put(ORDER_URL, json={"category_ids": [c, b, a]}, headers=auth_headers)

        client.put(ORDER_URL, json={"category_ids": [b, a, c]}, headers=auth_headers)

        assert child_ids(client, auth_headers, system_group["id"]) == [b, a, c]

    def test_order_is_per_user(self, client, auth_headers, second_auth_headers, system_group):
        client.put(ORDER_URL, json={"category_ids": list(reversed(system_group["children"]))}, headers=auth_headers)

        assert child_ids(client, second_auth_headers, system_group["id"]) == system_group["children"]

    def test_new_category_goes_to_the_end(self, client, auth_headers, system_group):
        new_order = list(reversed(system_group["children"]))
        client.put(ORDER_URL, json={"category_ids": new_order}, headers=auth_headers)

        created = client.post(
            CATEGORIES_URL,
            json={"name": "Bakery", "type": "expense", "parent_id": system_group["id"], "icon": "🥐"},
            headers=auth_headers,
        ).json()

        assert created["icon"] == "🥐"
        assert child_ids(client, auth_headers, system_group["id"]) == [*new_order, created["id"]]

    def test_own_categories_can_be_ordered_with_system_ones(self, client, auth_headers, system_group):
        own = client.post(
            CATEGORIES_URL,
            json={"name": "Bakery", "type": "expense", "parent_id": system_group["id"]},
            headers=auth_headers,
        ).json()["id"]
        new_order = [own, *system_group["children"]]

        client.put(ORDER_URL, json={"category_ids": new_order}, headers=auth_headers)

        assert child_ids(client, auth_headers, system_group["id"]) == new_order

    @pytest.mark.parametrize(
        "pick",
        [
            lambda children, group: children[:2],  # not the whole group
            lambda children, group: [*children, children[0]],  # duplicate
            lambda children, group: [*children, 999_999],  # unknown
            lambda children, group: [group, *children],  # the group itself
        ],
    )
    def test_rejects_anything_but_one_whole_group(self, client, auth_headers, system_group, pick):
        category_ids = pick(system_group["children"], system_group["id"])

        response = client.put(ORDER_URL, json={"category_ids": category_ids}, headers=auth_headers)

        assert response.status_code == 422
        assert child_ids(client, auth_headers, system_group["id"]) == system_group["children"]

    def test_rejects_categories_from_two_groups(self, client, auth_headers, system_group, created_category):
        category_ids = [*system_group["children"], created_category["id"]]

        response = client.put(ORDER_URL, json={"category_ids": category_ids}, headers=auth_headers)

        assert response.status_code == 422

    def test_cannot_see_or_order_another_users_categories(
        self, client, auth_headers, second_auth_headers, created_category
    ):
        response = client.put(ORDER_URL, json={"category_ids": [created_category["id"]]}, headers=second_auth_headers)

        assert response.status_code == 422

    def test_requires_session(self, client, system_group):
        response = client.put(ORDER_URL, json={"category_ids": system_group["children"]})

        assert response.status_code == 401
