"""Public SSR routes — render Jinja2 templates from DB state.

Per ARCHITECTURE.md §1: the database is the source of truth. No HTML files
are written to disk. Each request reads the DB (via 60s cache for hot reads)
and renders a Jinja2 template.
"""
from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from ..cache import cache
from ..database import get_db
from ..models._common import ContentStatus
from ..models.brand import Brand
from ..models.category import Category, CategoryType
from ..models.product import Product
from ..models.subcategory import Subcategory
from ..services import seo
from ..services.image import variant_url


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)
templates.env.filters["variant"] = variant_url
templates.env.filters["jsonld"] = seo.to_script


def _published(query, model):
    """Filter a query to status=PUBLISHED."""
    return query.filter(model.status == ContentStatus.PUBLISHED)


def _is_admin_preview(request: Request) -> bool:
    """True when the request is an authenticated admin asking for a draft preview.

    Triggered by ``?preview=1`` AND a valid ``sh_session`` cookie. Used by the
    detail routes to bypass the published-only filter so admins can review
    Draft content before publishing.
    """
    if request.query_params.get("preview") not in ("1", "true", "yes"):
        return False
    from ..services.auth import _extract_token, AuthService  # local import avoids cycle
    token = _extract_token(request)
    if not token:
        return False
    payload = AuthService.decode_token(token)
    return bool(payload and payload.get("sub"))


def _detail_query(request: Request, query, model):
    """Apply the published filter unless the requester is an admin previewing a draft."""
    return query if _is_admin_preview(request) else _published(query, model)


def _ctx(request: Request, **extra) -> dict:
    """Base template context shared by every page."""
    ctx = {
        "request": request,
        "current_year": datetime.utcnow().year,
        "is_home": False,
        "is_preview": _is_admin_preview(request),
    }
    ctx.update(extra)
    return ctx


# ─── Cached read helpers ──────────────────────────────────────────────

def _published_categories(db: Session) -> list[Category]:
    def _load():
        return (
            _published(db.query(Category), Category)
            .order_by(Category.display_order, Category.name)
            .all()
        )
    return cache.get_or_set("public:categories:all", _load)


def _published_brands(db: Session) -> list[Brand]:
    def _load():
        return (
            _published(db.query(Brand), Brand)
            .order_by(Brand.display_order, Brand.name)
            .all()
        )
    return cache.get_or_set("public:brands:all", _load)


def _footer_categories(db: Session) -> list[Category]:
    """Up to 4 published categories shown in the footer."""
    return _published_categories(db)[:4]


def _card_dict(p: Product) -> dict:
    """Lean dict shape used by every product-card template (home, search, featured).

    Includes ``gallery`` (the parsed list of secondary images) so cards can
    render the multi-image carousel without a second DB hit.
    """
    return {
        "id": p.id,
        "slug": p.slug,
        "name": p.name,
        "image": p.image,
        "part_number": p.part_number,
        "short_description": p.short_description,
        "brand_name": p.brand.name if p.brand else None,
        "category_name": p.category.name if p.category else None,
        "category_slug": p.category.slug if p.category else None,
        "gallery": p.gallery_list,
    }


# ─── Router ───────────────────────────────────────────────────────────

router = APIRouter(tags=["Public"])


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    footer_categories = _footer_categories(db)

    # Featured products — surfaced in the "Featured Products" home section.
    # Prefers is_featured=True; falls back to most-recent published if fewer than 8.
    def _featured() -> list:
        rows = (
            _published(db.query(Product), Product)
            .options(joinedload(Product.brand), joinedload(Product.category))
            .order_by(Product.is_featured.desc(), Product.display_order, Product.id)
            .limit(8)
            .all()
        )
        return [_card_dict(p) for p in rows]
    featured_products = cache.get_or_set("public:featured:home", _featured)

    return templates.TemplateResponse(
        "home.html",
        _ctx(
            request,
            is_home=True,
            footer_categories=footer_categories,
            featured_products=featured_products,
            meta_description="Shining Horizon Trading — industrial automation, electrical, lifting, pneumatic, safety and tools across Saudi Arabia.",
            jsonld_blocks=[seo.organization(str(request.base_url))],
        ),
    )


