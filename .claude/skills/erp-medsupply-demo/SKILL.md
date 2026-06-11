---
name: erp-medsupply-demo
description: Build, seed, verify, and document the Sudan medical-supply ERP demo on this Odoo 18 Community stack. Use when asked to (re)create the erpmedsupply database, run/seed demo data, verify the demo, regenerate the user manual (Word/PDF), or build the customer sales/demo deck (PDF).
---

# Medical-Supply ERP demo runbook

A reproducible Odoo 18 **Community** medical-supply ERP demo (database `erpmedsupply`):
inventory + warehousing + procurement + sales + accounting, multi-currency
(**SDG** base, **USD** reference). All scripts live in `scripts/`.

## Prerequisites
- Docker Desktop running (`docker info` succeeds). If down, the user must start it
  manually — `open -a Docker` is unreliable here.
- `addons_path` in `odoo.conf` / `odoo.conf.prod` must include
  `/mnt/extra-addons/bank-payment-18.0` (it is **not** recursive). Already patched.
- `dbfilter` in `odoo.conf` allows `erpmedsupply` (currently `^(ephem_uganda|erpmedsupply)$`).

## 1. Start Postgres
```bash
docker compose up -d db
# wait for healthy:
docker inspect -f '{{.State.Health.Status}}' ephem-db
```

## 2. Create + install modules (auto-creates the DB)
```bash
docker compose run --rm -T odoo odoo -d erpmedsupply \
  -i account,contacts,stock,purchase,sale_management,product_expiry,stock_landed_costs,\
om_account_accountant,account_reconcile_oca,account_statement_base,account_reconcile_model_oca,\
spiffy_theme_backend \
  --without-demo=all --stop-after-init --log-level=warn
```
`stock_account`, `purchase_stock`, `sale_stock` auto-install; `om_account_accountant`
pulls the full accounting suite. `generic_coa` chart loads from `account` (no separate
`l10n_generic_coa` module in this image). **`spiffy_theme_backend`** is the active backend
theme used in all screenshots — keep it in the install list.

## 3. Seed master data + transactions
```bash
docker compose run --rm -T odoo odoo shell -d erpmedsupply --no-http --log-level=error \
  < scripts/seed_medsupply.py
```
`scripts/seed_medsupply.py` is idempotent-guarded (bails if "Khartoum Teaching Hospital"
exists). It commits in phases via `env.cr.commit()` — **required**, `odoo shell` does not
auto-commit piped scripts.

Then layer the richer demo + a consistency cleanup (both idempotent, run in order):
```bash
docker compose run --rm -T odoo odoo shell -d erpmedsupply --no-http --log-level=error < scripts/seed_more.py
docker compose run --rm -T odoo odoo shell -d erpmedsupply --no-http --log-level=error < scripts/seed_cleanup.py
```
- `seed_more.py` adds **role users** (amira/khalid/sara/mohammed/layla, pwd `demo1234`), customer
  **payments** (bank + cash safe), a posted+paid SDG **vendor bill** and a posted unpaid **USD bill**,
  3 more posted customer invoices with staggered/overdue due dates (aged reports), **reordering rules**,
  a draft **RFQ**, and a **bank statement** for the reconciliation demo. It also aligns the fiscal country
  + the 15% taxes to **Sudan** (generic_coa ships them as US-country, which blocks direct invoice posting).
- `seed_cleanup.py` re-asserts the **USD rate history 2,400→4,500** (the real 1 USD = 4,500 SDG; SDG prices
  are scaled to match, so the rate and prices must move together), recreates the USD bill at the 4,500 rate,
  moves the reconciliation statement onto *Bank of Khartoum (SDG)*, and deactivates the empty generic
  **Bank/Cash** journals so the dashboard shows only the four named bank/cash journals.

