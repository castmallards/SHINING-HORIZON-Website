"""extend brands with description, website_url, country

Brand detail pages (new in v2) need richer info than just a name + logo.

Revision ID: 005_extend_brands
Revises: 004_audit_fks
Create Date: 2026-04-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "005_extend_brands"
down_revision: Union[str, None] = "004_audit_fks"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("brands") as batch:
        batch.add_column(sa.Column("description", sa.Text(), nullable=True))
        batch.add_column(sa.Column("website_url", sa.String(length=255), nullable=True))
        batch.add_column(sa.Column("country", sa.String(length=100), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("brands") as batch:
        batch.drop_column("country")
        batch.drop_column("website_url")
        batch.drop_column("description")
