from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
from ._common import ContentStatus


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    logo = Column(String(255))
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)

    # v2 additions
    description = Column(Text)
    website_url = Column(String(255))
    country = Column(String(100))
    status = Column(
        Enum(ContentStatus, name="contentstatus", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ContentStatus.DRAFT,
        index=True,
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    products = relationship("Product", back_populates="brand")
