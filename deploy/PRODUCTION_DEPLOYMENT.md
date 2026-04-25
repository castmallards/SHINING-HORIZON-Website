# Shining Horizon — Production Deployment Guide

**Audience:** the person actually putting this site on a server. Plain English, ordered checklist, copy-pasteable commands.

This guide takes you from a fresh Ubuntu 22.04 VPS (DigitalOcean / Hetzner / Linode / AWS EC2 — anything with `apt`) to a production website serving HTTPS in roughly **45 minutes**.

---

## What you're building

```
   Visitor's browser
        │
        ▼
   Cloudflare (CDN, edge cache, free TLS)         ← Step 7 (optional but recommended)
        │
        ▼
   Nginx (your server, port 443)                   ← Steps 4–5
        │   - terminates HTTPS
        │   - caches /uploads/ and /static/ for 7–30 days
        │   - gzips responses
        │   - forwards everything else to ↓
        ▼
   Uvicorn (your server, port 8000, 2+ workers)    ← Step 3
        │   - runs FastAPI
        │   - serves SSR templates + JSON API
        │   - writes to ↓
        ▼
   SQLite (or PostgreSQL when you outgrow it)
```

Nothing exotic. Each layer can be swapped without rewriting the others.

---

## Step 0 — Before you start (5 min)

You need:

