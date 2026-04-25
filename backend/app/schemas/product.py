from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from ..models._common import ContentStatus


class SpecItem(BaseModel):
    """A single key/value row in the product specifications table."""
    key: str
    value: str


class ProductBase(BaseModel):
    name: str
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    brand_id: Optional[int] = None
    part_number: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    display_order: int = 0
    is_active: bool = True
    is_featured: bool = False
    # v2
    status: ContentStatus = ContentStatus.DRAFT
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    specifications: List[SpecItem] = Field(default_factory=list)
    gallery: List[str] = Field(default_factory=list)
    datasheet_url: Optional[str] = None


class ProductCreate(ProductBase):
    image: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    brand_id: Optional[int] = None
    part_number: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    image: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    # v2
    status: Optional[ContentStatus] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    specifications: Optional[List[SpecItem]] = None
    gallery: Optional[List[str]] = None
    datasheet_url: Optional[str] = None


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    image: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_user_id: Optional[int] = None
    updated_by_user_id: Optional[int] = None
    category_name: Optional[str] = None
    subcategory_name: Optional[str] = None
    brand_name: Optional[str] = None
    brand_logo: Optional[str] = None
