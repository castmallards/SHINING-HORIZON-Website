# Architecture — Shining Horizon Catalog v2

> Single source of truth for how the upgraded system is built. Reference this file when changing structure.

---

## 1. System overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        CLIENT BROWSER                            │
│   (public site visitors + admin users — same browser, same UI)   │
└─────────────────────────┬────────────────────────────────────────┘
                          │ HTTPS
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                          NGINX                                   │
│   - serves /uploads/* directly (images, files)                   │
│   - serves /admin/* (static admin SPA assets)                    │
│   - reverse-proxies everything else to FastAPI                   │
└─────────────────────────┬────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                   FASTAPI (uvicorn, port 8000)                   │
│                                                                  │
│  Public routes (Jinja2 SSR)        Admin API (JSON)              │
│  ─────────────────────────         ─────────────────────         │
│  GET /                             POST /api/auth/login          │
│  GET /categories                   GET  /api/products            │
│  GET /category/{slug}              POST /api/products            │
│  GET /category/{c}/{sub}           PUT  /api/products/{id}       │
│  GET /product/{slug}               DELETE /api/products/{id}     │
│  GET /brands                       (and same for categories,     │
│  GET /brand/{slug}                  subcategories, brands,       │
│  GET /quote                        users, uploads, audit)        │
│  GET /sitemap.xml                                                │
│                                                                  │
│  In-memory cache (60s TTL) on hot reads                          │
└─────────────────────────┬────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│             SQLite (backend/shining_horizon.db)                  │
│             managed via Alembic migrations                       │
└──────────────────────────────────────────────────────────────────┘
```

Key principle: **the database is the source of truth. No HTML files are ever written to disk.** When a customer requests a page, FastAPI reads the database, renders a Jinja2 template, returns HTML. When an admin saves a change, the next visitor sees it.

---

## 2. Directory layout

```
shinning horizon/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app, mounts routers, middleware
│   │   ├── config.py                # Settings loaded from .env
│   │   ├── database.py              # SQLAlchemy engine + session
│   │   ├── cache.py                 # Simple in-memory TTL cache
│   │   ├── deps.py                  # Common FastAPI dependencies
│   │   │
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── category.py
│   │   │   ├── subcategory.py
│   │   │   ├── brand.py
│   │   │   ├── product.py
│   │   │   └── audit.py             # NEW: audit log table
│   │   │
│   │   ├── schemas/                 # Pydantic request/response shapes
│   │   │
│   │   ├── services/                # Business logic
│   │   │   ├── auth.py
│   │   │   ├── slug.py              # Slug generation + uniqueness
│   │   │   ├── image.py             # NEW: variant generation (thumb/card/hero, WebP)
│   │   │   ├── audit.py             # NEW: write audit log entries
│   │   │   ├── seo.py               # NEW: meta tags, JSON-LD builders
│   │   │   ├── sitemap.py           # NEW: sitemap.xml generator
│   │   │   └── (one per resource: category.py, product.py, ...)
│   │   │
│   │   ├── routers/
│   │   │   ├── public.py            # NEW: SSR public routes (renders Jinja2)
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── categories.py        # JSON API
│   │   │   ├── subcategories.py     # JSON API
│   │   │   ├── brands.py            # JSON API
│   │   │   ├── products.py          # JSON API
│   │   │   ├── upload.py
│   │   │   ├── import_data.py       # CSV import (kept for occasional bulk ops)
│   │   │   └── audit.py             # NEW: audit log endpoint
│   │   │   # generator.py — DELETED in v2
│   │   │
│   │   └── templates/               # Jinja2 templates (SSR)
│   │       ├── _base.html           # NEW: shared layout (head, header, footer)
│   │       ├── _head.html           # NEW: meta tags, SEO, fonts
│   │       ├── _header.html         # NEW: nav (replaces components/header.js injection)
│   │       ├── _footer.html         # NEW: footer
│   │       ├── _macros.html         # NEW: card, breadcrumb, brand-strip macros
│   │       ├── home.html            # NEW: homepage
│   │       ├── categories_index.html # NEW: all categories
│   │       ├── category_detailed.html  # existing template, refactored to extend _base
│   │       ├── category_simple.html    # existing template, refactored
│   │       ├── product_listing.html    # existing template, refactored (subcategory listing)
│   │       ├── product_detail.html  # NEW: single-product page
│   │       ├── brands_index.html    # NEW
│   │       ├── brand_detail.html    # NEW
│   │       └── quote.html           # NEW (replaces /quote.html)
│   │
│   ├── alembic/                     # NEW: schema migrations
│   │   ├── env.py
│   │   └── versions/
│   ├── alembic.ini                  # NEW
│   ├── .env.example                 # NEW: documents required env vars
│   ├── init_db.py                   # kept, but defers schema to Alembic
│   ├── requirements.txt
│   ├── shining_horizon.db
│   └── uploads/                     # serves /uploads
│       ├── products/
│       ├── categories/
│       ├── brands/
│       └── subcategories/
│
├── admin/                           # Static admin dashboard (vanilla JS)
│   ├── login.html
│   ├── index.html
│   ├── categories.html
│   ├── subcategories.html
│   ├── products.html
│   ├── brands.html
│   ├── users.html
│   ├── import.html
│   ├── audit.html                   # NEW: audit log viewer
│   └── assets/
│       ├── api.js                   # Existing fetch wrapper, refactored
│       ├── auth.js                  # NEW: cookie-based session helpers
│       ├── ui.js                    # NEW: shared modal/toast/form helpers
│       ├── editor.js                # NEW: TipTap rich-text wrapper
│       ├── gallery.js               # NEW: multi-image upload widget
│       ├── specs.js                 # NEW: key/value spec builder
│       └── style.css
│
├── public/                          # Static assets only (logos, brand images, hero)
│   ├── logo/
│   ├── hero/
│   ├── brands/
│   ├── categories/
│   ├── products/
│   └── Clients/
│
├── components/                      # KEPT for legacy header/footer JS during migration
│   ├── header.js                    # to be retired once SSR is live
│   ├── footer.js
│   └── shared-styles.css
│
├── docs/
│   ├── ARCHITECTURE.md              # this file
│   ├── DATA_ENTRY_GUIDE.md
│   ├── MANAGER_BRIEF.md
│   └── TASKS.md                     # task tracking
│
└── (root-level .html files: TO BE DELETED in Phase 2 once SSR routes are live)
```

---

## 3. Data model

### Existing tables (extended)

#### `users`
| Column | Type | Notes |
|---|---|---|
| id | int PK | |
| username | varchar(50) unique | |
| email | varchar(100) unique | |
| password_hash | varchar(255) | bcrypt |
| full_name | varchar(100) | |
| role | enum(super_admin, admin) | |
| is_active | bool | |
| created_at, updated_at | datetime | |

#### `categories` *(extended)*
| Column | Type | Notes |
|---|---|---|
| id | int PK | |
| name | varchar(100) | |
| slug | varchar(100) unique | |
| type | enum(detailed, simple) | |
| description | text | |
| image | varchar(255) | |
| hero_title | text | |
| hero_description | text | |
| display_order | int | |
| is_active | bool | legacy — replaced by `status` |
| show_on_home | bool | |
| **status** *(new)* | enum(draft, published) | |
| **meta_title** *(new)* | varchar(160) | |
| **meta_description** *(new)* | varchar(320) | |
| created_at, updated_at | datetime | |
| **created_by_user_id** *(new)* | int FK users.id | |
| **updated_by_user_id** *(new)* | int FK users.id | |

#### `subcategories` *(extended)*
Same additions as categories: `status`, `meta_title`, `meta_description`, `created_by`, `updated_by`.

#### `brands` *(extended)*
Add: `description (text)`, `website_url (varchar 255)`, `country (varchar 100)`, `status`, `created_by`, `updated_by`.

#### `products` *(extended)*
| Column | Type | Notes |
|---|---|---|
| (existing fields) | | |
| **status** *(new)* | enum(draft, published) | |
| **meta_title** *(new)* | varchar(160) | |
| **meta_description** *(new)* | varchar(320) | |
| **specifications** *(new)* | JSON | array of `{key, value}` objects |
| **gallery** *(new)* | JSON | array of image paths |
| **datasheet_url** *(new)* | varchar(500) | |
| **created_by_user_id** *(new)* | int FK | |
| **updated_by_user_id** *(new)* | int FK | |

### New table

#### `audit_log`
| Column | Type |
|---|---|
| id | int PK |
| user_id | int FK users.id |
| action | enum(create, update, delete, publish, unpublish) |
| entity_type | varchar(50) — e.g. `product`, `category` |
| entity_id | int |
| entity_label | varchar(255) — name at time of action, for human reading |
| changes | JSON — `{field: [old, new]}` for updates |
| created_at | datetime |
| ip_address | varchar(45) |

---

## 4. URL design

### Public URLs (clean, SEO-friendly)
| URL | Renders |
|---|---|
| `/` | home.html |
| `/categories` | categories_index.html |
| `/category/{slug}` | category_detailed.html OR category_simple.html (chosen by `category.type`) |
| `/category/{cat-slug}/{sub-slug}` | product_listing.html (products in that subcategory) |
| `/product/{slug}` | product_detail.html |
| `/brands` | brands_index.html |
| `/brand/{slug}` | brand_detail.html |
| `/quote` | quote.html |
| `/sitemap.xml` | dynamically generated |
| `/robots.txt` | static |

### Admin URLs (unchanged)
| URL | |
|---|---|
| `/admin/login.html` | login |
| `/admin/index.html` | dashboard |
| `/admin/{products\|categories\|...}.html` | resource pages |

### API URLs (now under `/api`)
All admin-facing endpoints move under `/api/*` prefix to keep them clearly separated from public SSR routes.

---

## 5. Authentication

- **Storage**: `httpOnly` Secure cookie (not `localStorage`).
- **Token**: JWT, HS256, 24h expiry, secret in `.env`.
- **Login endpoint**: `POST /api/auth/login` → sets cookie + returns user JSON.
- **Logout**: `POST /api/auth/logout` → clears cookie.
- **Rate limit**: 5 attempts per 15 minutes per IP on `/api/auth/login` (slowapi).
- **CSRF**: double-submit cookie pattern for admin form submits.
- **Role checks**: `Depends(require_admin)` and `Depends(require_super_admin)` on routes.

---

## 6. Image pipeline

On upload to `POST /api/upload/image/{folder}`:
1. Validate type (png/jpg/webp/svg) and size (≤ 5MB).
2. Save original to `backend/uploads/{folder}/originals/{uuid}.{ext}`.
3. Generate three variants using Pillow:
   - `thumb`: 300×300, WebP, quality 80
   - `card`: 600×600, WebP, quality 85
   - `hero`: 1600×900 (or 1600×1600 for square sources), WebP, quality 85
4. Store variants at `backend/uploads/{folder}/{variant}/{uuid}.webp`.
5. Database stores the **base path** (e.g. `uploads/products/{uuid}`); templates pick variant via filter (e.g. `image | variant('card')`).
6. SVG bypasses variant generation (vector — no resize needed).

---

## 7. Caching

Simple in-memory TTL dict in `app/cache.py`:
- 60-second TTL on category lists, brand lists, sitemap.
- Invalidated on any write via service-layer hook.
- No external cache server required for current scale.

If/when concurrent admin editors or multi-process deployment is needed, swap for Redis. Interface stays the same.

---

## 8. SEO layer

Each public route passes the following to `_head.html`:
- `meta_title` — from DB `meta_title` field, fallback to `name + " — Shining Horizon Trading"`.
- `meta_description` — from DB or first 160 chars of description.
- `canonical_url` — full URL of current page.
- `og_image` — main image, hero variant.
- `json_ld` — for product pages, render `Product` schema; for breadcrumbs everywhere render `BreadcrumbList`.

`/sitemap.xml` lists all published categories, subcategories, products, brands. Regenerated on demand (cached 1 hour).

---

## 9. Audit logging

Every write through the service layer calls `audit.log(user, action, entity, changes)`.
- Visible at `/admin/audit.html` (super_admin only).
- Filterable by user, entity type, date range.
- Retention: indefinite (small table, low volume).

---

## 10. Deployment

### Dev
```
cd backend
python -m venv venv && source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # edit SECRET_KEY, ALLOWED_ORIGINS
alembic upgrade head
python init_db.py     # creates super admin only
uvicorn app.main:app --reload --port 8000
```
Public site: `http://localhost:8000/`
Admin: `http://localhost:8000/admin/login.html`

### Production
- Nginx terminates TLS, serves `/uploads/*` and `/admin/*` directly, proxies all other paths to uvicorn.
- Uvicorn under Supervisor or systemd, 2–4 workers.
- Daily SQLite backup via cron → off-server (S3 / Backblaze).
- Sentry (or simple log file) for error tracking.
- Migrations applied during deploy: `alembic upgrade head`.

### Required env vars (.env)
```
APP_NAME=Shining Horizon
DEBUG=false
DATABASE_URL=sqlite:///./shining_horizon.db
SECRET_KEY=<32+ random chars — DO NOT use placeholder>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE=5242880
ALLOWED_ORIGINS=https://shininghorizon.com,https://www.shininghorizon.com
COOKIE_SECURE=true
COOKIE_DOMAIN=shininghorizon.com
```

---

## 11. What is being removed

These files/concepts go away in v2:
- `backend/app/services/generator.py` — DELETED
- `backend/app/routers/generator.py` — DELETED
- All `category-*.html` and `product-*.html` files in project root — DELETED after Phase 2
- `components/header.js` and `components/footer.js` runtime injection — REPLACED by SSR `_header.html` / `_footer.html` partials (the JS files stay during migration, removed at end of Phase 2)
- `is_active` boolean — kept for backward compatibility but new code uses `status` enum
- `localStorage.admin_token` — replaced by httpOnly cookie

---

## 12. What is staying the same

- Visual design, colours (#2d8bc9), Tailwind CDN, AOS animations, Inter + Noto Sans Arabic fonts.
- FastAPI + SQLAlchemy + SQLite + Jinja2 stack.
- Admin dashboard tech (vanilla JS) — incrementally improved, not rewritten.
- Image upload locations and file size limits.
- CSV import endpoints (kept for occasional bulk ops, not the primary entry path).
- JWT auth approach (just changing the storage mechanism).
