# Tasks — Shining Horizon v2 Upgrade

> Living task file. Status legend: `[ ]` todo · `[~]` in progress · `[x]` done · `[!]` blocked
> Each task is small enough to complete in one sitting. When done, mark `[x]` and note the date.

---

## Phase 1 — Schema & Infrastructure  ✅ COMPLETE (2026-04-22)

- [x] **1.1** Create `backend/.env.example` with all required vars (see ARCHITECTURE.md §10)
- [x] **1.2** Update `backend/app/config.py` to read from `.env` (already does — verify SECRET_KEY no longer has hard-coded fallback)
- [x] **1.3** Add `alembic` to `requirements.txt`
- [x] **1.4** Initialise Alembic: `alembic init backend/alembic`, configure `env.py` to use `app.database.Base`
- [x] **1.5** Generate baseline migration capturing the *current* schema (autogenerate against existing DB)
- [x] **1.6** Add `status` enum + columns to `categories`, `subcategories`, `brands`, `products` (migration 002)
- [x] **1.7** Add `meta_title` + `meta_description` to `categories`, `subcategories`, `products` (migration 003)
- [x] **1.8** Add `created_by_user_id` + `updated_by_user_id` to all content tables (migration 004)
- [x] **1.9** Extend `brands` with `description`, `website_url`, `country` (migration 005)
- [x] **1.10** Extend `products` with `specifications` (JSON), `gallery` (JSON), `datasheet_url` (migration 006)
- [x] **1.11** Create `audit_log` table (migration 007)
- [x] **1.12** Update SQLAlchemy models to match new schema
- [x] **1.13** Update Pydantic schemas to expose new fields
- [x] **1.14** Backfill existing rows: set `status='published'` where `is_active=true`, else `status='draft'`  *(folded into migration 002)*
- [x] **1.15** Add Pillow to requirements (image variants); slowapi (rate limiting); itsdangerous (cookie signing)
- [x] **Verification** — stamped baseline, applied 002–007, app boots, models read existing rows (11 categories, 22 subcategories, 111 brands, 14,801 products all backfilled to 'published'). DB backed up to `backend/shining_horizon.db.pre_v2_backup`.

## Phase 2 — Replace generator with SSR public routes  ✅ COMPLETE (2026-04-22)

- [x] **2.1** Create `app/templates/_base.html` extracting common shell (head, header, footer)
- [x] **2.2** Create `_head.html`, `_header.html`, `_footer.html`, `_macros.html` partials
- [x] **2.3** Refactor existing `category_detailed.html`, `category_simple.html`, `product_listing.html` to extend `_base.html`
- [x] **2.4** Create `home.html` template (port from current root `index.html`)
- [x] **2.5** Create `categories_index.html` (port from current `categories.html`)
- [x] **2.6** Create `brands_index.html` (port from current `brands.html`)
- [x] **2.7** Create `quote.html` template (port from current root `quote.html`)
- [x] **2.8** Create `app/routers/public.py` with all SSR routes (see ARCHITECTURE.md §4)
- [x] **2.9** Add `app/cache.py` (in-memory TTL cache, 60s)
- [x] **2.10** Wire cache invalidation into category/subcategory/brand/product service writes
- [x] **2.11** Move existing JSON CRUD routes under `/api/*` prefix (update admin `assets/api.js` accordingly)
- [x] **2.12** Smoke test every public URL renders correctly with seed data
- [x] **2.13** Delete `app/services/generator.py` and `app/routers/generator.py`
- [x] **2.14** Delete root-level `category-*.html` and `product-*.html` files
- [x] **2.15** Remove "Generate Pages" button from admin dashboard + sidebar
- [x] **2.16** Update `components/header.js` / `footer.js` references (templates now provide nav directly)
- [x] **Verification** — uvicorn boots, all 14 public URLs return 200 (or expected 302/404), 14801 published products / 22 subcats / 11 categories / 111 brands render. `/api/*` endpoints intact, cache invalidation wired into all 4 content services.

## Phase 3 — Per-product pages & image pipeline  ✅ COMPLETE (2026-04-23)

