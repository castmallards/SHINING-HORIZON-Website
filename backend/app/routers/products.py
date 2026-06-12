"""Product CRUD + bulk + pagination/search (Phases 4.14, 4.15, 4.16)."""
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy import and_, or_
from sqlalchemy.orm import Query as SqlQuery, Session

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

CatalogGap = Literal[
    "missing_image",
    "missing_meta",
    "missing_specs",
    "missing_description",
    "missing_brand",
]

_VALID_GAPS = {
    "missing_image",
    "missing_meta",
    "missing_specs",
    "missing_description",
    "missing_brand",
}

_PRODUCT_LIST_ORDER = (Product.display_order, Product.id)


def _client_ip(request: Request) -> Optional[str]:
    return request.client.host if request.client else None


def _apply_gap_filter(query: SqlQuery, gap: str) -> SqlQuery:
    if gap not in _VALID_GAPS:
        raise HTTPException(status_code=400, detail=f"Invalid gap. Must be one of: {sorted(_VALID_GAPS)}")
    if gap == "missing_image":
        return query.filter(
            or_(Product.image == None, Product.image == ""),  # noqa: E711
            or_(Product.gallery == None, Product.gallery == "", Product.gallery == "[]"),  # noqa: E711
        )
    if gap == "missing_meta":
        return query.filter(
            or_(
                Product.meta_title == None,  # noqa: E711
                Product.meta_title == "",
                Product.meta_description == None,  # noqa: E711
                Product.meta_description == "",
            )
        )
    if gap == "missing_specs":
        return query.filter(
            or_(Product.specifications == None, Product.specifications == "[]", Product.specifications == "")  # noqa: E711
        )
    if gap == "missing_description":
        return query.filter(or_(Product.description == None, Product.description == ""))  # noqa: E711
    if gap == "missing_brand":
        return query.filter(Product.brand_id == None)  # noqa: E711
    return query


def _build_products_query(
    db: Session,
    *,
    category_id: Optional[int] = None,
    subcategory_id: Optional[int] = None,
    brand_id: Optional[int] = None,
    status: Optional[ContentStatus] = None,
    search: Optional[str] = None,
    include_inactive: bool = True,
    gap: Optional[str] = None,
) -> SqlQuery:
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
        query = query.outerjoin(Brand, Product.brand_id == Brand.id).filter(
            or_(
                Product.name.ilike(like),
                Product.part_number.ilike(like),
                Product.slug.ilike(like),
                Product.short_description.ilike(like),
                Product.description.ilike(like),
                Brand.name.ilike(like),
            )
        )
    if gap:
        query = _apply_gap_filter(query, gap)
    return query


def _products_before_filter(product: Product) -> SqlQuery:
    return or_(
        Product.display_order < product.display_order,
        and_(Product.display_order == product.display_order, Product.id < product.id),
    )


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


@router.get("/check-part-number")
def check_part_number(
    part_number: str = Query(..., min_length=1, description="Part number to validate"),
    exclude_id: Optional[int] = Query(
        None,
        description="Product id to exclude (when editing an existing product)",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return whether a part number is available (for admin blur validation)."""
    normalized = ProductService.normalize_part_number(part_number)
    if not normalized:
        return {
            "available": True,
            "part_number": None,
            "existing": None,
        }

    existing = ProductService.get_by_part_number(
        db, normalized, exclude_id=exclude_id
    )
    if not existing:
        return {
            "available": True,
            "part_number": normalized,
            "existing": None,
        }

    return {
        "available": False,
        "part_number": normalized,
        "existing": {
            "id": existing.id,
            "name": existing.name,
            "slug": existing.slug,
        },
    }


@router.get("/validation")
def validate_catalog(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Surface gaps in published catalog data (Phase 4.16)."""
    pub = db.query(Product).filter(Product.status == ContentStatus.PUBLISHED)
    missing_image = _apply_gap_filter(pub, "missing_image").count()
    missing_meta = _apply_gap_filter(pub, "missing_meta").count()
    missing_specs = _apply_gap_filter(pub, "missing_specs").count()
    missing_description = _apply_gap_filter(pub, "missing_description").count()
    missing_brand = _apply_gap_filter(pub, "missing_brand").count()

    samples = (
        _apply_gap_filter(pub, "missing_image")
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
    gap: Optional[CatalogGap] = Query(
        None,
        description="Catalog quality filter (missing_image, missing_meta, etc.)",
    ),
    include_inactive: bool = Query(True, description="Include is_active=false rows"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List products. Returns ``{items, total, skip, limit}``."""
    query = _build_products_query(
        db,
        category_id=category_id,
        subcategory_id=subcategory_id,
        brand_id=brand_id,
        status=status,
        search=search,
        include_inactive=include_inactive,
        gap=gap,
    )

    total = query.count()
    rows = query.order_by(*_PRODUCT_LIST_ORDER).offset(skip).limit(limit).all()
    items = [ProductService.get_with_relations(db, p) for p in rows]
    return {"items": items, "total": total, "skip": skip, "limit": limit}


# ─── Per-id routes registered last ──────────────────────────────────────

@router.get("/{product_id}/list-position")
def get_product_list_position(
    product_id: int,
    category_id: Optional[int] = Query(None),
    subcategory_id: Optional[int] = Query(None),
    brand_id: Optional[int] = Query(None),
    status: Optional[ContentStatus] = Query(None),
    search: Optional[str] = Query(None),
    gap: Optional[CatalogGap] = Query(None),
    include_inactive: bool = Query(True),
    limit: int = Query(25, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return pagination skip/page for a product using the same filters and sort as the list."""
    product = ProductService.get_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    query = _build_products_query(
        db,
        category_id=category_id,
        subcategory_id=subcategory_id,
        brand_id=brand_id,
        status=status,
        search=search,
        include_inactive=include_inactive,
        gap=gap,
    )
    if not query.filter(Product.id == product_id).count():
        raise HTTPException(status_code=404, detail="Product not found for current filters")

    total = query.count()
    position = query.filter(_products_before_filter(product)).count()
    if position >= total and total > 0:
        position = max(0, total - 1)

    skip = (position // limit) * limit
    page = (position // limit) + 1 if total else 1
    total_pages = max(1, (total + limit - 1) // limit) if total else 1

    return {
        "product_id": product_id,
        "skip": skip,
        "limit": limit,
        "page": page,
        "total": total,
        "total_pages": total_pages,
        "index": position,
    }


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
