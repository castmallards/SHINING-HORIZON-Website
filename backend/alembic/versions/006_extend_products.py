"""extend products with specifications, gallery, datasheet_url

specifications: JSON array of {key, value} objects, e.g.
    [{"key": "Voltage", "value": "24 V DC"}, {"key": "IP Rating", "value": "IP67"}]
gallery: JSON array of image base-paths (same shape as `image` column)
datasheet_url: external link to manufacturer PDF (we store the URL, not the file)

Stored as TEXT and parsed in Python — works on SQLite and Postgres alike
without needing the JSONB type.

Revision ID: 006_extend_products
Revises: 005_extend_brands
Create Date: 2026-04-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "006_extend_products"
down_revision: Union[str, None] = "005_extend_brands"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("products") as batch:
        batch.add_column(sa.Column("specifications", sa.Text(), nullable=True))
        batch.add_column(sa.Column("gallery", sa.Text(), nullable=True))
        batch.add_column(sa.Column("datasheet_url", sa.String(length=500), nullable=True))

    # Initialise as empty JSON arrays so reads never see NULL
    op.execute("UPDATE products SET specifications = '[]' WHERE specifications IS NULL")
    op.execute("UPDATE products SET gallery = '[]' WHERE gallery IS NULL")


def downgrade() -> None:
    with op.batch_alter_table("products") as batch:
        batch.drop_column("datasheet_url")
        batch.drop_column("gallery")
        batch.drop_column("specifications")
