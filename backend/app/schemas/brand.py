from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator
from typing import Optional
from datetime import datetime
from ..models._common import ContentStatus


class BrandBase(BaseModel):
    name: str
    display_order: int = 0
    is_active: bool = True
    # v2
    description: Optional[str] = None
    website_url: Optional[str] = None
    country: Optional[str] = None
    status: ContentStatus = ContentStatus.DRAFT


class BrandCreate(BrandBase):
    logo: Optional[str] = None


class BrandUpdate(BaseModel):
    name: Optional[str] = None
    logo: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None
    # v2
    description: Optional[str] = None
    website_url: Optional[str] = None
    country: Optional[str] = None
    status: Optional[ContentStatus] = None


class BrandResponse(BrandBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    logo: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_user_id: Optional[int] = None
    updated_by_user_id: Optional[int] = None
    product_count: Optional[int] = 0
