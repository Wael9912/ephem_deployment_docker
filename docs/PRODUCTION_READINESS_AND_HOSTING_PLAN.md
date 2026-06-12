# Med-Supply ERP — Production Readiness Review & Hosting Plan

*Review date: 2026-06-11. Scope: Docker/NGINX/Odoo configs, seed scripts, custom addons (incl. Spiffy theme), backup/SSL scripts, UI screenshots. Target: hosting database `erpmedsupply` on a real server (nothing provisioned yet).*

## TL;DR

**The solution itself (Odoo 18 + module mix + seed pipeline) is solid and the UI is good — but the repo is not production-ready as-is.** There are 5 blockers, all fixable in a few hours. The foundation is already strong (NGINX with TLS/rate-limiting/websocket routing, backup + restore scripts, `docs/PRODUCTION_HARDENING_RUNBOOK.md`). Fix the blockers, then follow the hosting steps — realistically live within a week of getting a server.

## UI/UX — good, ship it

Reviewed captured screens (app launcher, Inventory overview, Accounting dashboard, forms). The Spiffy theme gives a clean, modern look: dark navbar, white card-based dashboards, a focused 9-app launcher with no clutter from unrelated modules. The Accounting dashboard correctly shows SDG amounts with the س.ج symbol, aged invoices, and the Bank of Khartoum balance. Arabic RTL is fully set up (`ar_001` + Alexandria font). For an Excel-to-ERP audience this is appropriately simple. No UX blockers — the caveats are in the theme's *code* (below), not its look.

## Production blockers (must fix before deploying)

1. **Mac-only paths in `docker-compose.yml:38-39`** — `/Users/waelabdalla/Documents/Projects/cmp/...` volume mounts will fail on any Linux server. *Update: fixed 2026-06-13 — all host-specific dev mounts moved to `docker-compose.override.yml` (dev-only, gitignored); the base compose file is now portable.*

2. **`dbfilter` mismatch** — `odoo.conf.prod` and `.env.example` pinned `^ephem_uganda$`, which would have made the `erpmedsupply` database unreachable. *Update: fixed 2026-06-13 — both now pin `^erpmedsupply$`, and the backup/restore scripts' default `DB_NAME` was aligned to `erpmedsupply` as well.*

3. **Old secret in git history** — the old `admin_passwd`/`db_password` (written here as `<OLD-PASSWORD-REDACTED>`) appeared in ~10 commits. Purge with `git filter-repo` (runbook §2 documents this) **before** pushing the repo to any server or remote. *Update: purge completed 2026-06-13 — see runbook §2.*

4. **~120 unrelated addons = real attack surface.** All ePHEM/EOC/CMP/OpenEducat modules are mounted alongside the med-supply ones, and some contain serious vulnerabilities if ever installed:
   - `eoc_base/controllers/api_proxy_controller.py:7` — unauthenticated open SSRF proxy (`auth='public'`, `cors='*'`, fetches any URL passed to it).
   - `eoc_base/controllers/geojson_controller.py` — public endpoints that **write files into the addons directory** (runtime code modification → RCE).
   - `spiffy_theme_backend/controllers/main.py` — **31 `auth='public'` routes** using `.sudo()`.
   - These routes only activate if the module is installed in the DB, but the safe move is: build the production `custom-addons/` with **only** what `erpmedsupply` needs. The authoritative, DB-verified list (queried from the live database 2026-06-13, after the Nile theme replaced Spiffy) is in `docs/PRODUCTION_HARDENING_RUNBOOK.md` §5 "Minimal addon set for production": 14 dirs from `custom-addons/` (OCA reconcile stack, Odoo Mates accounting, `web_responsive`, `web_chatter_position`, `ui_kanban_first`) plus 5 `nile_*` dirs from the `odoo-nile-theme` repo. `spiffy_theme_backend` and `bank-payment-18.0` are **no longer** part of the set.
   - Spiffy also ships a **Firebase service-account private key** in `static/description/firebase-key/` — delete that file regardless (and consider the key compromised).

5. **Demo credentials in the database** — `admin/admin` plus five users (amira/khalid/sara/mohammed/layla) all with password `demo1234` (`scripts/seed_more.py:97`). If going live from this seeded DB, reset every password first and decide what demo transactional data (fake invoices, DEMO-AGED-* records, hardcoded 2,400→4,500 FX history) stays or gets archived. Cleanest path: keep `erpmedsupply` as the demo, seed a fresh production DB with only master data (products, partners, warehouses, users) — no fake transactions.