- [x] **3.1** Create `product_detail.html` template (gallery, specs table, datasheet, related products, quote CTA)
- [x] **3.2** Add `GET /product/{slug}` route + `related_products` query (same subcategory, exclude self, limit 4)
- [x] **3.3** Build `app/services/image.py` — Pillow-based variant generator (thumb/card/hero, WebP)
- [x] **3.4** Update `routers/upload.py` to call image service after save; return base path
- [x] **3.5** Add Jinja2 filter `variant(name)` for templates to pick the right size
- [x] **3.6** Add SVG bypass (no variant generation; SVG base path includes extension so legacy passthrough handles it)
- [x] **3.7** Update product_detail and product cards to use new `variant()` filter
- [x] **3.8** Add `loading="lazy"` and proper `alt` attributes everywhere
- [x] **Verification** — `/product/{slug}` returns 200 with breadcrumb / specs / related products / datasheet / quote CTA. Upload pipeline round-trips PNG → originals/.png + thumb/card/hero/.webp variants on disk; SVG bypasses variant generation and `variant()` returns the original .svg URL. Legacy paths (`/uploads/...`, `backend/uploads/...`, `/static/...`) pass through unchanged. All `<img>` in templates now have `loading="lazy"` (except above-the-fold product hero) and meaningful `alt`.

## Phase 4 — Admin upgrades  ✅ COMPLETE (2026-04-23)

- [x] **4.1** Replace `localStorage.admin_token` with httpOnly cookie auth (`auth.js`) — `sh_session` cookie set by `POST /api/auth/login`, cleared by `POST /api/auth/logout`. `get_current_user` reads cookie first, falls back to Bearer for legacy clients.
- [x] **4.2** Add CSRF middleware + token in admin form helpers — double-submit `csrf_token` cookie + `X-CSRF-Token` header. `app/middleware/csrf.py`. Admin `api.js` echoes the token automatically on PUT/POST/PATCH/DELETE.
- [x] **4.3** Add Status dropdown (Draft / Published) to category, subcategory, brand, product forms.
- [x] **4.4** Add status filter to all admin list pages.
- [x] **4.5** Integrate Quill 2.0 for product full description (`assets/js/editor.js`, `RichEditor.mount/setValue`).
- [x] **4.6** Build multi-image gallery widget (`assets/js/gallery.js`) — HTML5 drag/drop reorder, per-tile delete, click-to-upload (multi-file).
- [x] **4.7** Build specifications key/value builder widget (`assets/js/specs.js`).
- [x] **4.8** Add datasheet URL field to product form.
- [x] **4.9** Add meta_title / meta_description fields to category, subcategory, product forms.
- [x] **4.10** Add brand description / website_url / country fields to brand form.
- [x] **4.11** Add "Preview" link on each edit modal → opens public URL in new tab.
- [x] **4.12** Implement audit log writes in service layer — `services/audit.py` with `AuditService.log()` + `snapshot()` diff helper. Wired into create/update/delete on the four content services and bulk product action.
- [x] **4.13** Build `/admin/audit.html` viewer (super_admin only) — filters by entity_type/action, paginated, change diffs rendered inline. Backed by `GET /api/audit/`.
- [x] **4.14** Add real pagination + search to products list — `GET /api/products/?skip=&limit=&search=&status=` returns `{items, total, skip, limit}`. Admin products page exposes search box + Prev/Next.
- [x] **4.15** Add bulk actions (publish/unpublish/delete) on products list — `POST /api/products/bulk` + select-all checkbox + bulk action bar.
- [x] **4.16** Build "Validate Catalog" dashboard widget — `GET /api/products/validation` reports counts of published rows missing image/meta/specs/description/brand and lists 10 examples.
- [x] **Verification** — uvicorn boots, CSRF blocks unauthenticated POSTs (403) and accepts authenticated ones (200), cookie session round-trips through login/me/logout, audit log captures create+publish+delete (3 entries from one cycle), product list paginated (14,801 total), search 'plc' returns 176 hits, bulk publish/unpublish runs cleanly, validation widget serves. All 7 admin pages (login, dashboard, categories, subcategories, products, brands, audit, users, import) and all public SSR pages return 200.

