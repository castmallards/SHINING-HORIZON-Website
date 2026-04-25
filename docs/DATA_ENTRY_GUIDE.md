# Data Entry Guide — Shining Horizon Catalog (v2)

> Purpose: Step-by-step instructions for entering product catalog data into the upgraded admin dashboard. Read this before opening the company catalog.

---

## 1. Before you start

### 1.1 What changed
- No more "Generate Pages" button. Whatever you save in admin is **live on the website immediately** (after you set status to **Published**).
- Every product, category, brand has a **Draft / Published** status. Use Draft while you're working, switch to Published when ready.
- Each product now has its own detail page (e.g. `/product/siemens-6es7214-1ag40-0xb0`) with a full spec table, image gallery, and datasheet.

### 1.2 What you need open
1. The company product catalog (PDF or printed).
2. A folder of product images, brand logos, datasheets — pre-sorted.
3. The admin dashboard: `https://<your-domain>/admin/login.html`.

### 1.3 Login
- Username: `admin`
- Password: (provided separately — change on first login)

---

## 2. Order of entry — DO NOT SKIP

Always enter data in this order. Later steps depend on earlier ones.

```
  1. Brands
  2. Categories
  3. Subcategories  (only for "Detailed" categories)
  4. Products
```

If you try to add a product before its category exists, the form won't let you save.

---

## 3. Step 1 — Brands

For every manufacturer in the catalog (Siemens, ABB, Schneider, Festo, SMC, etc.):

1. Go to **Brands → Add Brand**.
2. Fill in:
   - **Name** — exact spelling as on the brand's logo (e.g. `Schneider Electric`, not `schneider`).
   - **Logo** — square or horizontal PNG/SVG, transparent background, max 5MB.
   - **Description** — 1–2 sentence company description (optional but improves SEO).
   - **Website URL** — official manufacturer site (optional).
   - **Country** — country of origin (optional).
   - **Display Order** — controls position on the brands page (10, 20, 30…). Use gaps so you can insert new brands later without renumbering.
   - **Status** — `Published` once the logo is uploaded.
3. Save.

> Tip: Add all brands first in one sitting. You'll select them later when adding products.

---

## 4. Step 2 — Categories

A category is a top-level grouping (e.g. **Industrial Automation**, **Electrical Products**, **Tools**).

### 4.1 Pick a category type
- **Detailed** — has subcategories underneath. Use this when the catalog has 2 levels (Industrial Automation → PLC Controllers → individual products).
- **Simple** — products sit directly under the category, no subcategories. Use this when there's only 1 level (Tools → individual products).

> If unsure, use **Detailed**. It's easier to convert Detailed → Simple later than the reverse.

### 4.2 Fields
1. **Name** — what appears in the menu (e.g. `Industrial Automation`).
2. **Type** — Detailed or Simple (see above).
3. **Description** — 2–3 sentences, plain language. Shown on the category card.
4. **Hero Title** — short headline for the category page banner (e.g. `Industrial Automation Solutions`).
5. **Hero Description** — 1 sentence under the headline.
6. **Image** — landscape banner image (recommended 1600×600), max 5MB.
7. **Meta Title** — for Google search results. Format: `{Category Name} — Shining Horizon Trading`.
8. **Meta Description** — 150–160 characters, used as the Google snippet.
9. **Display Order** — 10, 20, 30…
10. **Show on Home** — tick if this category should appear on the homepage.
11. **Status** — Draft until images and copy are final, then Published.

### 4.3 Recommended categories (from current site)
| Order | Category | Type |
|------:|---|---|
| 10 | Industrial Automation | Detailed |
| 20 | Electrical Products | Detailed |
| 30 | Pneumatic Products | Detailed |
| 40 | HVAC & Spare Parts | Detailed |
| 50 | Plumbing Products | Detailed |
| 60 | Lighting Products | Detailed |
| 70 | Safety Products | Detailed |
| 80 | Cleaning Products | Detailed |
| 90 | Lifting Equipment | Simple |
| 100 | Tools | Simple |
| 110 | Maintenance Services | Simple |

---

## 5. Step 3 — Subcategories *(only for Detailed categories)*

For each Detailed category, add its subcategories before adding products.

Example for **Industrial Automation**:
- PLC Controllers
- VFDs (Variable Frequency Drives)
- HMI Panels
- Servo Motors
- Soft Starters
- I/O Modules
- Safety Relays

