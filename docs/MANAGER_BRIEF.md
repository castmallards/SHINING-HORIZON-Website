# Catalog System Upgrade — Brief for Management

**Project**: Shining Horizon Trading website
**Prepared for**: Management
**Date**: 22 April 2026
**Author**: Moeez

---

## Executive summary

We are upgrading the website's catalog system. The **public design stays exactly the same** — the same homepage, the same category and product cards, the same colours and animations. What changes is **how the website is built behind the scenes**.

The current system requires a manual "Generate Pages" step every time we update content. It also creates dozens of static files that pollute the project and become outdated silently. The upgraded system removes that step entirely: when we update content in the admin, the website reflects it immediately.

We are also taking this opportunity to add features the current system lacks: full per-product pages, draft/publish workflow, image galleries, specification tables, search-engine optimisation, and a security hardening pass.

The data we have today will be re-entered manually directly from the official company product catalogue, so the live website matches the brand's authoritative source.

---

## Why we are changing

The current system has eight specific problems we encounter regularly:

1. **Content goes stale silently.** Editing a product in the admin does not update the website. Someone must remember to click "Generate Pages." If they forget, customers see old data.
2. **No real product pages.** Today, "product pages" are actually subcategory listings. Each individual product has no dedicated page, no full specs, no gallery. Customers cannot deep-link to a specific item.
3. **All-or-nothing updates.** Editing one product regenerates dozens of HTML files. Slow, wasteful, and creates large diffs that complicate version control.
4. **No draft mode.** Every change is immediately public the moment we click Generate. There is no way to prepare content privately and review before launch.
5. **Weak search-engine visibility.** Pages have minimal SEO metadata, no Open Graph tags for social sharing, no structured product data for Google rich results, no sitemap. We are leaving search traffic on the table.
6. **Security gaps.** The application secret key is the placeholder default, the API accepts requests from any domain, and admin sessions are stored in browser local storage where they are vulnerable to script attacks.
7. **No audit trail.** We cannot tell who changed what, when. As the team grows this becomes a real problem.
8. **No proper image handling.** A single uploaded image is used for both product cards and full-size views, wasting bandwidth on mobile.

---

## What we are doing about it

### Same look, better engine
The visual design — homepage hero, category cards, product cards, colour scheme, animations — does not change. Customers will not see a different site. The change is in the rendering engine: the website will read the database live instead of relying on pre-generated files.

### New per-product detail pages
Every product gets its own page with a full image gallery, complete specifications table, datasheet link, brand information, related products, and a pre-filled "Request Quote" button. This gives our products a proper presence in search engines and lets customers deep-link to any item.

### Draft / Published workflow
Content can be prepared in Draft mode, previewed privately, then Published with one click. Edits to live content can be staged and reviewed before going public.

### Search-engine optimisation
Each page will have proper meta tags, Open Graph data for social sharing, structured product data so Google can show rich results (price, brand, availability), an auto-generated sitemap, and lazy-loaded images. This positions us to rank for searches like "Siemens VFD Saudi Arabia."

### Security hardening
We will rotate the application secret, restrict the API to our own domain, move admin sessions to secure cookies, add login rate-limiting, and enforce HTTPS. This brings the system in line with standard security practice.

### Audit logging
Every create, update, delete will be recorded with the user and timestamp. Useful for compliance and for debugging "who changed this?" questions.

### Better image pipeline
On upload, the system will automatically generate three sizes (thumbnail, card, hero) in modern WebP format. Faster page loads, lower bandwidth bill, better mobile experience.

---

## Why now

Three reasons converging:

1. **We are about to re-enter the entire catalogue manually from the official source.** The data-entry effort is the same whether we do it on the old system or the new one — but doing it on the new system means we capture richer data (specifications, gallery, meta descriptions) on the first pass, instead of doing it twice.
2. **The longer we wait, the more entrenched the current pattern becomes.** Right now we have ~33 generated files. After two more years of additions we'll have hundreds.
3. **Search engine traffic is a competitive advantage we are currently giving away.** Every week without proper SEO is missed enquiries.

---

## What it costs

### Time
- **Engineering**: approximately 6–7 working days for the system upgrade itself, before data entry begins.
- **Data entry**: dependent on catalogue size. Estimated 2–4 minutes per product on the new system. For 500 products, this is about 25–35 hours of focused entry, ideally spread across one or two team members over 1–2 weeks.

### Money
- Zero new software licences. Same FastAPI / Python stack, same SQLite database, same hosting server.
- One-time engineering cost only.

### Risk
- The public website remains operational throughout. The new system will be developed in parallel and switched over in a single deployment window once tested.
- Data is preserved: nothing in the existing database is lost. The schema is extended, not replaced.
- Rollback plan: if a critical issue is found post-deployment, we can switch DNS back to the old static files in under 10 minutes.

---

## What we are not doing

To keep scope clear, the following are out of scope for this upgrade:

- Visual redesign — site looks identical to today.
- E-commerce / online checkout — this remains a quote-request site.
- Customer accounts / login — public site is browse-only.
- Migrating to a new hosting provider or rewriting in a different framework.

These can be revisited in future phases if the business needs them.

---

## Timeline

| Phase | Duration | What happens |
|---|---|---|
| 1. Schema and infrastructure | 1 day | Add new database fields, set up migrations, environment configuration |
| 2. Replace generation with live rendering | 2 days | Build the new public routes, retire the static-file generator |
| 3. Per-product pages and image pipeline | 1 day | Add full product detail page; auto-generate image variants on upload |
| 4. Admin upgrades | 2 days | Draft/Publish, rich-text editor, gallery upload, specifications builder, audit log |
| 5. Security and SEO | 1 day | Secrets, CORS, cookies, rate-limiting, sitemap, structured data |
| 6. Catalogue re-entry | 1–2 weeks | Team enters official catalogue data using the new admin |
| 7. Final QA and launch | 1 day | Cross-browser, mobile, SEO checks, then DNS switch |

**Total to live launch**: approximately 3–4 weeks from start.

---

## Decision needed

Approval to proceed with the engineering upgrade (phases 1–5) so the new admin is ready when manual data entry begins.

If approved, no further sign-off is needed until phase 7 launch.
