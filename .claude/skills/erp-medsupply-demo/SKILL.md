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
- **Addons come from two mounts now** (the ERP is decoupled from the `borse/ePHEM`
  monorepo — see the UI/theme section): `/mnt/extra-addons` = ERP addons,
  `/mnt/nile-theme` = the `nile_*` backend theme. The dev `odoo.conf` `addons_path`
  lists both (plus `/mnt/extra-addons/bank-payment-18.0`, which is **not** recursive).
  In **dev** the `docker-compose.override.yml` mounts the full borse checkout at
  `/mnt/extra-addons` and `~/Documents/odoo-nile-theme` at `/mnt/nile-theme`; in **prod**
  the base compose mounts the two dedicated repos instead.
- `dbfilter` in dev `odoo.conf` allows `erpmedsupply` (and the throwaway `erpmedsupply_nile`).

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
ui_kanban_first,web_responsive,web_chatter_position,\
nile_core,nile_components,nile_shell,nile_config,nile_brand_medsupply \
  --without-demo=all --stop-after-init --log-level=warn
```
`stock_account`, `purchase_stock`, `sale_stock` auto-install; `om_account_accountant`
pulls the full accounting suite. `generic_coa` chart loads from `account` (no separate
`l10n_generic_coa` module in this image).

**Theme = Nile (Spiffy is retired/deleted as of 2026-06-13).** The active backend look is the
in-house `nile_*` stack on the OCA `web_responsive` shell, with `nile_brand_medsupply` supplying
the MedSupply logo/login/favicon. The `nile_*` addons resolve via the `/mnt/nile-theme` mount
(repo `Wael9912/odoo-nile-theme`, branch `18.0`). After install, set the per-user chatter default
to bottom: `env['ir.default'].set('res.users','chatter_position','bottom')` (commit). Company
branding (logo, `nile_menubar_logo`, tab name) + the anon-page ICP keys
(`nile.tab_name` / `nile.favicon_url` / `nile.login_background_url`) are set by the brand pack on
install — verify rather than re-do. The end-user **Theme Settings** dialog (systray paint-brush)
is `nile_config` — a **tabbed panel (Brand / Typography / Display)**: company palette presets + a
custom color with an **inline HSV picker** (Brand, admin-only); per-user font/size **plus the
company Google-Fonts link** (Typography — the font upload moved here from Brand on 2026-06-13b,
admin-only); density / **dark mode** / chatter position (Display). A separate **systray globe**
switches the UI language (writes `res.users.lang`, refreshes the session context, then reloads so
the LTR↔RTL flip lands on the FIRST reload). Adds DB fields
`res.company.nile_font_url/nile_font_name` → needs `-u nile_config` on an existing DB.

**Dark mode (Phase 3, 2026-06-13):** a real dark skin ships in `nile_components/dark.scss`
(Community has no core dark CSS). It's **off by default** — demos run in light. Toggle via the
Theme dialog (Dark Mode → On → Save) or `res.users.nile_dark_mode`; it loads `web.assets_web_dark`
via the `color_scheme` cookie. A compile-time WCAG-AA gate (`nile_core/contrast.scss`) breaks the
build on a failing palette — hard-tested by `nile_core/tests/test_contrast.py` (`--test-enable`).
A 2026-06-13b pass extended the dark skin to the **Discuss** app (sidebar/header/thread/composer)
and fixed dark-on-dark text — notably the **black kanban column counter** (`.text-900`) and the
grayscale text utilities `.text-{900,800,700,600,muted,dark,black}`, which compile to fixed grays.
**Local SCSS-change gotcha:** dev `odoo.conf` has no `assets` dev flag, so bundles are cached by
checksum — to see a `.scss` edit you must `docker compose restart odoo` (clears the ormcache) **and**
purge `text/css` `ir.attachment`s, else you'll get stale CSS.

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

**Theme/UI verification:** `python3 scripts/qa_dark_sweep.py erpmedsupply` screenshots
{light,dark}×{en_US,ar_001} of the main views into `docs/theme-audit/qa/dark-sweep/` and runs a
luminance gap-finder (flags any surface still light in dark mode), overflow/broken-img/font checks,
and JS-error capture — expect **0 findings**. Older light-only sweep: `scripts/qa_visual_sweep.py`.
WCAG contrast gate: `docker compose exec -T odoo odoo -d erpmedsupply -u nile_core --test-enable
--test-tags /nile_core --http-port=8999 --gevent-port=8998 --stop-after-init` (expect `0 failed`).
**Critical-flow tour (EN+AR smoke):** `python3 ~/Documents/odoo-nile-theme/.github/scripts/run_tours.py
http://localhost:8069 erpmedsupply en_US` (then `ar_001`) walks login→app launcher→list→form→create+
save and asserts the bundle flips to RTL in Arabic + Alexandria renders. **Non-destructive** (creates+
unlinks a "Nile Tour Probe" contact, restores the admin lang) so it's safe on the live demo DB. This is
the same script the theme repo's CI `tours` lane runs per brand.

