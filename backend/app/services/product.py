from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status
import re

from ..models.product import Product
from ..models._common import AuditAction
from ..models.category import Category
from ..models.subcategory import Subcategory
from ..models.brand import Brand
from ..schemas.product import ProductCreate, ProductUpdate
from ..cache import invalidate_public
from .audit import AuditService, snapshot

_AUDIT_FIELDS = ("name", "slug", "part_number", "category_id", "subcategory_id", "brand_id", "status", "is_active", "is_featured", "image", "datasheet_url", "display_order")

class ProductService:
    @staticmethod
    def normalize_part_number(part_number: Optional[str]) -> Optional[str]:
        """Strip whitespace; empty strings become None (no part number)."""
        if part_number is None:
            return None
        stripped = part_number.strip()
        return stripped if stripped else None

    @staticmethod
    def get_by_part_number(
        db: Session,
        part_number: str,
        *,
        exclude_id: Optional[int] = None,
    ) -> Optional[Product]:
        normalized = ProductService.normalize_part_number(part_number)
        if not normalized:
            return None
        query = db.query(Product).filter(Product.part_number == normalized)
        if exclude_id is not None:
            query = query.filter(Product.id != exclude_id)
        return query.first()

    @staticmethod
    def ensure_part_number_available(
        db: Session,
        part_number: Optional[str],
        *,
        exclude_id: Optional[int] = None,
    ) -> Optional[str]:
        """Return normalized part number, or raise 409 if another product already uses it."""
        normalized = ProductService.normalize_part_number(part_number)
        if not normalized:
            return None
        existing = ProductService.get_by_part_number(
            db, normalized, exclude_id=exclude_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A product with part number '{normalized}' already exists.",
            )
        return normalized

    @staticmethod
    def generate_slug(name: str, part_number: Optional[str] = None) -> str:
        base = part_number if part_number else name
        slug = base.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug
    
    @staticmethod
    def get_all(
        db: Session,
        category_id: Optional[int] = None,
        subcategory_id: Optional[int] = None,
        brand_id: Optional[int] = None,
        include_inactive: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        query = db.query(Product)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        if subcategory_id:
            query = query.filter(Product.subcategory_id == subcategory_id)
        if brand_id:
            query = query.filter(Product.brand_id == brand_id)
        if not include_inactive:
            query = query.filter(Product.is_active == True)
        
        return query.order_by(Product.display_order).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, product_id: int) -> Optional[Product]:
        return db.query(Product).filter(Product.id == product_id).first()
    
    @staticmethod
    def get_by_slug(db: Session, slug: str) -> Optional[Product]:
        return db.query(Product).filter(Product.slug == slug).first()
    
    @staticmethod
    def create(
        db: Session,
        product_data: ProductCreate,
        actor_id: Optional[int] = None,
        ip: Optional[str] = None,
    ) -> Product:
        if product_data.category_id:
            category = db.query(Category).filter(Category.id == product_data.category_id).first()
            if not category:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        if product_data.subcategory_id:
            subcategory = db.query(Subcategory).filter(Subcategory.id == product_data.subcategory_id).first()
            if not subcategory:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subcategory not found")

        if product_data.brand_id:
            brand = db.query(Brand).filter(Brand.id == product_data.brand_id).first()
            if not brand:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")

        part_number = ProductService.ensure_part_number_available(
            db, product_data.part_number
        )

        slug = ProductService.generate_slug(product_data.name, part_number)
        existing = ProductService.get_by_slug(db, slug)
        if existing:
            count = 1
            while ProductService.get_by_slug(db, f"{slug}-{count}"):
                count += 1
            slug = f"{slug}-{count}"

        product = Product(
            name=product_data.name,
            slug=slug,
            category_id=product_data.category_id,
            subcategory_id=product_data.subcategory_id,
            brand_id=product_data.brand_id,
            part_number=part_number,
            description=product_data.description,
            short_description=product_data.short_description,
            image=product_data.image,
            display_order=product_data.display_order,
            is_active=product_data.is_active,
            is_featured=product_data.is_featured,
            status=product_data.status,
            meta_title=product_data.meta_title,
            meta_description=product_data.meta_description,
            datasheet_url=product_data.datasheet_url,
            created_by_user_id=actor_id,
            updated_by_user_id=actor_id,
        )
        if product_data.specifications:
            product.specifications_list = [
                s.model_dump() if hasattr(s, "model_dump") else dict(s) for s in product_data.specifications
            ]
        if product_data.gallery:
            product.gallery_list = list(product_data.gallery)

        db.add(product)
        db.commit()
        db.refresh(product)
        invalidate_public()
        AuditService.log(
            action=AuditAction.CREATE,
            entity_type="product",
            entity_id=product.id,
            entity_label=product.name,
            user_id=actor_id,
            ip_address=ip,
        )
        return product

    @staticmethod
    def update(
        db: Session,
        product_id: int,
        product_data: ProductUpdate,
        actor_id: Optional[int] = None,
        ip: Optional[str] = None,
    ) -> Product:
        product = ProductService.get_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        before = snapshot(product, _AUDIT_FIELDS)
        prev_status = product.status
        update_data = product_data.model_dump(exclude_unset=True)
        spec_value = update_data.pop("specifications", None)
        gallery_value = update_data.pop("gallery", None)

        if "part_number" in update_data:
            update_data["part_number"] = ProductService.ensure_part_number_available(
                db,
                update_data["part_number"],
                exclude_id=product_id,
            )

        if "name" in update_data or "part_number" in update_data:
            name = update_data.get("name", product.name)
            part_number = update_data.get("part_number", product.part_number)
            new_slug = ProductService.generate_slug(name, part_number)
            existing = ProductService.get_by_slug(db, new_slug)
            if existing and existing.id != product_id:
                count = 1
                while ProductService.get_by_slug(db, f"{new_slug}-{count}"):
                    count += 1
                new_slug = f"{new_slug}-{count}"
            update_data["slug"] = new_slug

        for field, value in update_data.items():
            setattr(product, field, value)
        if spec_value is not None:
            product.specifications_list = [
                s.model_dump() if hasattr(s, "model_dump") else dict(s) for s in spec_value
            ]
        if gallery_value is not None:
            product.gallery_list = list(gallery_value)
        product.updated_by_user_id = actor_id

        db.commit()
        db.refresh(product)
        invalidate_public()

        after = snapshot(product, _AUDIT_FIELDS)
        action = AuditAction.UPDATE
        if "status" in update_data and product.status != prev_status:
            cur = product.status.value if hasattr(product.status, "value") else product.status
            action = AuditAction.PUBLISH if cur == "published" else AuditAction.UNPUBLISH
        AuditService.log(
            action=action,
            entity_type="product",
            entity_id=product.id,
            entity_label=product.name,
            user_id=actor_id,
            ip_address=ip,
            before=before,
            after=after,
        )
        return product

    @staticmethod
    def delete(
        db: Session,
        product_id: int,
        actor_id: Optional[int] = None,
        ip: Optional[str] = None,
    ) -> bool:
        product = ProductService.get_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        label = product.name
        pid = product.id
        db.delete(product)
        db.commit()
        invalidate_public()
        AuditService.log(
            action=AuditAction.DELETE,
            entity_type="product",
            entity_id=pid,
            entity_label=label,
            user_id=actor_id,
            ip_address=ip,
        )
        return True
    
    @staticmethod
    def get_with_relations(db: Session, product: Product) -> dict:
        category = db.query(Category).filter(Category.id == product.category_id).first()
        subcategory = db.query(Subcategory).filter(Subcategory.id == product.subcategory_id).first() if product.subcategory_id else None
        brand = db.query(Brand).filter(Brand.id == product.brand_id).first() if product.brand_id else None

        # `product.__dict__` exposes the raw Text columns (`specifications`, `gallery`)
        # which are JSON-encoded strings. ProductResponse declares them as List[...],
        # so we replace them with the parsed list properties before serialising.
        data = {k: v for k, v in product.__dict__.items() if not k.startswith("_")}
        data["specifications"] = product.specifications_list
        data["gallery"] = product.gallery_list
        data["category_name"] = category.name if category else None
        data["subcategory_name"] = subcategory.name if subcategory else None
        data["brand_name"] = brand.name if brand else None
        data["brand_logo"] = brand.logo if brand else None
        return data
