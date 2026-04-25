from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from ..models.category import CategoryType
from ..models._common import ContentStatus


class CategoryBase(BaseModel):
    name: str
    type: CategoryType = CategoryType.SIMPLE
    description: Optional[str] = None
    hero_title: Optional[str] = None
    hero_description: Optional[str] = None
    display_order: int = 0
    is_active: bool = True
    show_on_home: bool = True
    # v2
    status: ContentStatus = ContentStatus.DRAFT
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class CategoryCreate(CategoryBase):
    image: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[CategoryType] = None
    description: Optional[str] = None
    hero_title: Optional[str] = None
    hero_description: Optional[str] = None
    image: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None
    show_on_home: Optional[bool] = None
    # v2
    status: Optional[ContentStatus] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    image: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_user_id: Optional[int] = None
    updated_by_user_id: Optional[int] = None
    product_count: Optional[int] = 0
    subcategory_count: Optional[int] = 0