@router.get("/categories", response_class=HTMLResponse)
def categories_index(request: Request, db: Session = Depends(get_db)):
    categories = _published_categories(db)

    # Live published-product count per category. Cached so it's a single query
    # per cache window even with many categories.
    def _counts():
        from sqlalchemy import func
        rows = (
            db.query(Product.category_id, func.count(Product.id))
            .filter(Product.status == ContentStatus.PUBLISHED, Product.category_id.isnot(None))
            .group_by(Product.category_id)
            .all()
        )
        return {cid: count for cid, count in rows}
    category_counts = cache.get_or_set("public:category_counts", _counts)

    return templates.TemplateResponse(
        "categories_index.html",
        _ctx(
            request,
            categories=categories,
            category_counts=category_counts,
            footer_categories=categories[:4],
            meta_title="All Categories — Shining Horizon Trading",
            meta_description="Explore Shining Horizon's full range of industrial product categories.",
            jsonld_blocks=[
                seo.breadcrumb(
                    [{"name": "Home", "url": "/"}, {"name": "Categories"}],
                    str(request.base_url),
                ),
            ],
        ),
    )


@router.get("/search", response_class=HTMLResponse)
def search(
    request: Request,
    q: Optional[str] = Query(None, description="Search query"),
    db: Session = Depends(get_db),
):
    """Public product search across name, part number, slug, descriptions and brand name.

    No auth required. Pagination kept simple (top 60 hits) since most users
    refine their query rather than scroll. Results are cached per query for 60s.
    """
    query_str = (q or "").strip()
    results: list = []
    total = 0

    if query_str:
        def _do_search():
            like = f"%{query_str}%"
            rows = (
                _published(db.query(Product), Product)
                .options(joinedload(Product.brand), joinedload(Product.category))
                .outerjoin(Brand, Product.brand_id == Brand.id)
                .filter(or_(
                    Product.name.ilike(like),
                    Product.part_number.ilike(like),
                    Product.slug.ilike(like),
                    Product.short_description.ilike(like),
                    Product.description.ilike(like),
                    Brand.name.ilike(like),
                ))
                .order_by(Product.is_featured.desc(), Product.display_order, Product.id)
                .limit(60)
                .all()
            )
            return [_card_dict(p) for p in rows]
        cache_key = f"public:search:{query_str.lower()}"
        results = cache.get_or_set(cache_key, _do_search)
        total = len(results)

    return templates.TemplateResponse(
        "search.html",
        _ctx(
            request,
            query=query_str,
            results=results,
            total=total,
            footer_categories=_footer_categories(db),
            meta_title=(f"Search: {query_str}" if query_str else "Search Products") + " — Shining Horizon Trading",
            meta_description="Search Shining Horizon's full catalog by product name, brand or part number.",
            meta_robots="noindex, follow",
            jsonld_blocks=[
                seo.breadcrumb(
                    [{"name": "Home", "url": "/"}, {"name": "Search"}],
                    str(request.base_url),
                ),
            ],
        ),
    )