## High-priority warnings (fix in week one)

- **Backups miss the filestore** — `scripts/backup_db.sh` only does `pg_dump`; uploaded attachments live in the `odoo-data` volume and would be lost. Add a tar of `/var/lib/odoo/filestore/<db>` to the script (and to restore).
- **Certbot has no `restart:` policy** (`docker-compose.yml:65`) — if it dies, certs silently expire. Add `restart: unless-stopped`.
- **No Docker log rotation or memory limits** — add `logging: {options: {max-size: "100m", max-file: "3"}}` and memory limits to the `odoo` and `db` services, or a small VPS will eventually fill its disk / OOM.
- **Tune `workers`** in `odoo.conf.prod` to `(CPU cores × 2) + 1` for the server bought (current `workers = 2` suits a 1–2 core box).
- `seed_cleanup.py` is not idempotent (deletes/recreates FX rates and the USD bill every run) — never run it against a live DB.

## Already production-grade (keep)

NGINX config (TLS redirect, security headers, websocket/8072 routing, rate limiting 20r/s, gzip, 100M upload limit, static caching); Postgres healthcheck + isolated network (no exposed 5432); `list_db = False` + `proxy_mode = True` in the prod template; tested backup/restore/SSL/setup scripts; `docs/PRODUCTION_HARDENING_RUNBOOK.md`.

## Hosting plan — from nothing to live

### 1. Buy the infrastructure (~$10–20/month total)
- **VPS:** Ubuntu 24.04 LTS, **4 vCPU / 8 GB RAM / 80 GB SSD** is comfortable for ~20 concurrent users (4 GB / 2 vCPU works to start). Hetzner (~€8–15/mo, Falkenstein/Helsinki) or DigitalOcean; for Sudan-based users, Frankfurt/Helsinki gives the best latency.
- **Domain:** any registrar (Namecheap, Cloudflare Registrar, ~$10/yr). Create an **A record** pointing to the VPS IP.

### 2. Prepare the repo locally (the blocker fixes)
Remove the mac-path mounts, fix `dbfilter`/`.env.example` to `^erpmedsupply$`, purge the old secret from git history, trim `custom-addons` to the needed modules, delete the Firebase key. Push to a **private** GitHub/GitLab repo.

### 3. Harden the server (first 30 minutes after it boots)
Non-root user with SSH key auth; disable password SSH login; `ufw` allowing only 22/80/443; `fail2ban`; unattended-upgrades; install Docker Engine + compose plugin.

### 4. Deploy
Clone the repo. Write a fresh `.env` (new `openssl rand` passwords, `DOMAIN=`, `SSL_EMAIL=`). `cp odoo.conf.prod odoo.conf` and fill the two secrets. `docker compose up -d`. Restore the database: gzip a `pg_dump` of `erpmedsupply` locally, copy it up, use `scripts/restore_db.sh`. Immediately reset admin and all demo-user passwords.

### 5. TLS
Run `scripts/ssl-setup.sh` (drives certbot + swaps `nginx/active.conf` to the SSL config). Verify `https://yourdomain` loads and HTTP redirects.

### 6. Backups + monitoring (before announcing go-live)
Install the cron from `scripts/backup_db.cron.example` (after adding filestore backup). Ship backups **off the server** — nightly `rclone` to Backblaze B2/Google Drive is fine; a server-only backup is not a backup. Do one **test restore**. Free UptimeRobot/healthchecks.io ping on the login page + a cert-expiry check.

### 7. Go-live checklist
- [ ] `list_db = False`, `dbfilter = ^erpmedsupply$`, no `dev_mode`
- [ ] `workers` tuned to server cores
- [ ] All passwords rotated (admin, demo users, Postgres, master password)
- [ ] Old secret purged from git history (`git log --all -p | grep '<OLD-PASSWORD-REDACTED>'` → 0 hits; use the literal old password — done 2026-06-13, re-check before push)
- [ ] `custom-addons` trimmed to med-supply modules only; Firebase key deleted
- [ ] `certbot renew --dry-run` passes
- [ ] Backup cron installed (DB + filestore), offsite sync configured, restore tested
- [ ] Log rotation + memory limits in docker-compose
- [ ] `docker compose ps` shows all containers healthy