## 3b. Extract ground truth (anti-hallucination source for the manual)
```bash
docker compose run --rm -T odoo odoo shell -d erpmedsupply --no-http < scripts/extract_ground_truth.py > /tmp/gt.txt
# split the JSON between ===GT_JSON_START/END=== into docs/manual/_ground_truth/*.json (see the inline splitter)
```
Produces per-model `form_*.json` (every field label/help/type/page + buttons + statusbar states),
`menu_tree.json`, `roles.json`, and `demo.json` (exact counts/records). The manual is written **against
these files** so field names, menu paths and numbers are never invented.

## 4. Serve + verify
```bash
docker compose up -d odoo
# app: http://localhost:8069  -> pick erpmedsupply  -> admin / admin
```
Verification snippet (counts, stock math, FEFO lots, cold-storage location, invoice
currency = SDG, USD rate history) is in the transcript; rerun via
`docker compose run --rm -T odoo odoo shell -d erpmedsupply --no-http < /tmp/verify_medsupply.py`.

## Rebuild from scratch (preserves the Spiffy theme + Alexandria font)
The economy is built at the **real 1 USD = 4,500 SDG** (SDG prices are scaled to match in
`seed_medsupply.py`/`seed_more.py`, so rate and prices move together — don't change one alone).
```bash
# 0. back up the Spiffy theme (so the exact teal/dark palette + Alexandria font survive the drop)
docker compose exec -T db pg_dump -U odoo -d erpmedsupply --data-only --column-inserts \
  --table=backend_config --table=google_font_family > backups/spiffy/spiffy_theme.sql
# 1. drop + reinstall (step 2 list, incl. spiffy_theme_backend) + seed (step 3: medsupply, more)
docker compose stop odoo
docker compose exec -T db psql -U odoo -d postgres -c "DROP DATABASE IF EXISTS erpmedsupply WITH (FORCE);"
#    ...run step 2 install, then seed_medsupply.py + seed_more.py...
# 2. restore the theme + select Alexandria + activate Arabic (ORM is safer than truncate:
#    res_users.backend_theme_config FKs backend_config, so TRUNCATE CASCADE would delete users).
#    Re-apply the saved backend.config field values to every backend.config row and create a
#    google.font.family(name='Alexandria', is_selected=True) per user's config; then run the
#    Arabic language-install wizard. (See the session transcript / restore_theme_lang.py.)
docker compose up -d odoo
```
Gotchas:
- **The Odoo container is recreated on a `compose up` after image/config drift**, which **loses
  pip/apt packages installed at runtime** — reinstall WeasyPrint + poppler before building/rendering:
  `docker compose exec -u root odoo bash -lc 'apt-get install -y -qq libpango-1.0-0 libpangocairo-1.0-0 libpangoft2-1.0-0 poppler-utils && pip install --break-system-packages -q weasyprint'`
- After a rebuild, record IDs shift slightly — re-run the ID probe and update the `ID` dict in
  `scripts/capture_screens.py` before re-capturing.
- The fiscal-country tax fix (Sudan) lives in `seed_more.py`; without it, directly-posted invoices fail.

## Install Arabic in the system (bilingual UI / Arabic screenshots)
`ar_001` (generic Arabic, maps to the `ar` .po files) is the Sudan UI language. Activate
it with the language-install wizard — `--load-language=ar_001` alone loads only part
(field labels but not menus):
```bash
docker compose run --rm -T odoo odoo shell -d erpmedsupply --no-http <<'PY'
lang = env["res.lang"].with_context(active_test=False).search([("code","=","ar_001")],limit=1)
env["base.language.install"].create({"lang_ids":[(6,0,[lang.id])],"overwrite":True}).lang_install()
env.cr.commit()
PY
```
The app name "Sales" stays English (Odoo default); everything else translates.

## Capture real screenshots (EN + AR) — Spiffy theme
The UI now runs the **Spiffy backend theme** (`spiffy_theme_backend`, dark navbar, a 9-dot app
launcher, a vertical quick-action rail). `scripts/capture_screens.py` drives headless Chromium
(Playwright) over a **~53-shot manifest** covering every module, key forms (it opens specific
notebook tabs by index — language-independent — e.g. product Inventory=3, Purchase=2; partner
Sales&Purchase=1, Accounting=3), lists, dashboards and functions → `docs/manual/img/{en,ar}/`.
```bash
pip3 install --user playwright && python3 -m playwright install chromium   # host, once
# EN: set admin lang en_US, RESTART odoo, capture
printf "env.ref('base.user_admin').lang='en_US'\nenv.cr.commit()\n" | docker compose run --rm -T odoo odoo shell -d erpmedsupply --no-http
docker compose restart odoo && sleep 12
python3 scripts/capture_screens.py en
# AR: set admin lang ar_001, RESTART odoo, capture (then leave it ar_001 — the user's UI language)
printf "env.ref('base.user_admin').lang='ar_001'\nenv.cr.commit()\n" | docker compose run --rm -T odoo odoo shell -d erpmedsupply --no-http
docker compose restart odoo && sleep 12
python3 scripts/capture_screens.py ar
```
Gotchas:
- `dbfilter` matches >1 DB → log in via `/web/login?db=erpmedsupply`; Odoo holds a long-poll
  socket so after login wait on `.o_main_navbar`, never `networkidle`.
- **App launcher (apps_home)**: the Spiffy toggle is `a.appDrawerToggle` and Playwright's normal
  click is intercepted — open it with `page.eval_on_selector("a.appDrawerToggle","e=>e.click()")`.
- The worker **caches user lang + FX rates** — `docker compose restart odoo` before each capture.
- The script removes onboarding/tour overlays (`.o_onboarding_container`, etc.) via JS before each shot.

## Write the manual content (bilingual, grounded) — Workflow
`scripts/wf_manual_content.js` is a **Workflow** (run via the Workflow tool) that drafts then
**adversarially verifies** 17 chapters (EN + AR), each grounded in `docs/manual/_ground_truth/*`
and `figures.json`. Draft and verify agents read the ground-truth files and **write each chapter to
`docs/manual/_content/<key>.json`** (`{title_en,title_ar,blocks_en,blocks_ar}`); the verify pass
fact-checks every field label, menu path, button and number against the ground truth + live DB and
fixes mismatches in place. The workflow returns only small status (content lives in the files).
Chapter order is the `CHAPTER_ORDER` list in `build_manual.py`.

## Build the manual (Word + PDF, EN + AR)
`scripts/build_manual.py` assembles `docs/manual/_content/*.json` (falls back to the legacy
`fill_en/fill_ar` only if `_content` is empty), renders DOCX (python-docx) and HTML (images
base64-inlined). Arabic is RTL and uses **Alexandria** — the same Arabic font applied to the system
via Spiffy (`scripts/fonts/Alexandria-{Regular,Bold}.ttf`, `@font-face` at `file:///tmp/fonts/...`).
WeasyPrint in the container renders correct Arabic bidi (never wkhtmltopdf for AR) — but a container
recreate loses it, so reinstall if `No module named weasyprint` (see the Rebuild gotchas). One command
does it all:
```bash
bash scripts/build_manual_pdf.sh   # -> docs/manual/Medical-Supply_ERP_User_Manual_{EN,AR}.{docx,pdf}
```
Notes:
- The container has no Arabic system font, so the AR PDF embeds Alexandria from `scripts/fonts/`.
- The manuals must **not** mention "ePHEM" (per client request) — keep `META`/content clean.

## Build the customer demo / sales deck (PDF)
A **bilingual** 16:9 live-demo deck (audience: an Excel-only manager) lives at
`docs/deck/Medical-Supply_ERP_Demo_Deck_{EN,AR}.{pdf,html}` (**15 slides**, AR is full RTL with
Arabic screenshots) + a presenter cheat-sheet `docs/deck/PRESENTER_GUIDE.md`. `scripts/build_deck.py`
(`en`/`ar` arg) assembles a **self-contained** HTML (real screenshots from `docs/manual/img/{en,ar}/`
+ Alexandria font, all base64-inlined); `scripts/build_deck_pdf.sh` builds both languages with
**WeasyPrint inside the odoo container**:
```bash
bash scripts/build_deck_pdf.sh   # -> docs/deck/Medical-Supply_ERP_Demo_Deck_{EN,AR}.{html,pdf}
```
Flow: problem → "one connected system" → **7 capability slides** (each grounds a **real** demo number
and carries a **▶ SHOW LIVE** cue) → Excel-vs-ERP table → cost & growth → switching → 4-week roadmap →
CTA. **Every figure is real demo data** from `docs/manual/_ground_truth/demo.json` (P00002 $1,288 ⇄
5,796,000 SDG; insulin reorder 20/80; dashboard 3,966,350 unpaid / 3,924,950 SDG bank) — re-verify
after a reseed.

**Deck/manual layout, RTL and WeasyPrint gotchas now live in the `manual-deck-builder` skill** —
read it before editing either document. The headline traps: `inline-flex` renders full-width (use
`inline-block` chips + a filled play glyph in the cue), use a real `<table dir>` for the compare
table (flex mis-mirrors under RTL), `fit_w()` keeps captions off the cue band, and QA by rasterizing
in the container (`pdftoppm`) since the host has no poppler/WeasyPrint.

## Gotchas learned
- **USD FX rate direction**: store the USD `res.currency.rate` as `rate = 1/N` so 1 USD = N
  SDG. Writing `company_rate = N` inverts it on this build (the PO `amount_total_cc` is a
  **stored** field = `amount_total / currency_rate`, set at seed time and NOT recomputed on
  later rate edits) → e.g. $1,288 showed as 1.84 SDG. Verify with
  `usd._convert(1.0, sdg, company, date) == N`. Stale stored conversions only clear on a
  rebuild, so re-seed rather than patch live records.
- The seed sets the company to **Sudan MedSupply Co.** (Khartoum, Sudan) — don't leave it
  as "My Company".
- Default pricelist is created in the chart's currency (USD) → forces invoices to USD.
  The seed sets all pricelists to SDG; the SO/invoice currency follows the **pricelist**.
- Manually creating receipt move lines bypasses **putaway** rules; the seed adds an
  explicit internal transfer to land insulin in Cold Storage.
- Inventory valuation is **manual/periodic** + FIFO costing so goods moves post without
  configuring valuation GL accounts. Switch to Automated after setting category accounts.

## UI/UX addons & custom-theme program (2026-06-11)

The demo DB has two in-house UI addons installed (code lives in the **nested git repo**
`custom-addons/` — it has its own branches/remote, separate from this repo):

- **medsupply_ui_refresh** — CSS-only overlay on Spiffy: card form sheets, always-visible
  input borders, grouped-kanban headers/lanes (sale/purchase/stock.picking get
  `default_group_by="state"`), list polish. Depends on spiffy → cascades away if spiffy is
  uninstalled. Branch `ui-ux-refresh`+.
- **ui_kanban_first** — kanban is the default first view on all window actions (80 moved,
  28 prepended). `post_init_hook` runs at install only; re-apply via odoo shell:
  `from odoo.addons.ui_kanban_first import post_init_hook; post_init_hook(env); env.cr.commit()`.
  Exclude models via ir.config_parameter `ui_kanban_first.exclude_models`. Branch `custom-theme`+.

Install/update pattern (avoid registry races):
`docker compose stop odoo && docker compose run --rm odoo odoo -c /etc/odoo/odoo.conf -d erpmedsupply -i <addon> --stop-after-init && docker compose up -d odoo`

**Spiffy replacement ("Nile" theme)**: master plan in `docs/CUSTOM_THEME_PLAN.md`, audit with
no-spiffy evidence in `docs/theme-audit/SPIFFY_AUDIT.md` (branch `nile-theme` in both repos).
Any theme/UI change ⇒ the 53 manual screenshots + both decks show the old UI and need
re-capture (`scripts/capture_screens.py en|ar`) before the next manual/deck rebuild.
Screenshot gotchas: never wait on `networkidle` (longpolling hangs); login with
`/web/login?db=erpmedsupply`; use absolute output paths.
