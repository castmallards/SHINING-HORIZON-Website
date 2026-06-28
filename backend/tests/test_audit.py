"""Audit log and paginated catalog list tests."""

import uuid

import pytest
from tests.conftest import csrf_headers

from app.database import SessionLocal
from app.models.category import Category, CategoryType
from app.services.audit import _initial_snapshot


def test_initial_snapshot_records_create_fields():
    snap = _initial_snapshot({
        "name": "Motor",
        "slug": "motor",
        "status": "draft",
        "description": "",
        "image": None,
    })
    assert snap["name"] == [None, "Motor"]
    assert snap["slug"] == [None, "motor"]
    assert "description" not in snap
    assert "image" not in snap


@pytest.fixture
def category_id():
    db = SessionLocal()
    try:
        slug = f"audit-cat-{uuid.uuid4().hex[:8]}"
        cat = Category(
            name="Audit Test Cat",
            slug=slug,
            type=CategoryType.SIMPLE,
            description="For audit tests",
        )
        db.add(cat)
        db.commit()
        db.refresh(cat)
        return cat.id
    finally:
        db.close()


def test_categories_list_paginated(auth_client, category_id):
    response = auth_client.get("/api/categories/?skip=0&limit=5")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert "total" in body
    assert isinstance(body["items"], list)
    assert body["total"] >= 1


def test_audit_list_includes_user_and_entity_meta(auth_client, category_id):
    response = auth_client.get("/api/audit/?limit=5")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    if body["items"]:
        row = body["items"][0]
        assert "username" in row
        assert "full_name" in row
        assert "entity_exists" in row
        assert "entity_slug" in row


def test_create_product_writes_audit_changes(auth_client, category_id):
    part = f"AUD-{uuid.uuid4().hex[:8]}"
    created = auth_client.post(
        "/api/products/",
        json={
            "name": f"Audit Product {part}",
            "category_id": category_id,
            "part_number": part,
            "status": "draft",
        },
        headers=csrf_headers(auth_client),
    )
    assert created.status_code == 200
    product_id = created.json()["id"]

    audit = auth_client.get(f"/api/audit/?entity_type=product&action=create&limit=10")
    assert audit.status_code == 200
    items = audit.json()["items"]
    match = next((i for i in items if i.get("entity_id") == product_id), None)
    assert match is not None
    assert match.get("entity_slug")
    assert match.get("entity_exists") is True
    changes = match.get("changes") or {}
    assert changes.get("part_number") == [None, part]
