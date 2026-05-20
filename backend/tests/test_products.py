"""Product API tests — part number uniqueness (step 1: reject on save)."""

import uuid

import pytest
from tests.conftest import csrf_headers

from app.database import SessionLocal
from app.models.category import Category, CategoryType

@pytest.fixture
def category_id():
    """A category row tests can attach products to."""
    db = SessionLocal()
    try:
        cat = db.query(Category).first()
        if cat:
            return cat.id
        slug = f"test-cat-{uuid.uuid4().hex[:8]}"
        cat = Category(
            name="Test Category",
            slug=slug,
            type=CategoryType.DETAILED,
            description="For pytest",
        )
        db.add(cat)
        db.commit()
        db.refresh(cat)
        return cat.id
    finally:
        db.close()


def _product_payload(category_id: int, part_number: str, name: str | None = None):
    return {
        "name": name or f"Test Product {part_number}",
        "category_id": category_id,
        "part_number": part_number,
    }


def _post_product(client, category_id: int, part_number: str, name: str | None = None):
    return client.post(
        "/api/products/",
        json=_product_payload(category_id, part_number, name),
        headers=csrf_headers(client),
    )


def _put_product(client, product_id: int, json: dict):
    return client.put(
        f"/api/products/{product_id}",
        json=json,
        headers=csrf_headers(client),
    )


def test_create_product_with_part_number(auth_client, category_id):
    part = f"PN-{uuid.uuid4().hex[:8]}"
    response = _post_product(auth_client, category_id, part)
    assert response.status_code == 200
    body = response.json()
    assert body["part_number"] == part


def test_create_duplicate_part_number_returns_409(auth_client, category_id):
    part = f"DUP-{uuid.uuid4().hex[:8]}"
    first = _post_product(auth_client, category_id, part, name="First")
    assert first.status_code == 200

    second = _post_product(auth_client, category_id, part, name="Second")
    assert second.status_code == 409
    assert "already exists" in second.json()["detail"].lower()


def test_update_keep_same_part_number_ok(auth_client, category_id):
    part = f"KEEP-{uuid.uuid4().hex[:8]}"
    created = _post_product(auth_client, category_id, part)
    assert created.status_code == 200
    product_id = created.json()["id"]

    updated = _put_product(
        auth_client,
        product_id,
        {"part_number": part, "name": "Renamed but same part"},
    )
    assert updated.status_code == 200
    assert updated.json()["part_number"] == part


def test_update_to_existing_part_number_returns_409(auth_client, category_id):
    part_a = f"A-{uuid.uuid4().hex[:8]}"
    part_b = f"B-{uuid.uuid4().hex[:8]}"
    _post_product(auth_client, category_id, part_a)
    second = _post_product(auth_client, category_id, part_b, name="Product B")
    product_b_id = second.json()["id"]

    conflict = _put_product(auth_client, product_b_id, {"part_number": part_a})
    assert conflict.status_code == 409


def test_check_part_number_available(auth_client, category_id):
    part = f"CHK-{uuid.uuid4().hex[:8]}"
    result = auth_client.get(
        "/api/products/check-part-number",
        params={"part_number": part},
    )
    assert result.status_code == 200
    body = result.json()
    assert body["available"] is True
    assert body["existing"] is None


def test_check_part_number_taken_after_create(auth_client, category_id):
    part = f"TAKEN-{uuid.uuid4().hex[:8]}"
    assert _post_product(auth_client, category_id, part).status_code == 200

    result = auth_client.get(
        "/api/products/check-part-number",
        params={"part_number": part},
    )
    assert result.status_code == 200
    body = result.json()
    assert body["available"] is False
    assert body["existing"]["id"]
    assert body["existing"]["name"]


def test_check_part_number_exclude_self_on_edit(auth_client, category_id):
    part = f"SELF-{uuid.uuid4().hex[:8]}"
    created = _post_product(auth_client, category_id, part)
    product_id = created.json()["id"]

    result = auth_client.get(
        "/api/products/check-part-number",
        params={"part_number": part, "exclude_id": product_id},
    )
    assert result.status_code == 200
    assert result.json()["available"] is True


def test_create_without_part_number_still_allowed(auth_client, category_id):
    response = auth_client.post(
        "/api/products/",
        json={"name": f"No part {uuid.uuid4().hex[:8]}", "category_id": category_id},
        headers=csrf_headers(auth_client),
    )
    assert response.status_code == 200
    assert response.json().get("part_number") in (None, "")
