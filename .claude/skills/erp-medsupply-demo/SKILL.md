---
name: erp-medsupply-demo
description: Build, seed, verify, and document the Sudan medical-supply ERP demo on this Odoo 18 Community stack. Use when asked to (re)create the erpmedsupply database, run/seed demo data, verify the demo, or regenerate the user manual (Word/PDF).
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
om_account_accountant,account_reconcile_oca,account_statement_base,account_reconcile_model_oca \
  --without-demo=all --stop-after-init --log-level=warn
```
`stock_account`, `purchase_stock`, `sale_stock` auto-install; `om_account_accountant`
pulls the full accounting suite. `generic_coa` chart loads from `account` (no separate
`l10n_generic_coa` module in this image).

## 3. Seed master data + transactions
```bash
docker compose run --rm -T odoo odoo shell -d erpmedsupply --no-http --log-level=error \
  < scripts/seed_medsupply.py
```
`scripts/seed_medsupply.py` is idempotent-guarded (bails if "Khartoum Teaching Hospital"
exists). It commits in phases via `env.cr.commit()` — **required**, `odoo shell` does not
auto-commit piped scripts.

## 4. Serve + verify
```bash
docker compose up -d odoo
# app: http://localhost:8069  -> pick erpmedsupply  -> admin / admin
```
Verification snippet (counts, stock math, FEFO lots, cold-storage location, invoice
currency = SDG, USD rate history) is in the transcript; rerun via
`docker compose run --rm -T odoo odoo shell -d erpmedsupply --no-http < /tmp/verify_medsupply.py`.

## Rebuild from scratch
Stop Odoo to free connections, then drop and repeat from step 2:
```bash
docker compose stop odoo
docker compose exec -T db psql -U odoo -d postgres -c "DROP DATABASE IF EXISTS erpmedsupply WITH (FORCE);"
```

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

## Capture real screenshots (EN + AR)
`scripts/capture_screens.py` drives headless Chromium (Playwright) and deep-links into the
actual demo records → `docs/manual/img/{en,ar}/`, embedded by the manual builder.
```bash
pip3 install --user playwright && python3 -m playwright install chromium   # host, once
python3 scripts/capture_screens.py en                                       # admin must be en_US
# Arabic UI: set admin.lang=ar_001, RESTART odoo (the web worker caches user lang AND
# currency rates — a separate-process commit is NOT seen without a restart), then
# `capture_screens.py ar`, finally reset admin.lang=en_US and restart again.
```
Gotchas: `dbfilter` matches 2 DBs, so the script logs in via `/web/login?db=erpmedsupply`;
Odoo holds a long-poll socket, so after login wait on `.o_main_navbar`, never `networkidle`.

## Regenerate the user manual (Word + PDF, EN + AR)
Single source: `scripts/build_manual.py` — `fill_en()` / `fill_ar()` hold the content;
`d.fig(file, caption)` embeds a numbered screenshot from `docs/manual/img/<lang>/`.
Renderers emit DOCX (python-docx, images embedded) and HTML (images base64-inlined, so the
PDF step needs no image copy). Inline `**bold**` and paired `*italic*` are supported.
Arabic is RTL and uses Tajawal in both DOCX and PDF.
```bash
pip3 install --user python-docx        # host, once
python3 scripts/build_manual.py        # -> docs/manual/*_EN/_AR.docx + _manual_EN/AR.html

# container: WeasyPrint renders correct Arabic bidi (wkhtmltopdf here is unpatched Qt
# and garbles RTL inline runs + mixed Latin/Arabic headings — do NOT use it for AR).
docker compose exec -u root odoo bash -lc \
  'apt-get update -qq && apt-get install -y -qq libpango-1.0-0 libpangocairo-1.0-0 libpangoft2-1.0-0 && pip install --break-system-packages -q weasyprint'
docker compose exec -T odoo mkdir -p /tmp/fonts
docker cp scripts/fonts/Tajawal-Regular.ttf ephem-app:/tmp/fonts/Tajawal-Regular.ttf
docker cp scripts/fonts/Tajawal-Bold.ttf    ephem-app:/tmp/fonts/Tajawal-Bold.ttf
for L in EN AR; do
  docker cp docs/manual/_manual_$L.html ephem-app:/tmp/manual_$L.html
  docker compose exec -T odoo python3 -m weasyprint /tmp/manual_$L.html /tmp/manual_$L.pdf
  docker cp ephem-app:/tmp/manual_$L.pdf docs/manual/Medical-Supply_ERP_User_Manual_$L.pdf
done
```
Notes:
- The Arabic PDF embeds the bundled **Tajawal** font (`scripts/fonts/`, referenced via
  `@font-face` at `file:///tmp/fonts/...`). The container has no Arabic system font.
- The manuals must **not** mention "ePHEM" (per client request) — keep `META`/content clean.

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