- A domain name pointed at your server's IP via an **A record** (e.g. `shininghorizon.com → 1.2.3.4`). Add `www` too.
- A fresh Ubuntu 22.04 (or 24.04) VPS with **at least 1 GB RAM, 1 vCPU, 25 GB disk**. The site will happily run on this.
- SSH access as a sudo user (don't use root for the application).

Quick DNS check from your laptop before continuing:

```bash
dig +short shininghorizon.com
# should print your server's IP. If empty, fix DNS first.
```

---

## Step 1 — System packages (5 min)

SSH into the server, then:

```bash
sudo apt update && sudo apt -y upgrade
sudo apt -y install python3 python3-venv python3-pip git nginx certbot python3-certbot-nginx ufw

# basic firewall: allow SSH + web only
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
```

That's it for the OS layer.

---

## Step 2 — Pull the code & install Python deps (5 min)

We'll put everything under `/opt/shining-horizon` and run the app as the `www-data` user (which Nginx already uses).

```bash
sudo mkdir -p /opt/shining-horizon
sudo chown $USER:$USER /opt/shining-horizon
cd /opt/shining-horizon

# Either git clone, or scp/rsync your project here.
# git clone https://github.com/<your-org>/shining-horizon.git .

# Create an isolated virtualenv (don't use system Python).
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

# Hand the directory to www-data so the systemd service can read it.
sudo chown -R www-data:www-data /opt/shining-horizon
```

---

## Step 3 — Configure secrets & boot the app (10 min)

### 3.1 Create the production `.env`

```bash
cd /opt/shining-horizon/backend
cp .env.example .env
```

Now generate a real `SECRET_KEY` and edit `.env`:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
# Copy the output; it'll look like:  Pk-X4...long random...j3
```

Open `/opt/shining-horizon/backend/.env` with `nano` and **change at least these four**:

```ini
SECRET_KEY=<paste the long random string from above>
COOKIE_SECURE=true
COOKIE_DOMAIN=shininghorizon.com
ALLOWED_ORIGINS=https://shininghorizon.com,https://www.shininghorizon.com
ENABLE_HSTS=true
```

Lock the permissions so only the app user can read it:

```bash
sudo chown www-data:www-data /opt/shining-horizon/backend/.env
sudo chmod 600 /opt/shining-horizon/backend/.env
```

### 3.2 Run database migrations

```bash
cd /opt/shining-horizon/backend
sudo -u www-data /opt/shining-horizon/.venv/bin/alembic upgrade head
```

### 3.3 Install + start the systemd service

The unit file is already in `deploy/shining-horizon.service`. Install it:

```bash
sudo cp /opt/shining-horizon/deploy/shining-horizon.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now shining-horizon
sudo systemctl status shining-horizon       # should say "active (running)"
```

Quick local check (still on the server, before Nginx):

```bash
curl -I http://127.0.0.1:8000/health
# → HTTP/1.1 200 OK
```

If you get a 200, the app is up. Move on.

---

## Step 4 — Nginx (HTTPS reverse proxy with caching + gzip) (10 min)

The production Nginx config is already in `deploy/nginx.conf.example`. Install it:

```bash
sudo cp /opt/shining-horizon/deploy/nginx.conf.example /etc/nginx/sites-available/shining-horizon
sudo ln -sf /etc/nginx/sites-available/shining-horizon /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
```

**Edit the new file** to replace `shininghorizon.com` with your real domain everywhere.

Get a real TLS certificate (free, auto-renewing) from Let's Encrypt:

```bash
sudo certbot --nginx -d shininghorizon.com -d www.shininghorizon.com
# accept the email prompt, choose "redirect HTTP→HTTPS" when asked
```

Test the config and reload:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Visit `https://shininghorizon.com/` from your laptop. You should see the live site over HTTPS.

### What the Nginx config gives you (for free)

| Feature | Where it's set | What it buys |
|---|---|---|
| HTTPS termination | `listen 443 ssl http2` | Modern TLS 1.2/1.3, HTTP/2 multiplexing |
| Plain HTTP redirect | `return 301 https://$host$request_uri` | Browsers never speak HTTP again after first hit |
| `gzip on` for HTML/CSS/JS | (add to `nginx.conf` if not present, see below) | ~70% smaller text payloads |
| Long cache on `/uploads/` | `expires 30d` | Visitors download a product image once, ever |
| 7-day cache on `/static/` | `expires 7d` | Logos / brand images don't refetch every page |
| `X-Forwarded-For` to uvicorn | `proxy_set_header` | slowapi can rate-limit by real client IP, not by Nginx |

### Make sure gzip is enabled in the main Nginx config

Open `/etc/nginx/nginx.conf` and confirm the `http` block has these. Most distributions ship them by default but it's worth checking:

```nginx
http {
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain text/css application/javascript application/json
        application/xml text/xml image/svg+xml application/vnd.ms-fontobject
        application/x-font-ttf font/opentype;
}
```

Reload after any change: `sudo systemctl reload nginx`.

---

## Step 5 — App-level gzip (already wired) ✓

Even before Nginx, the FastAPI app gzips its own responses via `GZipMiddleware` (see `backend/app/main.py`). This is belt-and-braces — Nginx will compress everything that reaches it, and the app compresses what Nginx forwards in proxy mode. No extra configuration needed.

To verify it works after deploy:

```bash
curl -sI -H "Accept-Encoding: gzip" https://shininghorizon.com/ | grep -i content-encoding
# → content-encoding: gzip
```

---

## Step 6 — Verify the deploy (5 min)

From your laptop:

```bash
# Home page works and returns the right security headers
curl -sI https://shininghorizon.com/ | head -20

# Sitemap is valid XML
curl -s https://shininghorizon.com/sitemap.xml | head -3

# robots.txt allows crawling
curl -s https://shininghorizon.com/robots.txt

# Admin login is reachable
curl -sI https://shininghorizon.com/admin/login.html
```

Visit `https://shininghorizon.com/admin/login.html` in a browser. **Change the default `admin` password immediately** via the Users admin page.

---

## Step 7 — Cloudflare CDN (optional, 10 min, free tier is enough)

This is the single biggest win for visitors outside your server's region. Cloudflare caches HTML and assets at ~300 edge locations worldwide, so a visitor in Riyadh hitting your London server still gets sub-100 ms TTFB.

1. **Sign up at cloudflare.com**, add your domain. Free tier is fine.
2. Cloudflare gives you 2 nameservers (e.g. `lia.ns.cloudflare.com`). **Update them at your domain registrar** (GoDaddy / Namecheap / Route53). Wait 10–30 min for propagation.
3. In the Cloudflare dashboard:
   - **SSL/TLS** → mode **Full (strict)**. Forces real HTTPS to your origin.
   - **Speed → Optimization** → enable **Auto Minify** (HTML / CSS / JS) and **Brotli**.
   - **Speed → Optimization → Image Optimization** → enable **Polish** (lossy) and **WebP**. Free tier auto-converts your JPG/PNG.
   - **Caching → Configuration** → Browser Cache TTL: **4 hours**.
   - **Rules → Page Rules** (free plan: 3 rules) — recommended:
     - `*shininghorizon.com/admin/*` → **Cache Level: Bypass** (admin must always hit origin)
     - `*shininghorizon.com/api/*` → **Cache Level: Bypass**
     - `*shininghorizon.com/uploads/*` → **Cache Level: Cache Everything**, Edge Cache TTL: **1 month**
4. To make Cloudflare cache product/category HTML edge-side too, add response headers from FastAPI on public SSR routes (already wired in `backend/app/middleware/security.py` — extend if you want longer edge caching). For now: SSR pages will hit your origin every time, which is fine because the in-memory cache makes them ~5 ms each.

After Cloudflare propagates, every IP that resolves your domain is a Cloudflare edge IP — your origin IP is hidden, which also blocks direct attacks.

---

## What you have now

✅ HTTPS on a custom domain with auto-renewing certs
✅ HTTP/2 over TLS 1.3
✅ Gzip both at the app and at the edge
✅ Long-lived caching on uploaded images and static assets
✅ Cloudflare CDN serving from ~300 PoPs worldwide (if Step 7)
✅ Per-IP rate limiting on /api/auth/login
✅ Audit log of every admin action
✅ Role-based access (super_admin / admin / manager / data_entry)
✅ Branded 404, JSON-LD schema on every page, OG/Twitter share previews

---

## Day-2 operations

### Daily backups (cron)

```bash
sudo crontab -e
# Add this line — runs the SQLite online backup every day at 03:00:
0 3 * * * cd /opt/shining-horizon/backend && /opt/shining-horizon/.venv/bin/python -m scripts.backup_db --label nightly
```

To copy backups offsite (recommended), append `&& rsync ...` or use `restic`.

### Logs

```bash
sudo journalctl -u shining-horizon -f          # tail app logs
sudo tail -f /var/log/nginx/access.log         # nginx access
sudo tail -f /var/log/nginx/error.log          # nginx errors
```

### Updating the code

```bash
cd /opt/shining-horizon
sudo -u www-data git pull
source .venv/bin/activate
pip install -r backend/requirements.txt
sudo -u www-data /opt/shining-horizon/.venv/bin/alembic upgrade head
sudo systemctl restart shining-horizon
```

### Renew the TLS cert

Already automatic via certbot's systemd timer. Verify:

```bash
sudo systemctl list-timers | grep certbot
```

---

## When to scale up (you're not there yet)

| Symptom | Move to |
|---|---|
| `/api/products/` slow on lists > 200 items | Add the composite index in [docs/TASKS.md §8](../docs/TASKS.md) |
| Admin reports > 200 ms response time consistently | Bump uvicorn workers from 2 to 4 in `deploy/shining-horizon.service` |
| Multiple machines serving the same site | Replace `app/cache.py` TTLCache with a Redis-backed implementation (interface is identical) |
| > 50,000 products, SQLite locks on writes | Migrate to PostgreSQL: change `DATABASE_URL` and rerun `alembic upgrade head` |
| Slowapi rate limit needs to survive restarts / span workers | Configure slowapi's `storage_uri="redis://..."` |

Each of those is a 30-minute change made deliberately, after measuring — not pre-emptively.

---

## Troubleshooting cheatsheet

| Symptom | Likely cause | Fix |
|---|---|---|
| `502 Bad Gateway` from Nginx | Uvicorn not running | `sudo systemctl status shining-horizon` and check `journalctl -u shining-horizon -n 50` |
| `403 CSRF token missing` on admin actions | Cookie blocked or domain mismatch | Verify `COOKIE_DOMAIN` matches the actual host you're loading the admin from |
| Admin login redirects forever | Old `localStorage.admin_token` from v1 | Open browser DevTools → Application → Local Storage → Clear |
| `RuntimeError: ALLOWED_ORIGINS is empty` on boot | `.env` not loaded or value blank | Check the file path and that `EnvironmentFile=` in the systemd unit points to the right `.env` |
| HSTS broke the site after a cert problem | Browsers cached the HSTS header | Wait until `HSTS_MAX_AGE` expires, or in Chrome: `chrome://net-internals/#hsts` → delete the entry |

---

## Files you'll touch on the server

```
/opt/shining-horizon/
├── backend/.env                            # secrets, never in git
├── backend/shining_horizon.db              # the SQLite database
├── backend/uploads/                        # admin-uploaded images
├── deploy/nginx.conf.example               # → /etc/nginx/sites-available/shining-horizon
└── deploy/shining-horizon.service          # → /etc/systemd/system/
```

That's everything. The site should now be live, fast, and secure.