## Phase 5 — Security & SEO  ✅ COMPLETE (2026-04-23) — except 5.1/5.4/5.12 which need user/deploy action

- [ ] **5.1** Rotate `SECRET_KEY` to a 64-char random string (in `.env`, not committed) — **user action**, code already enforces non-placeholder via `config.py` validator
- [x] **5.2** Tighten CORS in `main.py` from `"*"` to env-configured allowed origins — wildcard fallback removed; app raises on startup if `ALLOWED_ORIGINS` is empty
- [x] **5.3** Add slowapi rate-limit on `/api/auth/login` (5 attempts / 15 min / IP) — `app/rate_limit.py`, `LOGIN_RATE_LIMIT` env var, verified 6th attempt returns 429
- [x] **5.4** Force HTTPS redirect — `deploy/nginx.conf.example` server block returns `301 https://$host$request_uri` for port 80
- [x] **5.5** Add security headers middleware — `app/middleware/security.py`: nosniff, X-Frame-Options, Referrer-Policy, Permissions-Policy, CSP, optional HSTS (`ENABLE_HSTS` env)
- [x] **5.6** Build `app/services/seo.py` — `organization()`, `breadcrumb()`, `product()`, `to_script()` builders. Registered as `jsonld` Jinja2 filter on `templates.env.filters`
- [x] **5.7** Add `Product` JSON-LD to `product_detail.html` via `jsonld_blocks` ctx
- [x] **5.8** Add `BreadcrumbList` JSON-LD to category, subcategory, brand, product detail pages
- [x] **5.9** `/sitemap.xml` route cached 1 hour — already shipped in Phase 2
- [x] **5.10** `/robots.txt` — already shipped in Phase 2
- [x] **5.11** Open Graph + Twitter Card meta tags in `_head.html` — added twitter:title/description, robots, theme-color
- [ ] **5.12** Verify Lighthouse scores (target: Performance ≥ 85, SEO ≥ 95, Accessibility ≥ 90) — **user action**, requires browser
- [x] **Verification** — uvicorn boots, security headers present on every response, login rate-limited (attempts 1-5 = 401, attempt 6 = 429), Organization JSON-LD on home, Product + BreadcrumbList on `/product/{slug}`, BreadcrumbList on `/category/{slug}` and `/category/{cat}/{sub}` and `/brand/{slug}`

## Phase 6 — Catalogue data entry

- [ ] **6.1** Train data-entry user on new admin (walk through DATA_ENTRY_GUIDE.md)
- [x] **6.2** Wipe seed data: keep super_admin user only, drop sample categories — done 2026-04-23 by `scripts/seed_demo_data.py`. Old DB backed up as `backend/shining_horizon.db.pre_seed_backup`
- [~] **6.3** Enter all brands from official catalogue — 25 demo brands seeded. Replace with real brand list when supplied
- [~] **6.4** Enter all categories — 11 categories seeded (Industrial Automation, Electrical, Lifting, Pneumatic, Plumbing, Lighting, Safety, Cleaning, HVAC, Maintenance, Tools)
- [~] **6.5** Enter all subcategories — 12 demo subcategories seeded under detailed categories (PLC/VFD/HMI, Breakers/Cables, Chain Hoists/Wire Rope/Shackles, Cylinders/Valves, PPE/Fire Safety)
- [~] **6.6** Enter products — 14 demo products seeded across all categories with images, specs, brands. Real catalogue entry pending
- [ ] **6.7** Run "Validate Catalog" — fix any flagged items
- [ ] **6.8** Switch all entries from Draft → Published — demo data is already PUBLISHED for testing

> **Note**: Demo seed (`scripts/seed_demo_data.py`) is idempotent — re-running it wipes catalog tables and reseeds. Use it any time you need a clean test state. Real catalogue entry will replace the demo via the admin UI; no need to wipe again.

## Phase 7 — Final QA & launch

