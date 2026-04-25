"""SEO helpers — JSON-LD builders (Phase 5.6).

Templates call these via the ``jsonld`` Jinja2 filter (registered in
``routers/public.py``). Output is pretty-printed JSON wrapped in a
``<script type="application/ld+json">`` block — that's done in the
template, this layer only produces the dict.

Schemas reference: https://schema.org
"""
from __future__ import annotations

import json
from typing import Any, Iterable, Optional


_ORG_NAME = "Shining Horizon Trading Co."


def organization(base_url: str) -> dict[str, Any]:
    """Static Organization block — used in the home page footer."""
    base = base_url.rstrip("/")
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": _ORG_NAME,
        "url": f"{base}/",
        "logo": f"{base}/static/logo/Shinning_Horizon_logo.png",
    }


def breadcrumb(items: Iterable[dict[str, Any]], base_url: str) -> dict[str, Any]:
    """BreadcrumbList. Items shape: ``[{name, url}, ...]``.

    The terminal item (current page) may omit ``url``.
    """
    base = base_url.rstrip("/")
    elements = []
    for idx, item in enumerate(items, start=1):
        entry: dict[str, Any] = {
            "@type": "ListItem",
            "position": idx,
            "name": item["name"],
        }
        url = item.get("url")
        if url:
            if url.startswith("/"):
                url = f"{base}{url}"
            entry["item"] = url
        elements.append(entry)
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": elements,
    }


def product(
    *,
    name: str,
    description: Optional[str],
    image: Optional[str],
    sku: Optional[str],
    brand: Optional[str],
    canonical_url: str,
    category: Optional[str] = None,
) -> dict[str, Any]:
    """Product schema — no ``offers`` block since the site doesn't list prices."""
    payload: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": name,
        "url": canonical_url,
    }
    if description:
        payload["description"] = description
    if image:
        payload["image"] = image
    if sku:
        payload["sku"] = sku
        payload["mpn"] = sku
    if brand:
        payload["brand"] = {"@type": "Brand", "name": brand}
    if category:
        payload["category"] = category
    return payload


def to_script(payload: dict[str, Any]) -> str:
    """Serialize and wrap in a script tag. Escapes ``</`` to prevent breakout."""
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    body = body.replace("</", "<\\/")
    return f'<script type="application/ld+json">{body}</script>'
