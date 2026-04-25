from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ..database import Base
from ._common import ContentStatus


class CategoryType(str, enum.Enum):
    DETAILED = "detailed"  # Has subcategories, products with part numbers
    SIMPLE = "simple"      # Direct product listing like tools page


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    type = Column(Enum(CategoryType), default=CategoryType.SIMPLE)
    description = Column(Text)
    image = Column(String(255))
    hero_title = Column(String(200))
    hero_description = Column(Text)
    display_order = Column(Integer, default=0)

    # Legacy flag — kept for backward compatibility. New code reads `status`.
    is_active = Column(Boolean, default=True)
    show_on_home = Column(Boolean, default=True)

    # v2 additions
    status = Column(
        Enum(ContentStatus, name="contentstatus", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ContentStatus.DRAFT,
        index=True,
    )
    meta_title = Column(String(160))
    meta_description = Column(String(320))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    subcategories = relationship("Subcategory", back_populates="category", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")
