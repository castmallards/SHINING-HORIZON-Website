from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models._common import ContentStatus
from ..models.category import Category
from ..models.user import User
from ..schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from ..services.auth import get_current_user
from ..services.category import CategoryService
from ..services.permissions import enforce_status_change, require_delete


router = APIRouter(prefix="/categories", tags=["Categories"])


def _client_ip(request: Request) -> Optional[str]:
    return request.client.host if request.client else None


@router.get("/", response_model=List[CategoryResponse])
def get_categories(
    include_inactive: bool = Query(True),
    status: Optional[ContentStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Category)
    if not include_inactive:
        query = query.filter(Category.is_active == True)  # noqa: E712
    if status is not None:
        query = query.filter(Category.status == status)
    rows = query.order_by(Category.display_order, Category.name).all()
    return [CategoryService.get_with_counts(db, c) for c in rows]


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = CategoryService.get_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryService.get_with_counts(db, category)


@router.post("/", response_model=CategoryResponse)
def create_category(
    category_data: CategoryCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enforce_status_change(current_user, getattr(category_data, "status", None))
    category = CategoryService.create(db, category_data, actor_id=current_user.id, ip=_client_ip(request))
    return CategoryService.get_with_counts(db, category)


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enforce_status_change(current_user, getattr(category_data, "status", None))
    category = CategoryService.update(db, category_id, category_data, actor_id=current_user.id, ip=_client_ip(request))
    return CategoryService.get_with_counts(db, category)


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delete),
):
    CategoryService.delete(db, category_id, actor_id=current_user.id, ip=_client_ip(request))
    return {"message": "Category deleted successfully"}
