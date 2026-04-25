"""Role-based permission gates.

Centralises the rules that decide what each role can do. Routers and the
service layer call these helpers (or use the FastAPI ``Depends`` wrappers
below) instead of branching on ``user.role`` themselves.

Role matrix:

  | role         | view | create | edit | publish | delete | users | audit |
  |--------------|------|--------|------|---------|--------|-------|-------|
  | super_admin  |  ✓   |   ✓    |  ✓   |    ✓    |   ✓    |   ✓   |   ✓   |
  | admin        |  ✓   |   ✓    |  ✓   |    ✓    |   ✓    |   ✗   |   ✓   |
  | manager      |  ✓   |   ✓    |  ✓   |    ✓    |   ✗    |   ✗   |   ✗   |
  | data_entry   |  ✓   |   ✓    |  ✓   |    ✗    |   ✗    |   ✗   |   ✗   |
"""
from __future__ import annotations

from fastapi import Depends, HTTPException, status

from ..models.user import User, UserRole
from .auth import get_current_user


_FULL_ACCESS = {UserRole.SUPER_ADMIN, UserRole.ADMIN}
_CAN_PUBLISH = {UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER}
_CAN_DELETE = _FULL_ACCESS
_CAN_MANAGE_USERS = {UserRole.SUPER_ADMIN}
_CAN_VIEW_AUDIT = {UserRole.SUPER_ADMIN, UserRole.ADMIN}


# ── boolean helpers (use from service / template layer) ──────────────────

def can_publish(user: User) -> bool:
    return user.role in _CAN_PUBLISH


def can_delete(user: User) -> bool:
    return user.role in _CAN_DELETE


def can_manage_users(user: User) -> bool:
    return user.role in _CAN_MANAGE_USERS


def can_view_audit(user: User) -> bool:
    return user.role in _CAN_VIEW_AUDIT


def can_bulk_action(user: User, action: str) -> bool:
    if action == "delete":
        return can_delete(user)
    if action in {"publish", "unpublish"}:
        return can_publish(user)
    return False


# ── FastAPI dependency wrappers (use in router signatures) ───────────────

def require_publish(current_user: User = Depends(get_current_user)) -> User:
    if not can_publish(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your role cannot publish or unpublish content.",
        )
    return current_user


def require_delete(current_user: User = Depends(get_current_user)) -> User:
    if not can_delete(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your role cannot delete content.",
        )
    return current_user


def require_manage_users(current_user: User = Depends(get_current_user)) -> User:
    if not can_manage_users(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can manage users.",
        )
    return current_user


def require_view_audit(current_user: User = Depends(get_current_user)) -> User:
    if not can_view_audit(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Audit log is restricted to admins.",
        )
    return current_user


def enforce_status_change(user: User, requested_status, current_status=None) -> None:
    """Reject a write that promotes content past ``draft`` for non-publishers.

    ``requested_status`` may be a ``ContentStatus`` enum or its string value.
    Pass ``current_status=None`` for create flows.
    """
    if can_publish(user):
        return
    requested = getattr(requested_status, "value", requested_status)
    if requested and requested != "draft":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your role can only save content as draft.",
        )