## Rebuild from scratch (Nile theme is code, not DB config — no backup/restore dance)
The economy is built at the **real 1 USD = 4,500 SDG** (SDG prices are scaled to match in
`seed_medsupply.py`/`seed_more.py`, so rate and prices move together — don't change one alone).
Unlike Spiffy (whose look lived in fragile `backend_config` DB rows), the Nile theme is entirely
in addon code, so a rebuild just reinstalls the `nile_*` addons — nothing to snapshot/restore.
```bash
# 1. drop + reinstall (step 2 list, incl. the nile stack) + seed (step 3: medsupply, more)
docker compose stop odoo
docker compose exec -T db psql -U odoo -d postgres -c "DROP DATABASE IF EXISTS erpmedsupply WITH (FORCE);"
#    ...run step 2 install, then seed_medsupply.py + seed_more.py...
# 2. re-apply the small DB-side branding the addons can't carry, then activate Arabic:
#    - chatter default bottom: env['ir.default'].set('res.users','chatter_position','bottom')
#    - company logo + nile_menubar_logo from nile_brand_medsupply/static/img (base64); tab name
#    - verify ICP nile.tab_name / nile.favicon_url / nile.login_background_url (brand pack sets these)
#    - run the Arabic language-install wizard (see below)
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

## Capture real screenshots (EN + AR) — ⚠️ PIPELINE NOT YET UPDATED FOR NILE
> **DEFERRED Phase-1 doc task (as of 2026-06-13):** the live UI now runs the **Nile theme**
> (`web_responsive` shell), but `scripts/capture_screens.py` and the committed screenshots
> (`docs/manual/img/{en,ar}/`) + both decks **still show the dead Spiffy UI**. Before re-capture
> someone must update the script's chrome selectors for `web_responsive` (the Spiffy app-launcher
> selector `a.appDrawerToggle` and the quick-action rail no longer exist; web_responsive uses its
> own apps-menu/burger). Until then, **do not run a capture against the nile DB expecting the old
> shots** — the manual/decks are knowingly stale. See the UI/theme section + memory `erp-custom-theme`.

`scripts/capture_screens.py` drives headless Chromium (Playwright) over a **~53-shot manifest**
covering every module, key forms (it opens specific notebook tabs by index — language-independent —
e.g. product Inventory=3, Purchase=2; partner Sales&Purchase=1, Accounting=3), lists, dashboards
and functions → `docs/manual/img/{en,ar}/`.
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
- **App launcher (apps_home)**: the old Spiffy toggle `a.appDrawerToggle` is GONE — `web_responsive`
  renders its own apps menu (burger / `.o_menu_apps`). This is the main selector to re-map when
  updating the script for Nile.
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
base64-inlined). Arabic is RTL and uses **Alexandria** — the same Arabic font self-hosted in the
system UI by `nile_core` (`scripts/fonts/Alexandria-{Regular,Bold}.ttf`, `@font-face` at `file:///tmp/fonts/...`).
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

## UI/theme: Nile is live; Spiffy is retired (current as of 2026-06-13)

**Phases 0–4 ALL DONE; `18.0` tagged `v18.0.1.2.0` (2026-06-14).** Latest (`v18.0.1.2.0`): the
app-launcher (9-dots) background follows the Nile palette and is admin-customizable from the Theme
dialog (Brand tab → "App Menu Background"); plus the Arabic Google-Fonts help-text now renders. It also
carries: the Phase-3 real
dark skin + neutral-dark navbar + dark toggle + WCAG contrast gate + a11y; a **UI refinement pass**
(palette-follow extended so the company color reaches the statusbar / settings rail / view-switcher /
notebook; grouped-kanban count-chip corner fix; stronger elevation + focus ring); the
**comprehensive tabbed Theme Settings panel** (inline HSV picker, company Google-Fonts link,
systray globe language switcher); a **Hoot JS test scaffold + CI `js-tests` lane**; the **2026-06-13b
bug-fix pass** (first-reload RTL flip, submenu palette-follow, dark Discuss, dark kanban/text, font→
Typography tab → `v18.0.1.1.1`); and the **Phase-4 "everything" tier** (`28c97b2`: EN/AR critical-flow
tour matrix in CI via `.github/scripts/run_tours.py`, `UPGRADE_19.md` 19.0 port checklist, per-addon
READMEs). Dark is off by default. See memory `erp-custom-theme` and `docs/CUSTOM_THEME_PLAN.md`. **Only
remaining plan item: the deferred Phase-1 doc re-capture (this section), ON HOLD until the user asks.**

**Repo layout (the ERP is decoupled from `borse/ePHEM`):**
- `Wael9912/ephem_deployment_docker` (this repo) — deployment: compose, configs, scripts, docs. Branch `nile-theme`.
- `Wael9912/erpmedsupply-addons` (`main`) — the **14 ERP addons** (OCA/OdooMates accounting,
  `web_responsive` [with the `env.isSmall` 18.0 patch], `web_chatter_position`, original
  `ui_kanban_first`). Mounted at `/mnt/extra-addons` in prod. Dependency-closure verified.
- `Wael9912/odoo-nile-theme` (`18.0`, pinned tag **`v18.0.1.2.0`**) — the `nile_*` theme stack
  (ship 5 for ERP: `nile_core`, `nile_components`, `nile_shell`, `nile_config`, `nile_brand_medsupply`).
  Mounted at `/mnt/nile-theme`. Prod clones are pinned to tags — see `docs/DEPLOY_PINS.md`.
- `borse/ePHEM` checkout (`custom-addons/`) — the 121-addon platform monorepo, now **DEV-ONLY**
  (mounted only by `docker-compose.override.yml`). Do **not** ship it or push ERP changes to it.

**`ui_kanban_first`** — kanban is the default first view on all window actions (80 moved, 28
prepended). `post_init_hook` runs at install only; re-apply via odoo shell:
`from odoo.addons.ui_kanban_first import post_init_hook; post_init_hook(env); env.cr.commit()`.
Exclude models via ir.config_parameter `ui_kanban_first.exclude_models`.

**Nile theme** — built in-house to replace Spiffy. Master plan `docs/CUSTOM_THEME_PLAN.md`; QA
audit `docs/theme-audit/QA_AUDIT_2026-06-13.md`. Layers: `nile_core` (design tokens, fonts,
SCSS knobs) → `nile_components` (absorbed the old `medsupply_ui_refresh` overlay, `--msr-*`→`--nile-*`)
→ `nile_shell` (logo/login/favicon on `web_responsive`) + `nile_config` (runtime theme dialog) →
brand pack `nile_brand_medsupply`. Live on `erpmedsupply` since the 2026-06-12 switchover;
`nile_config` + the QA fixes (reduced-motion dropdown bug, 13px base) shipped 2026-06-13.

**Retired & DELETED 2026-06-13** (uninstalled in every DB, then `git rm`'d from `custom-addons`):
`spiffy_theme_backend` (with its bundled third-party **Firebase key** — a Bizople vendor key, not
ours; closed a prod-readiness blocker), `medsupply_ui_refresh` (superseded by `nile_components`),
`eoc_theme_backend`. Don't reference these as installable.

Install/update pattern (avoid registry races; a live DB needs `update_list()` first if the nile/OCA
addons are new to it): `docker compose stop odoo && docker compose run --rm odoo odoo -c /etc/odoo/odoo.conf -d erpmedsupply -i <addon> --stop-after-init && docker compose up -d odoo`

**Docs lag the UI:** the 53 manual screenshots + both decks still show the dead Spiffy UI — see the
⚠️ note in the capture section (deferred Phase-1 task). Screenshot gotchas that still hold: never
wait on `networkidle` (longpolling hangs); login with `/web/login?db=erpmedsupply`; absolute output
paths; restart odoo after SQL lang flips (ormcache). RTL bundles use a `.rtl.` **filename suffix**,
not a `/rtl/` path. The `nile_core` `web_responsive` patch (`apps_menu.xml`: `this.ui.isSmall`→`env.isSmall`)
must be re-checked on every Odoo image bump — it now lives in `erpmedsupply-addons/web_responsive`.