### Fields
1. **Parent Category** — pick from dropdown.
2. **Name** — singular or plural, stay consistent (`PLC Controllers`, not `PLC Controller`).
3. **Description** — 1–2 sentences.
4. **Image** — square preferred (recommended 800×800).
5. **Display Order** — 10, 20, 30…
6. **Status** — Published.

---

## 6. Step 4 — Products *(the bulk of the work)*

For every product line in the catalog, fill in the form completely. **Quality matters more than speed.**

### 6.1 Required fields
| Field | Notes |
|---|---|
| **Category** | Pick first; this enables Subcategory dropdown if Detailed. |
| **Subcategory** | Required for Detailed categories only. |
| **Brand** | Pick from your previously entered brands. |
| **Product Name** | Customer-facing name. Example: `SIMATIC S7-1200 PLC Controller`. |
| **Part Number** | Exact manufacturer code from the catalog (e.g. `6ES7214-1AG40-0XB0`). Used in the URL. |
| **Short Description** | One sentence (max 160 chars), shown on cards. |
| **Full Description** | 2–4 paragraphs, rich text. Cover what it does, where it's used, key benefits. |
| **Specifications** | Key/value pairs — see 6.3 below. |
| **Main Image** | Square, white background preferred, 800×800 minimum, max 5MB. |
| **Gallery Images** | Up to 5 additional images (different angles, in-use shots). |
| **Datasheet URL** | Link to the manufacturer PDF (paste the URL — don't upload). |
| **Display Order** | 10, 20, 30… within the subcategory. |
| **Featured** | Tick for products you want to highlight on home page. |
| **Status** | Draft while you're working, Published when complete. |
| **Meta Title** | `{Brand} {Part Number} — {Category} \| Shining Horizon`. |
| **Meta Description** | 150–160 chars summary, used by Google. |

### 6.2 Naming and slug rules
- Slug is generated automatically from `{brand}-{part-number}`. You don't enter it.
- If the part number has slashes or special characters, replace with hyphens.
- Two products **cannot** have the same slug. The system will append `-1`, `-2` automatically — but check for typos in the part number first.

### 6.3 Specifications
This is the spec table on the product page. Add one row per spec:

| Key | Value |
|---|---|
| Voltage | 24 V DC |
| Output Channels | 14 |
| Communication | Profinet |
| Mounting | DIN Rail |
| Operating Temperature | -20 to +60 °C |
| Certifications | CE, UL, RoHS |

Use the same key wording across products in the same subcategory so customers can compare.

### 6.4 Image rules
- **Format**: WebP or JPG preferred (PNG only if transparency needed).
- **Size**: 800×800 minimum, ideally 1200×1200 for the main image.
- **Background**: white or transparent for product shots.
- **File size**: under 2MB per image.
- **Naming on disk** (before upload): `brand-partnumber-1.jpg`, `brand-partnumber-2.jpg`. Helps you find them later.

---

## 7. Workflow tips

### 7.1 Use Draft mode aggressively
Save as **Draft** when:
- You're missing the image or datasheet.
- You're not sure of the spec values.
- The translation/description isn't final.

You can preview drafts inside the admin before publishing.

### 7.2 Batch by subcategory
Don't jump around. Finish all PLC Controllers, then all VFDs, then all HMIs. Batching keeps your spec keys consistent.

### 7.3 Use the Live Preview button
Every product/category edit page has a **Preview** button. It opens the live URL in a new tab so you can check formatting before publishing.

### 7.4 Daily save discipline
At the end of each session, switch the **Status** dropdown filter to "Draft" and check what's still incomplete. Aim to leave the catalog in a publishable state at end of day.

---

## 8. Troubleshooting

| Symptom | Fix |
|---|---|
| "Cannot save: category required" | You must pick a category before saving. |
| Image upload fails | Check it's under 5MB and is JPG/PNG/WebP/SVG. |
| Same slug error | Two products have the same `{brand}-{part-number}`. Check for typos. |
| Page looks empty after publish | Hard refresh the public page (Ctrl+F5). New cache TTL is 60 seconds. |
| Form fields disappear | Subcategory only shows when the category is Detailed. |

---

## 9. After data entry — final checklist

Before you tell management the catalog is live:
- [ ] Every brand has a logo and is Published.
- [ ] Every category has a hero image, meta title, meta description.
- [ ] Every Detailed category has at least one subcategory.
- [ ] Every product has main image, full description, at least 3 specifications.
- [ ] No products are stuck in Draft accidentally (filter by Status).
- [ ] Sample 5 product detail pages on mobile — make sure they look right.
- [ ] Run the **Validate Catalog** button (Dashboard → top right) — it lists missing data.
