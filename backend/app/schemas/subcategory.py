from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from ..models._common import ContentStatus


class SubcategoryBase(BaseModel):
    name: str
    category_id: int
    description: Optional[str] = None
    display_order: int = 0
    is_active: bool = True
    # v2
    status: ContentStatus = ContentStatus.DRAFT
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class SubcategoryCreate(SubcategoryBase):
    image: Optional[str] = None


class SubcategoryUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    image: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None
    # v2
    status: Optional[ContentStatus] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class SubcategoryResponse(SubcategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    image: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_user_id: Optional[int] = None
    updated_by_user_id: Optional[int] = None
    product_count: Optional[int] = 0
    category_name: Optional[str] = None
