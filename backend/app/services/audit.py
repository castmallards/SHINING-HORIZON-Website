"""Audit log writer (Phase 4.12).

Service-layer hooks call ``AuditService.log(...)`` once their write has
committed. Designed to never raise — a logging failure must not roll back
the user's actual change. Writes use a fresh session so they don't depend
on the caller's transaction state.
"""
from __future__ import annotations

import logging
from typing import Any, Iterable, Mapping, Optional

from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models._common import AuditAction
from ..models.audit import AuditLog


_log = logging.getLogger(__name__)

# Fields we never want to persist in audit diffs (sensitive or noisy).
_REDACTED_FIELDS = {"password", "password_hash", "token", "access_token"}


class AuditService:
    @staticmethod
    def log(
        *,
        action: AuditAction,
        entity_type: str,
        entity_id: Optional[int],
        entity_label: Optional[str] = None,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        before: Optional[Mapping[str, Any]] = None,
        after: Optional[Mapping[str, Any]] = None,
    ) -> None:
        try:
            if action == AuditAction.UPDATE:
                changes = _diff(before, after)
            elif action == AuditAction.CREATE and after:
                changes = _initial_snapshot(after)
            else:
                changes = None
            db: Session = SessionLocal()
            try:
                entry = AuditLog(
                    user_id=user_id,
                    action=action,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    entity_label=(entity_label or "")[:255] or None,
                    ip_address=ip_address,
                )
                if changes:
                    entry.changes_dict = changes
                db.add(entry)
                db.commit()
            finally:
                db.close()
        except Exception as e:  # pragma: no cover — defensive only
            _log.warning("Audit log write failed: %s", e)


def snapshot(obj: Any, fields: Iterable[str]) -> dict:
    """Pull a flat dict of selected attributes off a model instance."""
    out: dict = {}
    if obj is None:
        return out
    for f in fields:
        if f in _REDACTED_FIELDS:
            continue
        if hasattr(obj, f):
            value = getattr(obj, f)
            # Coerce SQLAlchemy enums and datetimes to JSON-friendly values.
            if hasattr(value, "value"):
                value = value.value
            out[f] = value
    return out


def _initial_snapshot(after: Mapping[str, Any]) -> dict:
    """Record values set on create as ``{field: [null, new]}``."""
    diff: dict = {}
    for k, v in after.items():
        if k in _REDACTED_FIELDS:
            continue
        if v is None or v == "" or v == []:
            continue
        diff[k] = [None, _jsonable(v)]
    return diff


def _diff(before: Optional[Mapping[str, Any]], after: Optional[Mapping[str, Any]]) -> dict:
    """Compute a ``{field: [old, new]}`` diff. Skips fields that didn't change."""
    if not before or not after:
        return {}
    diff: dict = {}
    keys = set(before) | set(after)
    for k in keys:
        if k in _REDACTED_FIELDS:
            continue
        old = before.get(k)
        new = after.get(k)
        if old != new:
            diff[k] = [_jsonable(old), _jsonable(new)]
    return diff


def _jsonable(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool, list, dict)):
        return value
    return str(value)
