from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
from ._common import ContentStatus


class Subcategory(Base):
    __tablename__ = "subcategories"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), index=True, nullable=False)
    description = Column(Text)
    image = Column(String(255))
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

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
    category = relationship("Category", back_populates="subcategories")
    products = relationship("Product", back_populates="subcategory", cascade="all, delete-orphan")
