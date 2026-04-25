"""Shared enums and helpers for content models."""
import enum


class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class AuditAction(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    PUBLISH = "publish"
    UNPUBLISH = "unpublish"
