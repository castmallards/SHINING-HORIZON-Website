"""Product CRUD + bulk + pagination/search (Phases 4.14, 4.15, 4.16)."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models._common import AuditAction, ContentStatus
from ..models.brand import Brand
from ..models.product import Product
from ..models.user import User
from ..schemas.product import ProductCreate, ProductResponse, ProductUpdate
from ..services.audit import AuditService
from ..services.auth import get_current_user
from ..services.permissions import can_bulk_action, enforce_status_change, require_delete
from ..services.product import ProductService
from ..cache import invalidate_public


router = APIRouter(prefix="/products", tags=["Products"])


def _client_ip(request: Request) -> Optional[str]:
    return request.client.host if request.client else None


# ─── Static-path routes registered first so they aren't shadowed by /{id} ──

class BulkRequest(BaseModel):
    ids: List[int]
    action: str  # "publish" | "unpublish" | "delete"


@router.post("/bulk")
def bulk_action(
    payload: BulkRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not payload.ids:
        raise HTTPException(status_code=400, detail="No product IDs provided")
    if payload.action not in {"publish", "unpublish", "delete"}:
        raise HTTPException(status_code=400, detail="action must be publish, unpublish, or delete")
    if not can_bulk_action(current_user, payload.action):
        raise HTTPException(
            status_code=403,
            detail=f"Your role cannot perform bulk {payload.action}.",
        )

    rows = db.query(Product).filter(Product.id.in_(payload.ids)).all()
    if not rows:
        raise HTTPException(status_code=404, detail="No matching products")

    ip = _client_ip(request)
    affected = 0
    for p in rows:
        if payload.action == "delete":
            label, pid = p.name, p.id
            db.delete(p)
            AuditService.log(
                action=AuditAction.DELETE,
                entity_type="product",
                entity_id=pid,
                entity_label=label,
                user_id=current_user.id,
                ip_address=ip,
            )
            affected += 1
        else:
            new_status = ContentStatus.PUBLISHED if payload.action == "publish" else ContentStatus.DRAFT
            if p.status != new_status:
                p.status = new_status
                p.updated_by_user_id = current_user.id
                AuditService.log(
                    action=AuditAction.PUBLISH if payload.action == "publish" else AuditAction.UNPUBLISH,
                    entity_type="product",
                    entity_id=p.id,
                    entity_label=p.name,
                    user_id=current_user.id,
                    ip_address=ip,
                )
                affected += 1

    db.commit()
    invalidate_public()
    return {"action": payload.action, "affected": affected, "requested": len(payload.ids)}


@router.get("/validation")
def validate_catalog(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Surface gaps in published catalog data (Phase 4.16)."""
    pub = db.query(Product).filter(Product.status == ContentStatus.PUBLISHED)
    missing_image = pub.filter((Product.image == None) | (Product.image == "")).count()  # noqa: E711
    missing_meta = pub.filter(
        ((Product.meta_title == None) | (Product.meta_title == ""))  # noqa: E711
        | ((Product.meta_description == None) | (Product.meta_description == ""))  # noqa: E711
    ).count()
    missing_specs = pub.filter((Product.specifications == None) | (Product.specifications == "[]") | (Product.specifications == "")).count()  # noqa: E711
    missing_description = pub.filter((Product.description == None) | (Product.description == "")).count()  # noqa: E711
    missing_brand = pub.filter(Product.brand_id == None).count()  # noqa: E711

    samples = (
        pub.filter((Product.image == None) | (Product.image == ""))  # noqa: E711
        .order_by(Product.id)
        .limit(10)
        .all()
    )

    return {
        "published_total": pub.count(),
        "missing_image": missing_image,
        "missing_meta": missing_meta,
        "missing_specs": missing_specs,
        "missing_description": missing_description,
        "missing_brand": missing_brand,
        "samples_missing_image": [
            {"id": p.id, "name": p.name, "slug": p.slug, "part_number": p.part_number}
            for p in samples
        ],
    }


# ─── Paginated list ─────────────────────────────────────────────────────

@router.get("/")
def get_products(
    request: Request,
    category_id: Optional[int] = Query(None),
    subcategory_id: Optional[int] = Query(None),
    brand_id: Optional[int] = Query(None),
    status: Optional[ContentStatus] = Query(None, description="Filter by publish status"),
    search: Optional[str] = Query(None, description="Match name, part number, or slug (case-insensitive)"),
    include_inactive: bool = Query(True, description="Include is_active=false rows"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List products. Returns ``{items, total, skip, limit}``."""
    query = db.query(Product)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if subcategory_id:
        query = query.filter(Product.subcategory_id == subcategory_id)
    if brand_id:
        query = query.filter(Product.brand_id == brand_id)
    if status is not None:
        query = query.filter(Product.status == status)
    if not include_inactive:
        query = query.filter(Product.is_active == True)  # noqa: E712
    if search:
        like = f"%{search.strip()}%"
        query = query.outerjoin(Brand, Product.brand_id == Brand.id).filter(or_(
            Product.name.ilike(like),
            Product.part_number.ilike(like),
            Product.slug.ilike(like),
            Product.short_description.ilike(like),
            Product.description.ilike(like),
            Brand.name.ilike(like),
        ))

    total = query.count()
    rows = query.order_by(Product.display_order, Product.id).offset(skip).limit(limit).all()
    items = [ProductService.get_with_relations(db, p) for p in rows]
    return {"items": items, "total": total, "skip": skip, "limit": limit}


# ─── Per-id routes registered last ──────────────────────────────────────

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = ProductService.get_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductService.get_with_relations(db, product)


@router.post("/", response_model=ProductResponse)
def create_product(
    request: Request,
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enforce_status_change(current_user, getattr(product_data, "status", None))
    product = ProductService.create(db, product_data, actor_id=current_user.id, ip=_client_ip(request))
    return ProductService.get_with_relations(db, product)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enforce_status_change(current_user, getattr(product_data, "status", None))
    product = ProductService.update(db, product_id, product_data, actor_id=current_user.id, ip=_client_ip(request))
    return ProductService.get_with_relations(db, product)


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delete),
):
    ProductService.delete(db, product_id, actor_id=current_user.id, ip=_client_ip(request))
    return {"message": "Product deleted successfully"}
