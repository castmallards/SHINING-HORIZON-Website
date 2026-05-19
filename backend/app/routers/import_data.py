from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import csv
import io
from typing import List

from ..database import get_db
from ..services.auth import get_current_user
from ..models.user import User
from ..models.category import Category, CategoryType
from ..models.subcategory import Subcategory
from ..models.brand import Brand
from ..services.product import ProductService
from ..cache import invalidate_public
import re

router = APIRouter(prefix="/import", tags=["Import"])

def generate_slug(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug

@router.post("/categories")
async def import_categories(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Import categories from CSV.
    Columns: name, type (simple/detailed), description, hero_title, hero_description, display_order
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV")
    
    content = await file.read()
    decoded = content.decode('utf-8-sig')  # Handle BOM
    reader = csv.DictReader(io.StringIO(decoded))
    
    created = 0
    updated = 0
    errors = []
    
    for row_num, row in enumerate(reader, start=2):
        try:
            name = row.get('name', '').strip()
            if not name:
                continue
            
            slug = generate_slug(name)
            cat_type = CategoryType.DETAILED if row.get('type', '').lower() == 'detailed' else CategoryType.SIMPLE
            
            # Check if exists
            existing = db.query(Category).filter(Category.slug == slug).first()
            
            if existing:
                existing.name = name
                existing.type = cat_type
                existing.description = row.get('description', '').strip() or existing.description
                existing.hero_title = row.get('hero_title', '').strip() or existing.hero_title
                existing.hero_description = row.get('hero_description', '').strip() or existing.hero_description
                existing.display_order = int(row.get('display_order', 0) or 0)
                updated += 1
            else:
                category = Category(
                    name=name,
                    slug=slug,
                    type=cat_type,
                    description=row.get('description', '').strip(),
                    hero_title=row.get('hero_title', '').strip(),
                    hero_description=row.get('hero_description', '').strip(),
                    display_order=int(row.get('display_order', 0) or 0),
                    is_active=True,
                    show_on_home=True
                )
                db.add(category)
                created += 1
                
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
    
    db.commit()
    return {"created": created, "updated": updated, "errors": errors}


@router.post("/subcategories")
async def import_subcategories(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Import subcategories from CSV.
    Columns: category_name, name, description, display_order
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV")
    
    content = await file.read()
    decoded = content.decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(decoded))
    
    created = 0
    updated = 0
    errors = []
    
    for row_num, row in enumerate(reader, start=2):
        try:
            name = row.get('name', '').strip()
            category_name = row.get('category_name', '').strip()
            
            if not name or not category_name:
                continue
            
            # Find category
            category = db.query(Category).filter(Category.name == category_name).first()
            if not category:
                errors.append(f"Row {row_num}: Category '{category_name}' not found")
                continue
            
            slug = generate_slug(name)
            
            # Check if exists
            existing = db.query(Subcategory).filter(
                Subcategory.slug == slug,
                Subcategory.category_id == category.id
            ).first()
            
            if existing:
                existing.name = name
                existing.description = row.get('description', '').strip() or existing.description
                existing.display_order = int(row.get('display_order', 0) or 0)
                updated += 1
            else:
                subcategory = Subcategory(
                    name=name,
                    slug=slug,
                    category_id=category.id,
                    description=row.get('description', '').strip(),
                    display_order=int(row.get('display_order', 0) or 0),
                    is_active=True
                )
                db.add(subcategory)
                created += 1
                
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
    
    db.commit()
    return {"created": created, "updated": updated, "errors": errors}


@router.post("/brands")
async def import_brands(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Import brands from CSV.
    Columns: name, display_order
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV")
    
    content = await file.read()
    decoded = content.decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(decoded))
    
    created = 0
    updated = 0
    skipped = 0
    errors = []
    seen_slugs = set()  # Track slugs we've processed in this import
    
    for row_num, row in enumerate(reader, start=2):
        try:
            name = row.get('name', '').strip()
            if not name:
                continue
            
            slug = generate_slug(name)
            
            # Skip if we've already processed this slug in this import
            if slug in seen_slugs:
                skipped += 1
                continue
            seen_slugs.add(slug)
            
            # Check if exists in database
            existing = db.query(Brand).filter(Brand.slug == slug).first()
            
            if existing:
                existing.name = name
                existing.display_order = int(row.get('display_order', 0) or 0)
                updated += 1
            else:
                brand = Brand(
                    name=name,
                    slug=slug,
                    display_order=int(row.get('display_order', 0) or 0),
                    is_active=True
                )
                db.add(brand)
                db.flush()  # Flush to catch any DB errors immediately
                created += 1
                
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
    
    db.commit()
    return {"created": created, "updated": updated, "skipped": skipped, "errors": errors}


@router.post("/products")
async def import_products(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Import products from CSV.
    Columns: category_name, subcategory_name, brand_name, name, part_number, short_description, description, display_order

    Rows with a part_number update the existing product with that part number (upsert).
    Rows without a part_number match by slug + category + name, or create a new row.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV")
    
    content = await file.read()
    decoded = content.decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(decoded))
    
    created = 0
    updated = 0
    errors = []
    
    for row_num, row in enumerate(reader, start=2):
        try:
            name = row.get('name', '').strip()
            category_name = row.get('category_name', '').strip()
            
            if not name or not category_name:
                continue
            
            # Find category
            category = db.query(Category).filter(Category.name == category_name).first()
            if not category:
                errors.append(f"Row {row_num}: Category '{category_name}' not found")
                continue
            
            # Find subcategory (optional)
            subcategory_id = None
            subcategory_name = row.get('subcategory_name', '').strip()
            if subcategory_name:
                subcategory = db.query(Subcategory).filter(
                    Subcategory.name == subcategory_name,
                    Subcategory.category_id == category.id
                ).first()
                if subcategory:
                    subcategory_id = subcategory.id
                else:
                    errors.append(f"Row {row_num}: Subcategory '{subcategory_name}' not found, product added without subcategory")
            
            # Find brand (optional)
            brand_id = None
            brand_name = row.get('brand_name', '').strip()
            if brand_name:
                brand = db.query(Brand).filter(Brand.name == brand_name).first()
                if brand:
                    brand_id = brand.id
            
            outcome = ProductService.upsert_from_import(
                db,
                category_id=category.id,
                subcategory_id=subcategory_id,
                brand_id=brand_id,
                name=name,
                part_number_raw=row.get('part_number', ''),
                short_description=row.get('short_description', '').strip(),
                description=row.get('description', '').strip(),
                display_order=int(row.get('display_order', 0) or 0),
            )
            if outcome == "created":
                created += 1
            else:
                updated += 1
            db.flush()

        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")

    db.commit()
    if created or updated:
        invalidate_public()
    return {"created": created, "updated": updated, "errors": errors}
