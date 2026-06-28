"""Audit log read endpoints (Phase 4.13). Super-admin only."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models._common import AuditAction
from ..models.audit import AuditLog
from ..models.brand import Brand
from ..models.category import Category
from ..models.product import Product
from ..models.subcategory import Subcategory
from ..models.user import User
from ..services.permissions import require_view_audit


router = APIRouter(prefix="/audit", tags=["Audit"])


def _entity_meta(db: Session, entity_type: str, entity_id: Optional[int]) -> dict:
    """Resolve slug + existence for linking from audit rows."""
    if not entity_id:
        return {"entity_slug": None, "entity_exists": False, "entity_status": None}
    row = None
    if entity_type == "product":
        row = db.query(Product).filter(Product.id == entity_id).first()
    elif entity_type == "category":
        row = db.query(Category).filter(Category.id == entity_id).first()
    elif entity_type == "brand":
        row = db.query(Brand).filter(Brand.id == entity_id).first()
    elif entity_type == "subcategory":
        row = db.query(Subcategory).filter(Subcategory.id == entity_id).first()
    if not row:
        return {"entity_slug": None, "entity_exists": False, "entity_status": None}
    status = getattr(row, "status", None)
    status_val = status.value if hasattr(status, "value") else status
    return {
        "entity_slug": getattr(row, "slug", None),
        "entity_exists": True,
        "entity_status": status_val,
    }


@router.get("/")
def list_audit(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    entity_type: Optional[str] = Query(None),
    action: Optional[AuditAction] = Query(None),
    user_id: Optional[int] = Query(None),
    since: Optional[datetime] = Query(None),
    until: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_view_audit),
):
    query = db.query(AuditLog)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if action is not None:
        query = query.filter(AuditLog.action == action)
    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)
    if since is not None:
        query = query.filter(AuditLog.created_at >= since)
    if until is not None:
        query = query.filter(AuditLog.created_at <= until)

    total = query.count()
    rows = query.order_by(AuditLog.created_at.desc(), AuditLog.id.desc()).offset(skip).limit(limit).all()

    items = []
    for r in rows:
        meta = _entity_meta(db, r.entity_type, r.entity_id)
        items.append({
            "id": r.id,
            "user_id": r.user_id,
            "username": r.user.username if r.user else None,
            "full_name": r.user.full_name if r.user else None,
            "action": r.action.value if hasattr(r.action, "value") else r.action,
            "entity_type": r.entity_type,
            "entity_id": r.entity_id,
            "entity_label": r.entity_label,
            "entity_slug": meta["entity_slug"],
            "entity_exists": meta["entity_exists"],
            "entity_status": meta["entity_status"],
            "changes": r.changes_dict,
            "ip_address": r.ip_address,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    return {"items": items, "total": total, "skip": skip, "limit": limit}
