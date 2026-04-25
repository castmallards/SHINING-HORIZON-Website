import json
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
from ._common import AuditAction


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(
        Enum(AuditAction, name="auditaction", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer)
    entity_label = Column(String(255))
    # JSON: {field: [old_value, new_value]} for updates. Empty for creates/deletes.
    changes = Column(Text)
    ip_address = Column(String(45))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User")

    @property
    def changes_dict(self) -> dict:
        try:
            return json.loads(self.changes or "{}")
        except (TypeError, ValueError):
            return {}

    @changes_dict.setter
    def changes_dict(self, value: dict) -> None:
        self.changes = json.dumps(value or {})
