"""Wipe catalog data and seed a small demo catalog (Phase 6 prep).

Keeps:
  * users (super_admin / admin)
  * audit_log (kept as historical record; new entries will append)

Wipes:
  * products
  * subcategories
  * categories
  * brands

Then seeds:
  * 11 categories matching the existing public/categories/*.{png,jpg,webp} images
  * a handful of subcategories under the detailed ones
  * ~25 brands using public/brands/*.png logos
  * ~14 demo products with images from public/products/

Run:
    cd backend && python -m scripts.seed_demo_data
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Allow running as "python -m scripts.seed_demo_data" from backend/
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


# ──────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    return _SLUG_RE.sub("-", text.lower()).strip("-")


def img_category(filename: str) -> str:
    return f"/static/categories/{filename}"


def img_brand(filename: str) -> str:
    return f"/static/brands/{filename}"


def img_product(filename: str) -> str:
    return f"/static/products/{filename}"


# ──────────────────────────────────────────────────────────────────────
# Seed data
# ──────────────────────────────────────────────────────────────────────

CATEGORIES = [
    {
        "name": "Industrial Automation",
        "type": CategoryType.DETAILED,
        "image": img_category("industrial automation.png"),
        "tagline": "PLCs, VFDs, HMIs & More",
        "description": "Programmable logic controllers, variable frequency drives, HMIs, sensors, and complete automation systems for factories and process plants.",
        "subcategories": [
            {"name": "PLC Controllers", "description": "Programmable Logic Controllers from leading manufacturers"},
            {"name": "Variable Frequency Drives", "description": "VFDs for motor speed control and energy savings"},
            {"name": "HMI & Touch Panels", "description": "Human-machine interfaces and operator panels"},
        ],
    },
    {
        "name": "Electrical Products",
        "type": CategoryType.DETAILED,
        "image": img_category("electrical products.jpg"),
        "tagline": "Cables, Breakers & More",
        "description": "Industrial cables, circuit breakers, motor starters, distribution boards and electrical accessories.",
        "subcategories": [
            {"name": "Circuit Breakers", "description": "MCBs, MCCBs and air circuit breakers"},
            {"name": "Cables & Wires", "description": "Power, control and instrumentation cables"},
        ],
    },
    {
        "name": "Lifting Equipment",
        "type": CategoryType.DETAILED,
        "image": img_category("lifting-equipment.jpg"),
        "tagline": "Chain Hoists, Wire Ropes & More",
        "description": "Chain hoists, wire rope hoists, slings, shackles and complete lifting solutions for industrial use.",
        "subcategories": [
            {"name": "Chain Hoists", "description": "Manual and electric chain hoists"},
            {"name": "Wire Rope & Slings", "description": "Wire rope hoists, slings and rigging"},
            {"name": "Shackles & Hardware", "description": "Shackles, hooks, turnbuckles and clamps"},
        ],
    },
    {
        "name": "Pneumatic Products",
        "type": CategoryType.DETAILED,
        "image": img_category("pneumatic products.png"),
        "tagline": "Cylinders, Valves & More",
        "description": "Pneumatic cylinders, valves, FRL units and air preparation equipment.",
        "subcategories": [
            {"name": "Cylinders", "description": "Pneumatic actuators and cylinders"},
            {"name": "Valves", "description": "Solenoid, manual and process valves"},
        ],
    },
    {
        "name": "Plumbing Products",
        "type": CategoryType.SIMPLE,
        "image": img_category("plumbing products.webp"),
        "tagline": "Valves, Pipes & Fittings",
        "description": "Industrial plumbing supplies — valves, pipes, fittings and accessories.",
        "subcategories": [],
    },
    {
        "name": "Lighting Products",
        "type": CategoryType.SIMPLE,
        "image": img_category("lighting products.jpg"),
        "tagline": "LED & Industrial Lighting",
        "description": "LED industrial lighting, high bays, floodlights and explosion-proof lighting.",
        "subcategories": [],
    },
    {
        "name": "Safety Products",
        "type": CategoryType.DETAILED,
        "image": img_category("safety products.jpg"),
        "tagline": "PPE & Fire Safety",
        "description": "Personal protective equipment, fire safety, fall protection and industrial safety supplies.",
        "subcategories": [
            {"name": "Personal Protective Equipment", "description": "Helmets, gloves, glasses, footwear"},
            {"name": "Fire Safety", "description": "Fire extinguishers, alarms and accessories"},
        ],
    },
    {
        "name": "Cleaning Products",
        "type": CategoryType.SIMPLE,
        "image": img_category("cleaning products.webp"),
        "tagline": "Industrial & Commercial",
        "description": "Industrial cleaning chemicals, equipment and accessories for commercial and industrial facilities.",
        "subcategories": [],
    },
    {
        "name": "HVAC & Spare Parts",
        "type": CategoryType.SIMPLE,
        "image": img_category("hvac & spare parts.jpg"),
        "tagline": "AC, Chillers & Parts",
        "description": "Air conditioning, chillers, ventilation equipment and HVAC spare parts.",
        "subcategories": [],
    },
    {
        "name": "Maintenance & Services",
        "type": CategoryType.SIMPLE,
        "image": img_category("maintenance & services.jpg"),
        "tagline": "Repair & Programming",
        "description": "Equipment repair, PLC programming, maintenance contracts and engineering services.",
        "subcategories": [],
    },
    {
        "name": "Tools",
        "type": CategoryType.SIMPLE,
        "image": img_category("tools.webp"),
        "tagline": "Hand & Power Tools",
        "description": "Hand tools, power tools and professional tool kits for industrial and commercial use.",
        "subcategories": [],
    },
]


BRANDS = [
    {"name": "Siemens", "logo": img_brand("Siemens.png"), "country": "Germany",
     "website_url": "https://www.siemens.com",
     "description": "Global leader in automation, drives and electrification."},
    {"name": "ABB", "logo": img_brand("brand1.png"), "country": "Switzerland",
     "website_url": "https://www.abb.com",
     "description": "Power and automation technologies for utility and industry."},
    {"name": "Schneider Electric", "logo": img_brand("brand2.png"), "country": "France",
     "website_url": "https://www.se.com",
     "description": "Energy management and automation solutions."},
    {"name": "Allen-Bradley", "logo": img_brand("brand3.png"), "country": "USA",
     "description": "Rockwell Automation industrial automation brand."},
    {"name": "Mitsubishi Electric", "logo": img_brand("brand4.png"), "country": "Japan",
     "description": "Factory automation, drives and PLCs."},
    {"name": "Omron", "logo": img_brand("brand5.png"), "country": "Japan",
     "description": "Industrial automation, sensing and control."},
    {"name": "Danfoss", "logo": img_brand("brand6.png"), "country": "Denmark",
     "description": "Drives, heating and cooling components."},
    {"name": "Phoenix Contact", "logo": img_brand("brand7.png"), "country": "Germany",
     "description": "Connection technology and industrial automation."},
    {"name": "Pepperl+Fuchs", "logo": img_brand("brand8.png"), "country": "Germany",
     "description": "Industrial sensors and explosion protection."},
    {"name": "WEG", "logo": img_brand("brand9.png"), "country": "Brazil",
     "description": "Electric motors, drives and energy solutions."},
    {"name": "Legrand", "logo": img_brand("brand10.png"), "country": "France",
     "description": "Electrical and digital building infrastructure."},
    {"name": "Hager", "logo": img_brand("brand11.png"), "country": "Germany",
     "description": "Electrical installation systems."},
    {"name": "Eaton", "logo": img_brand("brand12.png"), "country": "Ireland",
     "description": "Power management solutions."},
    {"name": "Festo", "logo": img_brand("brand13.png"), "country": "Germany",
     "description": "Pneumatic and electric automation technology."},
    {"name": "SMC", "logo": img_brand("brand14.png"), "country": "Japan",
     "description": "Pneumatic control engineering."},
    {"name": "Parker Hannifin", "logo": img_brand("brand15.png"), "country": "USA",
     "description": "Motion and control technologies."},
    {"name": "Bosch Rexroth", "logo": img_brand("brand16.png"), "country": "Germany",
     "description": "Drive and control technologies."},
    {"name": "Crosby", "logo": img_brand("crosby-logo.png"), "country": "USA",
     "description": "Lifting and rigging hardware."},
    {"name": "Yale", "logo": img_brand("yale-logo.png"), "country": "USA",
     "description": "Hoists and material handling."},
    {"name": "Kito", "logo": img_brand("kito-logo.png"), "country": "Japan",
     "description": "Chain hoists and lifting equipment."},
    {"name": "Pewag", "logo": img_brand("pewag-logo.png"), "country": "Austria",
     "description": "Chain technology for lifting and lashing."},
    {"name": "Gunnebo", "logo": img_brand("gunnebo-logo.png"), "country": "Sweden",
     "description": "Lifting hardware and rigging."},
    {"name": "Elephant", "logo": img_brand("elephant-logo.png"), "country": "Japan",
     "description": "Hoists and cranes."},
    {"name": "Ingersoll Rand", "logo": img_brand("ingersoll-rand-logo.png"), "country": "USA",
     "description": "Compressed air and industrial tools."},
    {"name": "3M", "logo": img_brand("aaw44ogzy.png"), "country": "USA",
     "description": "PPE, safety and industrial products."},
]


# Each product references category by name, optional subcategory by name, optional brand by name.
PRODUCTS = [
    # Industrial Automation -> PLC Controllers
    {
        "category": "Industrial Automation", "subcategory": "PLC Controllers", "brand": "Siemens",
        "name": "SIMATIC S7-1200 CPU 1214C", "part_number": "6ES7214-1AG40-0XB0",
        "image": img_product("plc.webp"),
        "short_description": "Compact PLC with 14 DI / 10 DO / 2 AI for small to medium machines.",
        "description": "The SIMATIC S7-1200 CPU 1214C is a compact PLC designed for medium-scale automation tasks. Integrated PROFINET interface, onboard I/O and high-speed counters.",
        "specs": [
            {"key": "Digital Inputs", "value": "14"},
            {"key": "Digital Outputs", "value": "10 (relay)"},
            {"key": "Analog Inputs", "value": "2 (0–10V)"},
            {"key": "Communication", "value": "PROFINET"},
            {"key": "Power Supply", "value": "AC 120/240V"},
        ],
    },
    {
        "category": "Industrial Automation", "subcategory": "PLC Controllers", "brand": "Allen-Bradley",
        "name": "MicroLogix 1400 1766-L32BWA", "part_number": "1766-L32BWA",
        "image": img_product("product1.png"),
        "short_description": "Expandable micro PLC with 32 I/O and embedded Ethernet/IP.",
        "description": "Compact controller for small standalone machines with embedded EtherNet/IP and an LCD operator interface.",
        "specs": [
            {"key": "Digital I/O", "value": "20 In / 12 Out"},
            {"key": "Ethernet", "value": "10/100 EtherNet/IP"},
        ],
    },
    # Industrial Automation -> VFD
    {
        "category": "Industrial Automation", "subcategory": "Variable Frequency Drives", "brand": "ABB",
        "name": "ACS580 General Purpose Drive 11kW", "part_number": "ACS580-01-026A-4",
        "image": img_product("product2.png"),
        "short_description": "11 kW industrial VFD with built-in EMC filter.",
        "description": "Compact wall-mount drive engineered for HVAC, water and general industrial applications.",
        "specs": [
            {"key": "Power Rating", "value": "11 kW"},
            {"key": "Voltage", "value": "380...480 V"},
            {"key": "Protection", "value": "IP21 (IP55 optional)"},
        ],
    },
    {
        "category": "Industrial Automation", "subcategory": "HMI & Touch Panels", "brand": "Siemens",
        "name": "SIMATIC HMI KTP700 Basic 7\"", "part_number": "6AV2123-2GB03-0AX0",
        "image": img_product("product3.png"),
        "short_description": "7-inch touch panel with PROFINET, 800×480 resolution.",
        "description": "Cost-effective basic HMI panel for visualisation tasks of small to medium machines.",
        "specs": [
            {"key": "Display", "value": "7\" TFT, 64K colors"},
            {"key": "Resolution", "value": "800×480"},
            {"key": "Touch", "value": "Resistive"},
        ],
    },

    # Electrical -> Circuit Breakers
    {
        "category": "Electrical Products", "subcategory": "Circuit Breakers", "brand": "Schneider Electric",
        "name": "Acti9 iC60N MCB 32A C-Curve 3P", "part_number": "A9F44332",
        "image": img_product("product4.png"),
        "short_description": "Three-phase miniature circuit breaker, 32A C-curve.",
        "description": "Reliable miniature circuit breaker for distribution boards in commercial and industrial buildings.",
        "specs": [
            {"key": "Rated Current", "value": "32 A"},
            {"key": "Poles", "value": "3"},
            {"key": "Breaking Capacity", "value": "10 kA"},
        ],
    },
    {
        "category": "Electrical Products", "subcategory": "Cables & Wires", "brand": "Legrand",
        "name": "Industrial Power Cable 4×16mm² Cu/PVC", "part_number": "PWR-4X16-CU",
        "image": img_product("product5.png"),
        "short_description": "Four-core copper power cable, PVC insulated, per metre.",
        "description": "Multi-core power cable for industrial distribution. Supplied per linear metre on request.",
        "specs": [
            {"key": "Cores", "value": "4 × 16 mm²"},
            {"key": "Insulation", "value": "PVC"},
            {"key": "Voltage Rating", "value": "0.6/1 kV"},
        ],
    },

    # Lifting -> Chain Hoists
    {
        "category": "Lifting Equipment", "subcategory": "Chain Hoists", "brand": "Kito",
        "name": "Kito CB Manual Chain Block 2 Ton x 3m", "part_number": "CB020",
        "image": img_product("Hoist.webp"),
        "short_description": "Manual chain hoist 2 ton capacity, 3 m lift height.",
        "description": "Compact, lightweight manual chain hoist suitable for general industrial lifting.",
        "specs": [
            {"key": "Capacity", "value": "2 Ton"},
            {"key": "Standard Lift", "value": "3 m"},
            {"key": "Test Load", "value": "1.5× WLL"},
        ],
    },
    {
        "category": "Lifting Equipment", "subcategory": "Wire Rope & Slings", "brand": "Crosby",
        "name": "Wire Rope Sling 16mm × 2m EE", "part_number": "WRS-16-2M",
        "image": img_product("Lifting Slings.jpg"),
        "short_description": "16 mm wire rope sling with eye-eye terminations, 2 m length.",
        "description": "Heavy-duty wire rope sling for general industrial lifting. Conforms to applicable lifting standards.",
        "specs": [
            {"key": "Diameter", "value": "16 mm"},
            {"key": "Length", "value": "2 m"},
            {"key": "Termination", "value": "Eye-Eye flemish"},
        ],
    },
    {
        "category": "Lifting Equipment", "subcategory": "Shackles & Hardware", "brand": "Crosby",
        "name": "Crosby G-2130 Bow Shackle 6.5T", "part_number": "G-2130-6.5",
        "image": img_product("Shackles.jfif"),
        "short_description": "Bolt-type bow shackle with safety pin, 6.5 ton WLL.",
        "description": "Forged alloy bow shackle with bolt, nut and cotter pin. Quenched and tempered.",
        "specs": [
            {"key": "Working Load Limit", "value": "6.5 t"},
            {"key": "Pin Type", "value": "Bolt + Cotter"},
            {"key": "Material", "value": "Forged alloy steel"},
        ],
    },

    # Pneumatic -> Cylinders
    {
        "category": "Pneumatic Products", "subcategory": "Cylinders", "brand": "Festo",
        "name": "DSBC Standard Cylinder Ø50 × 200mm", "part_number": "DSBC-50-200-PPVA-N3",
        "image": img_product("product6.png"),
        "short_description": "ISO 15552 standard pneumatic cylinder, bore 50 mm, stroke 200 mm.",
        "description": "Double-acting pneumatic cylinder with adjustable cushioning, ISO 15552 mounting.",
        "specs": [
            {"key": "Bore", "value": "50 mm"},
            {"key": "Stroke", "value": "200 mm"},
            {"key": "Operating Pressure", "value": "0.6...12 bar"},
        ],
    },
    {
        "category": "Pneumatic Products", "subcategory": "Valves", "brand": "SMC",
        "name": "SY5120 5/2 Solenoid Valve 24VDC", "part_number": "SY5120-5LZD-01",
        "image": img_product("product7.png"),
        "short_description": "5-port 2-position solenoid valve, 24 VDC, G1/8 ports.",
        "description": "Compact solenoid valve for pneumatic actuator control. Manual override included.",
        "specs": [
            {"key": "Function", "value": "5/2 single solenoid"},
            {"key": "Coil Voltage", "value": "24 VDC"},
            {"key": "Port Size", "value": "G1/8"},
        ],
    },

    # Safety -> PPE
    {
        "category": "Safety Products", "subcategory": "Personal Protective Equipment", "brand": "3M",
        "name": "3M H-700 Hard Hat White (Type 1)", "part_number": "H-701V",
        "image": img_product("product8.png"),
        "short_description": "ANSI Z89.1 Type 1 vented hard hat with ratchet suspension.",
        "description": "Lightweight industrial hard hat with 4-point ratchet suspension and accessory slots.",
        "specs": [
            {"key": "Standard", "value": "ANSI Z89.1 Type 1 Class C"},
            {"key": "Suspension", "value": "4-point ratchet"},
            {"key": "Color", "value": "White"},
        ],
    },

    # Tools (simple category, no subcategory)
    {
        "category": "Tools", "subcategory": None, "brand": "Ingersoll Rand",
        "name": "Ingersoll Rand 2235TiMAX 1/2\" Impact Wrench", "part_number": "2235TiMAX",
        "image": img_product("product.png"),
        "short_description": "1/2-inch heavy-duty pneumatic impact wrench, 1,350 ft-lb max torque.",
        "description": "Industrial pneumatic impact wrench with titanium hammer case for low weight and high durability.",
        "specs": [
            {"key": "Drive", "value": "1/2 inch"},
            {"key": "Max Torque", "value": "1,350 ft-lb"},
            {"key": "Weight", "value": "1.95 kg"},
        ],
    },

    # Lighting (simple)
    {
        "category": "Lighting Products", "subcategory": None, "brand": "Eaton",
        "name": "LED High Bay 200W IP65 5000K", "part_number": "HB-200-50K",
        "image": img_product("capture.png"),
        "short_description": "200W LED high bay luminaire for warehouses and factories.",
        "description": "High-efficiency LED high bay with aluminium heat sink and 5000K daylight colour temperature.",
        "specs": [
            {"key": "Power", "value": "200 W"},
            {"key": "Luminous Flux", "value": "26,000 lm"},
            {"key": "IP Rating", "value": "IP65"},
            {"key": "Color Temp", "value": "5000 K"},
        ],
    },
]


# ──────────────────────────────────────────────────────────────────────
# Wipe + seed
# ──────────────────────────────────────────────────────────────────────

def wipe(db) -> None:
    print("Wiping catalog tables...")
    deleted_p = db.query(Product).delete(synchronize_session=False)
    deleted_s = db.query(Subcategory).delete(synchronize_session=False)
    deleted_c = db.query(Category).delete(synchronize_session=False)
    deleted_b = db.query(Brand).delete(synchronize_session=False)
    db.commit()
    print(f"  deleted: {deleted_p} products, {deleted_s} subcategories, {deleted_c} categories, {deleted_b} brands")


def seed(db) -> None:
    print("Seeding brands...")
    brand_by_name: dict[str, Brand] = {}
    for order, b in enumerate(BRANDS, start=1):
        brand = Brand(
            name=b["name"],
            slug=slugify(b["name"]),
            logo=b.get("logo"),
            description=b.get("description"),
            website_url=b.get("website_url"),
            country=b.get("country"),
            display_order=order,
            is_active=True,
            status=ContentStatus.PUBLISHED,
        )
        db.add(brand)
        brand_by_name[b["name"]] = brand
    db.flush()
    print(f"  inserted {len(brand_by_name)} brands")

    print("Seeding categories + subcategories...")
    cat_by_name: dict[str, Category] = {}
    sub_by_key: dict[tuple[str, str], Subcategory] = {}
    for order, c in enumerate(CATEGORIES, start=1):
        cat = Category(
            name=c["name"],
            slug=slugify(c["name"]),
            type=c["type"],
            description=c["description"],
            image=c["image"],
            hero_title=c["name"],
            hero_description=c["tagline"],
            display_order=order,
            is_active=True,
            show_on_home=True,
            status=ContentStatus.PUBLISHED,
            meta_title=f"{c['name']} — Shining Horizon Trading",
            meta_description=c["description"][:300],
        )
        db.add(cat)
        db.flush()
        cat_by_name[c["name"]] = cat

        for s_order, s in enumerate(c.get("subcategories", []), start=1):
            sub = Subcategory(
                category_id=cat.id,
                name=s["name"],
                slug=slugify(s["name"]),
                description=s["description"],
                display_order=s_order,
                is_active=True,
                status=ContentStatus.PUBLISHED,
                meta_title=f"{s['name']} — {c['name']}",
                meta_description=s["description"][:300],
            )
            db.add(sub)
            sub_by_key[(c["name"], s["name"])] = sub
    db.flush()
    print(f"  inserted {len(cat_by_name)} categories, {len(sub_by_key)} subcategories")

    print("Seeding products...")
    seeded_count = 0
    for order, p in enumerate(PRODUCTS, start=1):
        cat = cat_by_name.get(p["category"])
        if not cat:
            print(f"  ! skip {p['name']} — category {p['category']!r} missing")
            continue
        sub = sub_by_key.get((p["category"], p["subcategory"])) if p.get("subcategory") else None
        brand = brand_by_name.get(p["brand"]) if p.get("brand") else None

        prod = Product(
            category_id=cat.id,
            subcategory_id=sub.id if sub else None,
            brand_id=brand.id if brand else None,
            name=p["name"],
            slug=slugify(p["name"]),
            part_number=p.get("part_number"),
            description=p["description"],
            short_description=p["short_description"],
            image=p["image"],
            display_order=order,
            is_active=True,
            is_featured=(order <= 4),
            status=ContentStatus.PUBLISHED,
            meta_title=f"{p['name']} — Shining Horizon Trading",
            meta_description=p["short_description"][:300],
            datasheet_url=None,
        )
        prod.specifications_list = p.get("specs", [])
        prod.gallery_list = []  # main image only for demo
        db.add(prod)
        seeded_count += 1
    db.commit()
    print(f"  inserted {seeded_count} products")

    invalidate_public()
    print("Public cache invalidated.")


def main() -> None:
    db = SessionLocal()
    try:
        wipe(db)
        seed(db)
        c = db.query(Category).count()
        s = db.query(Subcategory).count()
        b = db.query(Brand).count()
        p = db.query(Product).count()
        print(f"\nFinal counts -> categories={c}  subcategories={s}  brands={b}  products={p}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
