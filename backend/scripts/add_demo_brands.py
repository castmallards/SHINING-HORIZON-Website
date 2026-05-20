"""Add extra published brands for local testing (idempotent by name).

Does not delete existing data. Skips brands whose name already exists.

Run from backend/:
    python -m scripts.add_demo_brands
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
BACKEND_DIR = THIS_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.cache import invalidate_public  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.models._common import ContentStatus  # noqa: E402
from app.models.brand import Brand  # noqa: E402

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    return _SLUG_RE.sub("-", text.lower()).strip("-")


def img_brand(filename: str) -> str:
    return f"/static/brands/{filename}"


# Extra brands for marquee testing (logos under public/brands/).
EXTRA_BRANDS = [
    {"name": "Allen-Bradley", "logo": img_brand("brand3.png"), "country": "USA"},
    {"name": "Mitsubishi Electric", "logo": img_brand("brand4.png"), "country": "Japan"},
    {"name": "Omron", "logo": img_brand("brand5.png"), "country": "Japan"},
    {"name": "Danfoss", "logo": img_brand("brand6.png"), "country": "Denmark"},
    {"name": "Phoenix Contact", "logo": img_brand("brand7.png"), "country": "Germany"},
    {"name": "Pepperl+Fuchs", "logo": img_brand("brand8.png"), "country": "Germany"},
    {"name": "WEG", "logo": img_brand("brand9.png"), "country": "Brazil"},
    {"name": "Legrand", "logo": img_brand("brand10.png"), "country": "France"},
    {"name": "Hager", "logo": img_brand("brand11.png"), "country": "Germany"},
    {"name": "Eaton", "logo": img_brand("brand12.png"), "country": "Ireland"},
    {"name": "Festo", "logo": img_brand("brand13.png"), "country": "Germany"},
    {"name": "SMC", "logo": img_brand("brand14.png"), "country": "Japan"},
    {"name": "Parker Hannifin", "logo": img_brand("brand15.png"), "country": "USA"},
    {"name": "Bosch Rexroth", "logo": img_brand("brand16.png"), "country": "Germany"},
    {"name": "Yale", "logo": img_brand("yale-logo.png"), "country": "USA"},
    {"name": "Kito", "logo": img_brand("kito-logo.png"), "country": "Japan"},
]


def main() -> None:
    db = SessionLocal()
    try:
        existing = {b.name for b in db.query(Brand.name).all()}
        added = 0
        order_base = db.query(Brand).count()
        for i, row in enumerate(EXTRA_BRANDS, start=1):
            if row["name"] in existing:
                continue
            db.add(
                Brand(
                    name=row["name"],
                    slug=slugify(row["name"]),
                    logo=row.get("logo"),
                    country=row.get("country"),
                    display_order=order_base + i,
                    is_active=True,
                    status=ContentStatus.PUBLISHED,
                )
            )
            added += 1
        db.commit()
        invalidate_public()
        total = db.query(Brand).filter(Brand.status == ContentStatus.PUBLISHED).count()
        print(f"Added {added} brand(s). Published brands in DB: {total}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
