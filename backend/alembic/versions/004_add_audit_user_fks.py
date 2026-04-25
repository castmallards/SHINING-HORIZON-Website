"""add created_by_user_id and updated_by_user_id to content tables

Tracks which admin created or last edited each row. Used by the audit log
viewer and "edited 3 days ago by Sarah" UI hints in the admin dashboard.

Revision ID: 004_audit_fks
Revises: 003_seo_meta
Create Date: 2026-04-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "004_audit_fks"
down_revision: Union[str, None] = "003_seo_meta"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


CONTENT_TABLES = ("categories", "subcategories", "brands", "products")


def upgrade() -> None:
    for table in CONTENT_TABLES:
        with op.batch_alter_table(table) as batch:
            batch.add_column(sa.Column("created_by_user_id", sa.Integer(), nullable=True))
            batch.add_column(sa.Column("updated_by_user_id", sa.Integer(), nullable=True))
            batch.create_foreign_key(
                f"fk_{table}_created_by",
                "users",
                ["created_by_user_id"],
                ["id"],
                ondelete="SET NULL",
            )
            batch.create_foreign_key(
                f"fk_{table}_updated_by",
                "users",
                ["updated_by_user_id"],
                ["id"],
                ondelete="SET NULL",
            )


def downgrade() -> None:
    for table in CONTENT_TABLES:
        with op.batch_alter_table(table) as batch:
            batch.drop_constraint(f"fk_{table}_updated_by", type_="foreignkey")
            batch.drop_constraint(f"fk_{table}_created_by", type_="foreignkey")
            batch.drop_column("updated_by_user_id")
            batch.drop_column("created_by_user_id")
