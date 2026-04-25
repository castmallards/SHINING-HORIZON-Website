from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models._common import ContentStatus
from ..models.subcategory import Subcategory
from ..models.user import User
from ..schemas.subcategory import SubcategoryCreate, SubcategoryResponse, SubcategoryUpdate
from ..services.auth import get_current_user
from ..services.permissions import enforce_status_change, require_delete
from ..services.subcategory import SubcategoryService


router = APIRouter(prefix="/subcategories", tags=["Subcategories"])


def _client_ip(request: Request) -> Optional[str]:
    return request.client.host if request.client else None


@router.get("/", response_model=List[SubcategoryResponse])
def get_subcategories(
    category_id: Optional[int] = Query(None),
    include_inactive: bool = Query(True),
    status: Optional[ContentStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Subcategory)
    if category_id:
        query = query.filter(Subcategory.category_id == category_id)
    if not include_inactive:
        query = query.filter(Subcategory.is_active == True)  # noqa: E712
    if status is not None:
        query = query.filter(Subcategory.status == status)
    rows = query.order_by(Subcategory.display_order, Subcategory.name).all()
    return [SubcategoryService.get_with_counts(db, s) for s in rows]


@router.get("/{subcategory_id}", response_model=SubcategoryResponse)
def get_subcategory(
    subcategory_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subcategory = SubcategoryService.get_by_id(db, subcategory_id)
    if not subcategory:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    return SubcategoryService.get_with_counts(db, subcategory)


@router.post("/", response_model=SubcategoryResponse)
def create_subcategory(
    subcategory_data: SubcategoryCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enforce_status_change(current_user, getattr(subcategory_data, "status", None))
    sub = SubcategoryService.create(db, subcategory_data, actor_id=current_user.id, ip=_client_ip(request))
    return SubcategoryService.get_with_counts(db, sub)


@router.put("/{subcategory_id}", response_model=SubcategoryResponse)
def update_subcategory(
    subcategory_id: int,
    subcategory_data: SubcategoryUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enforce_status_change(current_user, getattr(subcategory_data, "status", None))
    sub = SubcategoryService.update(db, subcategory_id, subcategory_data, actor_id=current_user.id, ip=_client_ip(request))
    return SubcategoryService.get_with_counts(db, sub)


@router.delete("/{subcategory_id}")
def delete_subcategory(
    subcategory_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delete),
):
    SubcategoryService.delete(db, subcategory_id, actor_id=current_user.id, ip=_client_ip(request))
    return {"message": "Subcategory deleted successfully"}
