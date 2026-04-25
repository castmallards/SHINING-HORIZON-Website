from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import os

from .config import settings
from .database import engine, Base
from .middleware import CSRFMiddleware, SecurityHeadersMiddleware
from .rate_limit import limiter
from .routers import (
    auth_router,
    users_router,
    categories_router,
    subcategories_router,
    brands_router,
    products_router,
    upload_router,
    import_router,
    public_router,
    audit_router,
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Shining Horizon Trading — public site (SSR) + Admin API",
    version="2.0.0",
)

# Rate limiter (Phase 5.3) — slowapi attaches the limiter to app.state and
# registers its 429 exception handler. Endpoints opt in with @limiter.limit(...).
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Security headers on every response (Phase 5.5).
app.add_middleware(
    SecurityHeadersMiddleware,
    hsts=settings.ENABLE_HSTS,
    hsts_max_age=settings.HSTS_MAX_AGE,
)

# Gzip compress every text response > 1 KB (Phase 9 perf). Cuts HTML / CSS /
# JS payload by ~70%. Already-compressed types (images, webp, woff2) are
# skipped automatically by Starlette.
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=6)

# CSRF protection on /api/* mutating requests (Phase 4.2). Registered BEFORE
# CORS so that the cookie/header check happens after preflight is handled.
app.add_middleware(
    CSRFMiddleware,
    cookie_secure=settings.COOKIE_SECURE,
    cookie_domain=settings.COOKIE_DOMAIN or None,
)

# CORS middleware (Phase 5.2). allow_credentials=True requires explicit origins
# — wildcard is no longer accepted; ALLOWED_ORIGINS must be set in .env.
allowed_origins = settings.allowed_origins_list
if not allowed_origins:
    raise RuntimeError(
        "ALLOWED_ORIGINS is empty. Configure a comma-separated list of "
        "exact origins in .env (wildcard is no longer permitted)."
    )
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-CSRF-Token"],
)

# Mount uploaded media (admin upload destination)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Mount static frontend assets (logos, brand images, hero, etc.) from /public.
# Templates reference these as /static/...
public_dir = os.path.join(settings.FRONTEND_DIR, "public")
if os.path.isdir(public_dir):
    app.mount("/static", StaticFiles(directory=public_dir), name="static")

# Mount admin SPA (legacy/admin pages live at /admin/*)
admin_dir = os.path.join(settings.FRONTEND_DIR, "admin")
if os.path.isdir(admin_dir):
    app.mount("/admin", StaticFiles(directory=admin_dir, html=True), name="admin")

# JSON API routers (admin-facing)
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(categories_router, prefix="/api")
app.include_router(subcategories_router, prefix="/api")
app.include_router(brands_router, prefix="/api")
app.include_router(products_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(import_router, prefix="/api")
app.include_router(audit_router, prefix="/api")

# Public SSR routes (must be registered LAST so they don't shadow API paths)
app.include_router(public_router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# ─── 404 handler — branded HTML for the public site, JSON for /api/* ──────
# Importing here (not at top) avoids a circular import: routers/public.py
# imports from app, and we need its `templates` instance.
from .routers.public import templates as _public_templates  # noqa: E402


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Serve a branded 404 page for HTML requests; keep JSON for API clients."""
    path = request.url.path
    accepts_html = "text/html" in request.headers.get("accept", "")
    is_api_or_admin = path.startswith("/api/") or path.startswith("/admin/") or path == "/health"
    if accepts_html and not is_api_or_admin:
        return _public_templates.TemplateResponse(
            "404.html",
            {"request": request, "current_year": __import__("datetime").datetime.utcnow().year, "is_home": False, "footer_categories": [], "meta_robots": "noindex, follow"},
            status_code=404,
        )
    return JSONResponse(status_code=404, content={"detail": exc.detail or "Not Found"})
