import json
from typing import Optional

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
from ._common import ContentStatus


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    subcategory_id = Column(Integer, ForeignKey("subcategories.id", ondelete="SET NULL"), nullable=True)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="SET NULL"), nullable=True)

    name = Column(String(200), nullable=False)
    slug = Column(String(200), index=True, nullable=False)
    part_number = Column(String(100), unique=True, nullable=True)
    description = Column(Text)
    short_description = Column(String(500))
    image = Column(String(255))

    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)

    # v2 additions
    status = Column(
        Enum(ContentStatus, name="contentstatus", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ContentStatus.DRAFT,
        index=True,
    )
    meta_title = Column(String(160))
    meta_description = Column(String(320))
    # JSON-encoded text. Use the helper properties below to read/write.
    specifications = Column(Text, default="[]")
    gallery = Column(Text, default="[]")
    datasheet_url = Column(String(500))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    category = relationship("Category", back_populates="products")
    subcategory = relationship("Subcategory", back_populates="products")
    brand = relationship("Brand", back_populates="products")

    # ── JSON helpers ──
    @property
    def specifications_list(self) -> list[dict]:
        try:
            return json.loads(self.specifications or "[]")
        except (TypeError, ValueError):
            return []

    @specifications_list.setter
    def specifications_list(self, value: list[dict]) -> None:
        self.specifications = json.dumps(value or [])

    @property
    def gallery_list(self) -> list[str]:
        try:
            return json.loads(self.gallery or "[]")
        except (TypeError, ValueError):
            return []

    @gallery_list.setter
    def gallery_list(self, value: list[str]) -> None:
        self.gallery = json.dumps(value or [])

    @property
    def cover_image(self) -> Optional[str]:
        """Primary listing image, or first gallery image when primary is unset."""
        if self.image:
            return self.image
        gallery = self.gallery_list
        return gallery[0] if gallery else None
