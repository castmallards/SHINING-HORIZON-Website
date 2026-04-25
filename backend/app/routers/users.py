from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.user import User, UserRole
from ..schemas.user import UserCreate, UserResponse, UserUpdate
from ..services.permissions import require_manage_users
from ..services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def _last_super_admin_guard(db: Session, target: User, *, demoting_role=None, deactivating=False, deleting=False) -> None:
    """Don't let the operator strand the system without a super admin."""
    if target.role != UserRole.SUPER_ADMIN:
        return
    others = (
        db.query(User)
        .filter(User.role == UserRole.SUPER_ADMIN, User.is_active == True, User.id != target.id)  # noqa: E712
        .count()
    )
    if others >= 1:
        return
    if deleting or deactivating or (demoting_role is not None and demoting_role != UserRole.SUPER_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove the last active super admin.",
        )


@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manage_users),
):
    return UserService.get_all(db, skip, limit)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manage_users),
):
    user = UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manage_users),
):
    return UserService.create(db, user_data)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manage_users),
):
    target = UserService.get_by_id(db, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    _last_super_admin_guard(
        db, target,
        demoting_role=user_data.role,
        deactivating=(user_data.is_active is False),
    )
    return UserService.update(db, user_id, user_data)


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manage_users),
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself",
        )
    target = UserService.get_by_id(db, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    _last_super_admin_guard(db, target, deleting=True)
    UserService.delete(db, user_id)
    return {"message": "User deleted successfully"}