@router.get("/category/{slug}", response_class=HTMLResponse)
def category_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    category = (
        _detail_query(request, db.query(Category), Category)
        .filter(Category.slug == slug)
        .first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    footer_categories = _footer_categories(db)

    base_url = str(request.base_url)
    cat_breadcrumb = seo.breadcrumb(
        [{"name": "Home", "url": "/"}, {"name": "Categories", "url": "/categories"}, {"name": category.name}],
        base_url,
    )

    if category.type == CategoryType.DETAILED:
        subcategories = (
            _published(
                db.query(Subcategory).filter(Subcategory.category_id == category.id),
                Subcategory,
            )
            .order_by(Subcategory.display_order, Subcategory.name)
            .all()
        )
        brands = _published_brands(db)
        return templates.TemplateResponse(
            "category_detailed.html",
            _ctx(
                request,
                category=category,
                subcategories=subcategories,
                brands=brands,
                footer_categories=footer_categories,
                meta_title=category.meta_title or f"{category.name} — Shining Horizon Trading",
                meta_description=category.meta_description or category.description,
                jsonld_blocks=[cat_breadcrumb],
            ),
        )

    # SIMPLE
    products = [
        _card_dict(p) for p in
        _published(
            db.query(Product).filter(Product.category_id == category.id),
            Product,
        )
        .order_by(Product.display_order, Product.name)
        .all()
    ]
    brands = _published_brands(db)
    return templates.TemplateResponse(
        "category_simple.html",
        _ctx(
            request,
            category=category,
            products=products,
            brands=brands,
            footer_categories=footer_categories,
            meta_title=category.meta_title or f"{category.name} — Shining Horizon Trading",
            meta_description=category.meta_description or category.description,
            jsonld_blocks=[cat_breadcrumb],
        ),
    )


@router.get("/category/{cat_slug}/{sub_slug}", response_class=HTMLResponse)
def subcategory_detail(
    cat_slug: str,
    sub_slug: str,
    request: Request,
    db: Session = Depends(get_db),
):
    category = (
        _detail_query(request, db.query(Category), Category)
        .filter(Category.slug == cat_slug)
        .first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    subcategory = (
        _detail_query(
            request,
            db.query(Subcategory).filter(
                Subcategory.category_id == category.id,
                Subcategory.slug == sub_slug,
            ),
            Subcategory,
        )
        .first()
    )
    if not subcategory:
        raise HTTPException(status_code=404, detail="Subcategory not found")

    products = (
        _published(
            db.query(Product)
            .options(joinedload(Product.brand))
            .filter(Product.subcategory_id == subcategory.id),
            Product,
        )
        .order_by(Product.display_order, Product.name)
        .all()
    )

    products_with_brands = [{"product": p, "brand": p.brand} for p in products]

    sub_breadcrumb = seo.breadcrumb(
        [
            {"name": "Home", "url": "/"},
            {"name": "Categories", "url": "/categories"},
            {"name": category.name, "url": f"/category/{category.slug}"},
            {"name": subcategory.name},
        ],
        str(request.base_url),
    )

    return templates.TemplateResponse(
        "product_listing.html",
        _ctx(
            request,
            category=category,
            subcategory=subcategory,
            products=products_with_brands,
            footer_categories=_footer_categories(db),
            meta_title=subcategory.meta_title or f"{subcategory.name} — {category.name}",
            meta_description=subcategory.meta_description or subcategory.description or category.description,
            jsonld_blocks=[sub_breadcrumb],
        ),
    )


@router.get("/brands", response_class=HTMLResponse)
def brands_index(request: Request, db: Session = Depends(get_db)):
    brands = _published_brands(db)
    return templates.TemplateResponse(
        "brands_index.html",
        _ctx(
            request,
            brands=brands,
            footer_categories=_footer_categories(db),
            meta_title="Trusted Brands — Shining Horizon Trading",
            meta_description="Trusted manufacturers Shining Horizon partners with for industrial automation, electrical, lifting and safety solutions.",
            jsonld_blocks=[
                seo.breadcrumb(
                    [{"name": "Home", "url": "/"}, {"name": "Brands"}],
                    str(request.base_url),
                ),
            ],
        ),
    )


@router.get("/brand/{slug}", response_class=HTMLResponse)
def brand_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    brand = (
        _detail_query(request, db.query(Brand), Brand)
        .filter(Brand.slug == slug)
        .first()
    )
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    # Products from this brand (published only). Phase 3 introduces a dedicated
    # brand_detail.html template; until then redirect-style render reuses the
    # category_simple shape with a synthesized "category" object so existing
    # markup works without a new template file.
    products = [
        _card_dict(p) for p in
        _published(
            db.query(Product).filter(Product.brand_id == brand.id),
            Product,
        )
        .order_by(Product.display_order, Product.name)
        .limit(60)
        .all()
    ]

    pseudo_category = type("PseudoCategory", (), {
        "name": brand.name,
        "slug": brand.slug,
        "description": brand.description,
        "image": brand.logo,
        "hero_title": f"{brand.name} Products",
        "hero_description": brand.description,
        "tags": [brand.country] if brand.country else [],
    })()

    brand_breadcrumb = seo.breadcrumb(
        [
            {"name": "Home", "url": "/"},
            {"name": "Brands", "url": "/brands"},
            {"name": brand.name},
        ],
        str(request.base_url),
    )

    return templates.TemplateResponse(
        "category_simple.html",
        _ctx(
            request,
            category=pseudo_category,
            products=products,
            brands=[],
            footer_categories=_footer_categories(db),
            meta_title=f"{brand.name} — Shining Horizon Trading",
            meta_description=brand.description or f"Products from {brand.name} available through Shining Horizon Trading.",
            jsonld_blocks=[brand_breadcrumb],
        ),
    )


@router.get("/product/{slug}", response_class=HTMLResponse)
def product_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    product = (
        _detail_query(
            request,
            db.query(Product).options(
                joinedload(Product.category),
                joinedload(Product.subcategory),
                joinedload(Product.brand),
            ),
            Product,
        )
        .filter(Product.slug == slug)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Related products: same subcategory (or category fallback), exclude self,
    # prefer published, limit 4.
    related_q = _published(db.query(Product), Product).filter(Product.id != product.id)
    if product.subcategory_id:
        related_q = related_q.filter(Product.subcategory_id == product.subcategory_id)
    elif product.category_id:
        related_q = related_q.filter(Product.category_id == product.category_id)
    related_rows = related_q.order_by(Product.display_order, Product.id).limit(4).all()
    related_products = [
        {
            "id": r.id,
            "name": r.name,
            "slug": r.slug,
            "image": r.image,
            "part_number": r.part_number,
            "short_description": r.short_description,
            "brand_name": r.brand.name if r.brand else None,
        }
        for r in related_rows
    ]

    # Gallery: main image first, then any additional gallery images.
    # De-duplicate so the cover image is never listed twice.
    raw_gallery = list(product.gallery_list or [])
    if product.image:
        gallery_items = [product.image] + [g for g in raw_gallery if g != product.image]
    else:
        gallery_items = raw_gallery

    canonical = str(request.url_for("product_detail", slug=product.slug))
    base_url = str(request.base_url)
    hero_image = variant_url(product.image, "hero") if product.image else None
    if hero_image and hero_image.startswith("/"):
        hero_image_abs = base_url.rstrip("/") + hero_image
    else:
        hero_image_abs = hero_image

    breadcrumb_items: list[dict[str, str]] = [{"name": "Home", "url": "/"}]
    if product.category:
        breadcrumb_items.append({"name": product.category.name, "url": f"/category/{product.category.slug}"})
    if product.subcategory and product.category:
        breadcrumb_items.append({
            "name": product.subcategory.name,
            "url": f"/category/{product.category.slug}/{product.subcategory.slug}",
        })
    breadcrumb_items.append({"name": product.name})

    jsonld_blocks = [
        seo.product(
            name=product.name,
            description=product.short_description or product.description,
            image=hero_image_abs,
            sku=product.part_number,
            brand=product.brand.name if product.brand else None,
            canonical_url=canonical,
            category=product.category.name if product.category else None,
        ),
        seo.breadcrumb(breadcrumb_items, base_url),
    ]

    return templates.TemplateResponse(
        "product_detail.html",
        _ctx(
            request,
            product=product,
            category=product.category,
            subcategory=product.subcategory,
            brand=product.brand,
            specifications=product.specifications_list,
            gallery_items=gallery_items,
            related_products=related_products,
            footer_categories=_footer_categories(db),
            meta_title=product.meta_title or f"{product.name} — Shining Horizon Trading",
            meta_description=product.meta_description or product.short_description or product.description,
            canonical_url=canonical,
            og_image=hero_image_abs,
            og_type="product",
            jsonld_blocks=jsonld_blocks,
        ),
    )


@router.get("/quote", response_class=HTMLResponse)
def quote_form(
    request: Request,
    db: Session = Depends(get_db),
    product: Optional[str] = None,
    brand: Optional[str] = None,
    category: Optional[str] = None,
):
    return templates.TemplateResponse(
        "quote.html",
        _ctx(
            request,
            prefill_product=product,
            prefill_brand=brand,
            prefill_category=category,
            footer_categories=_footer_categories(db),
            meta_description="Request a quote on industrial equipment from Shining Horizon Trading. Response within 24 hours.",
        ),
    )


@router.get("/products", response_class=HTMLResponse)
def products_index(
    request: Request,
    db: Session = Depends(get_db),
    q: str = Query(None),
    category: str = Query(None),
    brand: str = Query(None),
):
    query = _published(db.query(Product).options(
        joinedload(Product.brand),
        joinedload(Product.category),
    ), Product)

    if q:
        like = f"%{q}%"
        query = query.filter(
            Product.name.ilike(like) | Product.part_number.ilike(like)
        )
    if category:
        query = query.join(Category, Product.category_id == Category.id).filter(Category.slug == category)
    if brand:
        query = query.join(Brand, Product.brand_id == Brand.id).filter(Brand.slug == brand)

    products = [_card_dict(p) for p in query.order_by(Product.display_order, Product.name).all()]
    categories = _published(db.query(Category), Category).order_by(Category.display_order, Category.name).all()
    brands = _published_brands(db)

    return templates.TemplateResponse(
        "products_index.html",
        _ctx(
            request,
            products=products,
            categories=categories,
            brands=brands,
            active_category=category,
            active_brand=brand,
            search_q=q or "",
            total=len(products),
            footer_categories=_footer_categories(db),
            meta_title="All Products — Shining Horizon Trading",
            meta_description="Browse our full catalog of industrial automation, lifting equipment, safety and electrical products.",
        ),
    )


@router.get("/sitemap.xml")
def sitemap(request: Request, db: Session = Depends(get_db)):
    def _build() -> str:
        base = str(request.base_url).rstrip("/")
        urls: list[tuple[str, str]] = [(f"{base}/", "1.0")]
        urls.append((f"{base}/categories", "0.8"))
        urls.append((f"{base}/brands", "0.7"))
        urls.append((f"{base}/quote", "0.6"))

        for c in _published_categories(db):
            urls.append((f"{base}/category/{c.slug}", "0.8"))

        subs = (
            _published(
                db.query(Subcategory, Category).join(Category, Subcategory.category_id == Category.id),
                Subcategory,
            )
            .filter(Category.status == ContentStatus.PUBLISHED)
            .all()
        )
        for sub, cat in subs:
            urls.append((f"{base}/category/{cat.slug}/{sub.slug}", "0.7"))

        for b in _published_brands(db):
            urls.append((f"{base}/brand/{b.slug}", "0.6"))

        prods = (
            _published(db.query(Product), Product)
            .order_by(Product.id)
            .limit(50000)
            .all()
        )
        for p in prods:
            urls.append((f"{base}/product/{p.slug}", "0.5"))

        body = "\n".join(
            f"  <url><loc>{loc}</loc><priority>{prio}</priority></url>"
            for loc, prio in urls
        )
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{body}\n"
            "</urlset>\n"
        )

    xml = cache.get_or_set("public:sitemap", _build, ttl=3600.0)
    return Response(content=xml, media_type="application/xml")


@router.get("/robots.txt", response_class=PlainTextResponse)
def robots(request: Request):
    base = str(request.base_url).rstrip("/")
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin/\n"
        "Disallow: /api/\n"
        f"Sitemap: {base}/sitemap.xml\n"
    )