- [ ] **7.1** Cross-browser test (Chrome, Safari, Firefox, Edge) — **user action**
- [ ] **7.2** Mobile device test (iOS Safari, Android Chrome) — **user action**
- [ ] **7.3** Lighthouse audit on home + 1 category + 1 product page — **user action**
- [ ] **7.4** Submit `/sitemap.xml` to Google Search Console — **user action** (after DNS cutover)
- [x] **7.5** Pre-launch SQLite backup — `backend/scripts/backup_db.py` (uses SQLite online backup API; safe while serving). Verified 2026-04-23
- [x] **7.6** Deploy to production server — `deploy/shining-horizon.service` (systemd unit) + `deploy/nginx.conf.example` (HTTPS reverse proxy with Let's Encrypt + HSTS) ready. Actual server provisioning is **user action**
- [ ] **7.7** Run `alembic upgrade head` on production — **user action** during deploy
- [x] **7.8** DNS / Nginx switch — Nginx config drafted in `deploy/nginx.conf.example` (covers Phase 5.4 HTTPS redirect). DNS cutover is **user action**
- [ ] **7.9** Smoke test production — **user action** post-deploy
- [ ] **7.10** Send launch confirmation to management — **user action**

---

## Phase 8 — Role-based access control (added 2026-04-23)

- [x] **8.1** Extend `UserRole` enum with `MANAGER` + `DATA_ENTRY` (in addition to existing `SUPER_ADMIN` + `ADMIN`)
- [x] **8.2** Build `app/services/permissions.py` — `can_publish/can_delete/can_manage_users/can_view_audit/can_bulk_action` boolean helpers + FastAPI `Depends` wrappers (`require_publish`, `require_delete`, `require_manage_users`, `require_view_audit`) + `enforce_status_change(user, requested)` for create/update flows
- [x] **8.3** Wire `enforce_status_change` into create/update on categories, subcategories, brands, products
- [x] **8.4** Wire `require_delete` onto every DELETE endpoint
- [x] **8.5** Wire `can_bulk_action` into `POST /api/products/bulk` (publish/unpublish gated to manager+; delete gated to admin+)
- [x] **8.6** Open `/api/audit/` from super_admin-only to admin+ via `require_view_audit`
- [x] **8.7** Last-super-admin guard in `/api/users/` PUT and DELETE — cannot demote, deactivate or delete the only active super_admin
- [x] **8.8** Admin frontend: role labels (Super Admin / Admin / Manager / Data Entry), `data-permission` attributes on nav links and Delete buttons, `applyRoleGates()` in `auth.js` hides forbidden controls + locks Status select to "draft" for non-publishers
- [x] **8.9** Users edit form now exposes all 4 roles with descriptive labels
- [x] **Verification** — end-to-end role smoke for all 4 roles. data_entry: draft create 200, published create 403, delete 403, bulk publish 403, users 403, audit 403. manager: published create 200, delete 403, bulk publish 200, bulk delete 403, users 403, audit 403. admin: bulk delete 200, audit 200, users 403. super_admin: users 200, last-super-admin guard returns 400 on self-demote/deactivate.

### Test users seeded (change passwords before production)

| Username | Password | Role |
|---|---|---|
| `admin` | `TestAdmin#2026` | super_admin |
| `test_admin` | `TestPass#123` | admin |
| `test_manager` | `TestPass#123` | manager |
| `test_data_entry` | `TestPass#123` | data_entry |

## Notes for the agent working this file

- Always work top-to-bottom within a phase. Phase boundaries are real dependencies — do not start Phase 2 until Phase 1 is complete.
- Update task status (`[ ]` → `[~]` → `[x]`) **as soon as** state changes, not in batches.
- If a task is blocked, mark `[!]` and add a one-line note on the next line.
- After each task, verify with the smallest possible check (run the migration, hit the URL, etc.) — do not "look correct" your way through.
- Never delete a file without grep-confirming nothing references it.
- Commit after each meaningful chunk (typically 3–5 related tasks). Use conventional commit style: `feat:`, `fix:`, `refactor:`, `chore:`.
