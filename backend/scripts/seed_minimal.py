"""Minimal demo seed — 5 brands / 5 categories / 4 subcategories / 5 products.

Use this when you want a small representative dataset to walk through every
admin page (categories list, subcategory linkage, brand cards, product detail
with specs and gallery) without filling the catalog with noise.

Idempotent: wipes catalog tables (NOT users / audit log) before reseeding.

Run from the backend directory:
    python -m scripts.seed_minimal
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
from app.models.category import Category, CategoryType  # noqa: E402
from app.models.product import Product  # noqa: E402
from app.models.subcategory import Subcategory  # noqa: E402


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    return _SLUG_RE.sub("-", text.lower()).strip("-")


# ── Demo data ─────────────────────────────────────────────────────────

BRANDS = [
    {"name": "Siemens",            "country": "Germany",     "website_url": "https://www.siemens.com",
     "logo": "/static/brands/Siemens.png",
     "description": "Global leader in automation, drives and electrification."},
    {"name": "ABB",                "country": "Switzerland", "website_url": "https://www.abb.com",
     "logo": "/static/brands/brand1.png",
     "description": "Power and automation technologies for utility and industry."},
    {"name": "Schneider Electric", "country": "France",      "website_url": "https://www.se.com",
     "logo": "/static/brands/brand2.png",
     "description": "Energy management and industrial automation solutions."},
    {"name": "Crosby",             "country": "USA",         "website_url": "https://www.thecrosbygroup.com",
     "logo": "/static/brands/crosby-logo.png",
     "description": "Lifting and rigging hardware — shackles, hooks, blocks."},
    {"name": "3M",                 "country": "USA",         "website_url": "https://www.3m.com",
     "logo": "/static/brands/aaw44ogzy.png",
     "description": "Personal protective equipment, safety and industrial products."},
]

CATEGORIES = [
    {
        "name": "Industrial Automation", "type": CategoryType.DETAILED,
        "image": "/static/categories/industrial automation.png",
        "tagline": "PLCs, VFDs, HMIs & More",
        "description": "Programmable logic controllers, variable frequency drives, HMIs and complete automation systems for factories and process plants.",
        "subcategories": [
            {"name": "PLC Controllers", "description": "Programmable Logic Controllers from leading manufacturers."},
            {"name": "Variable Frequency Drives", "description": "VFDs for motor speed control and energy savings."},
        ],
    },
    {
        "name": "Electrical Products", "type": CategoryType.DETAILED,
        "image": "/static/categories/electrical products.jpg",
        "tagline": "Cables, Breakers & More",
        "description": "Industrial cables, circuit breakers, motor starters, distribution boards and electrical accessories.",
        "subcategories": [
            {"name": "Circuit Breakers", "description": "MCBs, MCCBs and air circuit breakers."},
        ],
    },
    {
        "name": "Lifting Equipment", "type": CategoryType.DETAILED,
        "image": "/static/categories/lifting-equipment.jpg",
        "tagline": "Chain Hoists, Shackles & More",
        "description": "Chain hoists, shackles, slings and complete lifting solutions for industrial use.",
        "subcategories": [
            {"name": "Shackles & Hardware", "description": "Forged shackles, hooks and rigging hardware."},
        ],
    },
    {
        "name": "Safety Products", "type": CategoryType.SIMPLE,
        "image": "/static/categories/safety products.jpg",
        "tagline": "PPE & Fire Safety",
        "description": "Personal protective equipment, fire safety and industrial safety supplies.",
        "subcategories": [],
    },
    {
        "name": "Tools", "type": CategoryType.SIMPLE,
        "image": "/static/categories/tools.webp",
        "tagline": "Hand & Power Tools",
        "description": "Hand tools, pneumatic tools and professional tool kits.",
        "subcategories": [],
    },
]

PRODUCTS = [
    {
        "category": "Industrial Automation", "subcategory": "PLC Controllers", "brand": "Siemens",
        "name": "SIMATIC S7-1200 CPU 1214C", "part_number": "6ES7214-1AG40-0XB0",
        "image": "/static/products/plc.webp",
        "short_description": "Compact PLC with 14 DI / 10 DO / 2 AI for small to medium machines.",
        "description": "The SIMATIC S7-1200 CPU 1214C is a compact PLC designed for medium-scale automation tasks. Integrated PROFINET interface, onboard I/O and high-speed counters.",
        "specs": [
            {"key": "Digital Inputs", "value": "14"},
            {"key": "Digital Outputs", "value": "10 (relay)"},
            {"key": "Analog Inputs", "value": "2 (0-10V)"},
            {"key": "Communication", "value": "PROFINET"},
            {"key": "Power Supply", "value": "AC 120/240V"},
        ],
        "featured": True,
    },
    {
        "category": "Industrial Automation", "subcategory": "Variable Frequency Drives", "brand": "ABB",
        "name": "ACS580 General Purpose Drive 11kW", "part_number": "ACS580-01-026A-4",
        "image": "/static/products/product2.png",
        "short_description": "11 kW industrial VFD with built-in EMC filter.",
        "description": "Compact wall-mount drive engineered for HVAC, water and general industrial applications.",
        "specs": [
            {"key": "Power Rating", "value": "11 kW"},
            {"key": "Voltage", "value": "380...480 V"},
            {"key": "Protection", "value": "IP21 (IP55 optional)"},
        ],
        "featured": True,
    },
    {
        "category": "Electrical Products", "subcategory": "Circuit Breakers", "brand": "Schneider Electric",
        "name": "Acti9 iC60N MCB 32A C-Curve 3P", "part_number": "A9F44332",
        "image": "/static/products/product4.png",
        "short_description": "Three-phase miniature circuit breaker, 32A C-curve.",
        "description": "Reliable miniature circuit breaker for distribution boards in commercial and industrial buildings.",
        "specs": [
            {"key": "Rated Current", "value": "32 A"},
            {"key": "Poles", "value": "3"},
            {"key": "Breaking Capacity", "value": "10 kA"},
        ],
        "featured": True,
    },
    {
        "category": "Lifting Equipment", "subcategory": "Shackles & Hardware", "brand": "Crosby",
        "name": "Crosby G-2130 Bow Shackle 6.5T", "part_number": "G-2130-6.5",
        "image": "/static/products/Shackles.jfif",
        "short_description": "Bolt-type bow shackle with safety pin, 6.5 ton WLL.",
        "description": "Forged alloy bow shackle with bolt, nut and cotter pin. Quenched and tempered.",
        "specs": [
            {"key": "Working Load Limit", "value": "6.5 t"},
            {"key": "Pin Type", "value": "Bolt + Cotter"},
            {"key": "Material", "value": "Forged alloy steel"},
        ],
        "featured": False,
    },
    {
        "category": "Safety Products", "subcategory": None, "brand": "3M",
        "name": "3M H-700 Hard Hat White (Type 1)", "part_number": "H-701V",
        "image": "/static/products/product8.png",
        "short_description": "ANSI Z89.1 Type 1 vented hard hat with 4-point ratchet suspension.",
        "description": "Lightweight industrial hard hat with 4-point ratchet suspension and accessory slots.",
        "specs": [
            {"key": "Standard", "value": "ANSI Z89.1 Type 1 Class C"},
            {"key": "Suspension", "value": "4-point ratchet"},
            {"key": "Color", "value": "White"},
        ],
        "featured": False,
    },
]


def wipe(db) -> None:
    print("Wiping catalog tables...")
    dp = db.query(Product).delete(synchronize_session=False)
    ds = db.query(Subcategory).delete(synchronize_session=False)
    dc = db.query(Category).delete(synchronize_session=False)
    dbk = db.query(Brand).delete(synchronize_session=False)
    db.commit()
    print(f"  removed {dp} products, {ds} subcategories, {dc} categories, {dbk} brands")


def seed(db) -> None:
    brand_by_name: dict[str, Brand] = {}
    for order, b in enumerate(BRANDS, start=1):
        brand = Brand(
            name=b["name"], slug=slugify(b["name"]), logo=b.get("logo"),
            description=b.get("description"), website_url=b.get("website_url"),
            country=b.get("country"), display_order=order, is_active=True,
            status=ContentStatus.PUBLISHED,
        )
        db.add(brand)
        brand_by_name[b["name"]] = brand
    db.flush()
    print(f"  inserted {len(brand_by_name)} brands")

    cat_by_name: dict[str, Category] = {}
    sub_by_key: dict[tuple[str, str], Subcategory] = {}
    for order, c in enumerate(CATEGORIES, start=1):
        cat = Category(
            name=c["name"], slug=slugify(c["name"]), type=c["type"],
            description=c["description"], image=c["image"],
            hero_title=c["name"], hero_description=c["tagline"],
            display_order=order, is_active=True, show_on_home=True,
            status=ContentStatus.PUBLISHED,
            meta_title=f"{c['name']} - Shining Horizon Trading",
            meta_description=c["description"][:300],
        )
        db.add(cat)
        db.flush()
        cat_by_name[c["name"]] = cat

        for s_order, s in enumerate(c.get("subcategories", []), start=1):
            sub = Subcategory(
                category_id=cat.id, name=s["name"], slug=slugify(s["name"]),
                description=s["description"], display_order=s_order,
                is_active=True, status=ContentStatus.PUBLISHED,
                meta_title=f"{s['name']} - {c['name']}",
                meta_description=s["description"][:300],
            )
            db.add(sub)
            sub_by_key[(c["name"], s["name"])] = sub
    db.flush()
    print(f"  inserted {len(cat_by_name)} categories, {len(sub_by_key)} subcategories")

    seeded = 0
    for order, p in enumerate(PRODUCTS, start=1):
        cat = cat_by_name[p["category"]]
        sub = sub_by_key.get((p["category"], p["subcategory"])) if p.get("subcategory") else None
        brand = brand_by_name.get(p["brand"]) if p.get("brand") else None

        prod = Product(
            category_id=cat.id, subcategory_id=sub.id if sub else None,
            brand_id=brand.id if brand else None,
            name=p["name"], slug=slugify(p["name"]),
            part_number=p.get("part_number"),
            description=p["description"], short_description=p["short_description"],
            image=p["image"], display_order=order,
            is_active=True, is_featured=p.get("featured", False),
            status=ContentStatus.PUBLISHED,
            meta_title=f"{p['name']} - Shining Horizon Trading",
            meta_description=p["short_description"][:300],
            datasheet_url=None,
        )
        prod.specifications_list = p.get("specs", [])
        prod.gallery_list = []
        db.add(prod)
        seeded += 1
    db.commit()
    print(f"  inserted {seeded} products")
    invalidate_public()


def main() -> None:
    db = SessionLocal()
    try:
        wipe(db)
        seed(db)
        c = db.query(Category).count()
        s = db.query(Subcategory).count()
        b = db.query(Brand).count()
        p = db.query(Product).count()
        print()
        print(f"Final: categories={c}  subcategories={s}  brands={b}  products={p}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
