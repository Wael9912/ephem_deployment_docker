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

## Regenerate the user manual (Word + PDF, EN + AR)
Single source: `scripts/build_manual.py` — `fill_en()` / `fill_ar()` hold the content;
renderers emit DOCX (python-docx) and HTML for both languages. Arabic is RTL.
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
- Default pricelist is created in the chart's currency (USD) → forces invoices to USD.
  The seed sets all pricelists to SDG; the SO/invoice currency follows the **pricelist**.
- Manually creating receipt move lines bypasses **putaway** rules; the seed adds an
  explicit internal transfer to land insulin in Cold Storage.
- Inventory valuation is **manual/periodic** + FIFO costing so goods moves post without
  configuring valuation GL accounts. Switch to Automated after setting category accounts.
