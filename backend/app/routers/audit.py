"""Audit log read endpoints (Phase 4.13). Super-admin only."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models._common import AuditAction
from ..models.audit import AuditLog
from ..models.user import User
from ..services.permissions import require_view_audit


router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/")
def list_audit(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    entity_type: Optional[str] = Query(None),
    action: Optional[AuditAction] = Query(None),
    user_id: Optional[int] = Query(None),
    since: Optional[datetime] = Query(None),
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

    total = query.count()
    rows = query.order_by(AuditLog.created_at.desc(), AuditLog.id.desc()).offset(skip).limit(limit).all()

    items = []
    for r in rows:
        items.append({
            "id": r.id,
            "user_id": r.user_id,
            "username": r.user.username if r.user else None,
            "action": r.action.value if hasattr(r.action, "value") else r.action,
            "entity_type": r.entity_type,
            "entity_id": r.entity_id,
            "entity_label": r.entity_label,
            "changes": r.changes_dict,
            "ip_address": r.ip_address,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    return {"items": items, "total": total, "skip": skip, "limit": limit}
