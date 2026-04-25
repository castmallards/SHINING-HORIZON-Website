from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
import enum
from ..database import Base

class UserRole(str, enum.Enum):
    """Admin role hierarchy. Permission gates live in services.permissions.

    * SUPER_ADMIN — everything, including managing other admin users + audit log.
    * ADMIN       — full content CRUD + publish + delete + audit log; cannot manage users.
    * MANAGER     — create / edit / publish / unpublish; cannot delete or manage users.
    * DATA_ENTRY  — create + edit draft content; cannot publish or delete.
    """
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    DATA_ENTRY = "data_entry"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(Enum(UserRole), default=UserRole.ADMIN)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
