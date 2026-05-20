"""Normalize part numbers, remove duplicates, add unique constraint.

Revision ID: 008_unique_part_number
Revises: 007_audit_log
Create Date: 2026-05-19

Before applying the unique index, duplicate rows sharing the same
normalized part_number are collapsed: we keep the row with the lowest id,
preferring a slug that does not end in ``-<digits>`` (legacy slug suffix).
"""
from __future__ import annotations

import re
from collections import defaultdict
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "008_unique_part_number"
down_revision: Union[str, None] = "007_audit_log"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SLUG_NUMERIC_SUFFIX = re.compile(r"-\d+$")


def _normalize_part_number(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped if stripped else None


def _keeper_sort_key(row: sa.Row) -> tuple:
    slug = row.slug or ""
    has_numeric_suffix = bool(_SLUG_NUMERIC_SUFFIX.search(slug))
    return (has_numeric_suffix, row.id)


def upgrade() -> None:
    conn = op.get_bind()
    products = sa.table(
        "products",
        sa.column("id", sa.Integer),
        sa.column("slug", sa.String),
        sa.column("part_number", sa.String),
    )

    rows = conn.execute(
        sa.select(products.c.id, products.c.slug, products.c.part_number)
    ).fetchall()

    # Normalize stored part numbers (trim; blank → NULL).
    for row in rows:
        normalized = _normalize_part_number(row.part_number)
        if normalized != row.part_number:
            conn.execute(
                sa.update(products)
                .where(products.c.id == row.id)
                .values(part_number=normalized)
            )

    # Reload after normalization.
    rows = conn.execute(
        sa.select(products.c.id, products.c.slug, products.c.part_number)
    ).fetchall()

    groups: dict[str, list] = defaultdict(list)
    for row in rows:
        pn = _normalize_part_number(row.part_number)
        if pn:
            groups[pn].append(row)

    ids_to_delete: list[int] = []
    for pn, group in groups.items():
        if len(group) < 2:
            continue
        group.sort(key=_keeper_sort_key)
        for dup in group[1:]:
            ids_to_delete.append(dup.id)

    if ids_to_delete:
        conn.execute(sa.delete(products).where(products.c.id.in_(ids_to_delete)))

    # SQLite / PostgreSQL: multiple NULL part_numbers remain allowed.
    op.create_index(
        "uq_products_part_number",
        "products",
        ["part_number"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_products_part_number", table_name="products")
