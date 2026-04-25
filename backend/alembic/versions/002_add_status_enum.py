"""add status enum to categories, subcategories, brands, products

Adds a `status` column (draft|published) alongside the legacy `is_active`
boolean. New code uses `status`; `is_active` is kept for backward compatibility
during the migration. Default is 'draft' so admin must explicitly publish.

Backfill (existing rows): is_active=True → 'published', else 'draft'.

Revision ID: 002_status
Revises: 001_baseline
Create Date: 2026-04-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "002_status"
down_revision: Union[str, None] = "001_baseline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


CONTENT_TABLES = ("categories", "subcategories", "brands", "products")


def upgrade() -> None:
    status_enum = sa.Enum("draft", "published", name="contentstatus")
    bind = op.get_bind()
    # PostgreSQL needs the type created once; SQLite is permissive
    if bind.dialect.name != "sqlite":
        status_enum.create(bind, checkfirst=True)

    for table in CONTENT_TABLES:
        with op.batch_alter_table(table) as batch:
            batch.add_column(
                sa.Column(
                    "status",
                    status_enum,
                    nullable=False,
                    server_default="draft",
                )
            )

    # Backfill from legacy is_active flag (1.14)
    for table in CONTENT_TABLES:
        op.execute(
            f"UPDATE {table} SET status = CASE WHEN is_active = 1 THEN 'published' ELSE 'draft' END"
        )

    # Indexes for filtering by status (admin list pages, public published-only queries)
    for table in CONTENT_TABLES:
        op.create_index(f"ix_{table}_status", table, ["status"])


def downgrade() -> None:
    for table in CONTENT_TABLES:
        op.drop_index(f"ix_{table}_status", table_name=table)
        with op.batch_alter_table(table) as batch:
            batch.drop_column("status")

    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        sa.Enum(name="contentstatus").drop(bind, checkfirst=True)
