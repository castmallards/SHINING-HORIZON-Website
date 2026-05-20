"""CSV product import — upsert by part number."""

import uuid

import pytest
from tests.conftest import csrf_headers

from app.database import SessionLocal
from app.models.category import Category, CategoryType
from app.models.product import Product
from app.services.product import ProductService


@pytest.fixture
def import_category():
    """Category name used in CSV rows."""
    db = SessionLocal()
    try:
        cat = db.query(Category).first()
        if not cat:
            slug = f"import-cat-{uuid.uuid4().hex[:8]}"
            cat = Category(
                name="Import Test Category",
                slug=slug,
                type=CategoryType.DETAILED,
                description="For import tests",
            )
            db.add(cat)
            db.commit()
            db.refresh(cat)
        return {"id": cat.id, "name": cat.name}
    finally:
        db.close()


def _csv_row(category_name: str, name: str, part_number: str = "", **extra) -> str:
    row = {
        "category_name": category_name,
        "subcategory_name": "",
        "brand_name": "",
        "name": name,
        "part_number": part_number,
        "short_description": extra.get("short_description", ""),
        "description": extra.get("description", ""),
        "display_order": str(extra.get("display_order", "0")),
    }
    return ",".join(
        [
            row["category_name"],
            row["subcategory_name"],
            row["brand_name"],
            row["name"],
            row["part_number"],
            row["short_description"],
            row["description"],
            row["display_order"],
        ]
    )


def _import_csv(auth_client, body: str):
    return auth_client.post(
        "/api/import/products",
        files={"file": ("products.csv", body.encode("utf-8"), "text/csv")},
        headers=csrf_headers(auth_client),
    )


def test_import_creates_product_with_part_number(auth_client, import_category):
    part = f"IMP-{uuid.uuid4().hex[:8]}"
    header = "category_name,subcategory_name,brand_name,name,part_number,short_description,description,display_order"
    row = _csv_row(import_category["name"], "Import Widget", part, short_description="Short")
    response = _import_csv(auth_client, f"{header}\n{row}")

    assert response.status_code == 200
    body = response.json()
    assert body["created"] == 1
    assert body["updated"] == 0
    assert body["errors"] == []

    db = SessionLocal()
    try:
        product = ProductService.get_by_part_number(db, part)
        assert product is not None
        assert product.name == "Import Widget"
        assert product.short_description == "Short"
    finally:
        db.close()


def test_import_same_part_number_updates_existing(auth_client, import_category):
    part = f"UPSERT-{uuid.uuid4().hex[:8]}"
    header = "category_name,subcategory_name,brand_name,name,part_number,short_description,description,display_order"
    row1 = _csv_row(import_category["name"], "Original Name", part)
    row2 = _csv_row(
        import_category["name"],
        "Updated Name",
        part,
        short_description="New short",
    )

    first = _import_csv(auth_client, f"{header}\n{row1}")
    assert first.status_code == 200
    assert first.json()["created"] == 1

    second = _import_csv(auth_client, f"{header}\n{row2}")
    assert second.status_code == 200
    assert second.json()["created"] == 0
    assert second.json()["updated"] == 1

    db = SessionLocal()
    try:
        product = ProductService.get_by_part_number(db, part)
        assert product is not None
        assert product.name == "Updated Name"
        assert product.short_description == "New short"
    finally:
        db.close()


def test_import_duplicate_part_number_in_one_file(auth_client, import_category):
    part = f"BATCH-{uuid.uuid4().hex[:8]}"
    header = "category_name,subcategory_name,brand_name,name,part_number,short_description,description,display_order"
    row1 = _csv_row(import_category["name"], "First Row", part)
    row2 = _csv_row(import_category["name"], "Second Row", part)

    response = _import_csv(auth_client, f"{header}\n{row1}\n{row2}")
    assert response.status_code == 200
    body = response.json()
    assert body["created"] == 1
    assert body["updated"] == 1

    db = SessionLocal()
    try:
        assert ProductService.get_by_part_number(db, part) is not None
        assert (
            db.query(Product)
            .filter(Product.part_number == part)
            .count()
            == 1
        )
    finally:
        db.close()


def test_import_without_part_number_creates(auth_client, import_category):
    header = "category_name,subcategory_name,brand_name,name,part_number,short_description,description,display_order"
    name = f"No Part {uuid.uuid4().hex[:8]}"
    row = _csv_row(import_category["name"], name, "")

    response = _import_csv(auth_client, f"{header}\n{row}")
    assert response.status_code == 200
    assert response.json()["created"] == 1
