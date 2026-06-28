from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models._common import ContentStatus
from ..models.brand import Brand
from ..models.user import User
from ..schemas.brand import BrandCreate, BrandResponse, BrandUpdate
from ..services.auth import get_current_user
from ..services.brand import BrandService
from ..services.permissions import enforce_status_change, require_delete


router = APIRouter(prefix="/brands", tags=["Brands"])


def _client_ip(request: Request) -> Optional[str]:
    return request.client.host if request.client else None


@router.get("/")
def get_brands(
    include_inactive: bool = Query(True),
    status: Optional[ContentStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Brand)
    if not include_inactive:
        query = query.filter(Brand.is_active == True)  # noqa: E712
    if status is not None:
        query = query.filter(Brand.status == status)
    total = query.count()
    rows = (
        query.order_by(Brand.display_order, Brand.name)
        .offset(skip)
        .limit(limit)
        .all()
    )
    items = [BrandService.get_with_counts(db, b) for b in rows]
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/{brand_id}", response_model=BrandResponse)
def get_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    brand = BrandService.get_by_id(db, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return BrandService.get_with_counts(db, brand)


@router.post("/", response_model=BrandResponse)
def create_brand(
    brand_data: BrandCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enforce_status_change(current_user, getattr(brand_data, "status", None))
    brand = BrandService.create(db, brand_data, actor_id=current_user.id, ip=_client_ip(request))
    return BrandService.get_with_counts(db, brand)


@router.put("/{brand_id}", response_model=BrandResponse)
def update_brand(
    brand_id: int,
    brand_data: BrandUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enforce_status_change(current_user, getattr(brand_data, "status", None))
    brand = BrandService.update(db, brand_id, brand_data, actor_id=current_user.id, ip=_client_ip(request))
    return BrandService.get_with_counts(db, brand)


@router.delete("/{brand_id}")
def delete_brand(
    brand_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delete),
):
    BrandService.delete(db, brand_id, actor_id=current_user.id, ip=_client_ip(request))
    return {"message": "Brand deleted successfully"}
