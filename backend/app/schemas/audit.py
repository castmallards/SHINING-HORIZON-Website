from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from ..models._common import AuditAction


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    action: AuditAction
    entity_type: str
    entity_id: Optional[int] = None
    entity_label: Optional[str] = None
    entity_slug: Optional[str] = None
    entity_exists: bool = False
    entity_status: Optional[str] = None
    changes: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: datetime
