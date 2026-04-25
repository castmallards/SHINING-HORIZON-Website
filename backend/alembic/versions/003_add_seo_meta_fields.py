"""add meta_title and meta_description for SEO

Adds Google/social meta fields to categories, subcategories, products.
Brands deliberately skipped — brand pages use the brand name directly.

Revision ID: 003_seo_meta
Revises: 002_status
Create Date: 2026-04-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "003_seo_meta"
down_revision: Union[str, None] = "002_status"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


SEO_TABLES = ("categories", "subcategories", "products")


def upgrade() -> None:
    for table in SEO_TABLES:
        with op.batch_alter_table(table) as batch:
            batch.add_column(sa.Column("meta_title", sa.String(length=160), nullable=True))
            batch.add_column(sa.Column("meta_description", sa.String(length=320), nullable=True))


def downgrade() -> None:
    for table in SEO_TABLES:
        with op.batch_alter_table(table) as batch:
            batch.drop_column("meta_description")
            batch.drop_column("meta_title")
