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

## Regenerate the user manual (Word + PDF)
Single source: `scripts/build_manual.py` (edit content blocks there).
```bash
pip3 install --user python-docx        # host, once
python3 scripts/build_manual.py        # -> docs/manual/*.docx + _manual.html
docker cp docs/manual/_manual.html ephem-app:/tmp/manual.html
docker compose exec -T odoo wkhtmltopdf --enable-local-file-access --dpi 150 \
  /tmp/manual.html /tmp/manual.pdf
docker cp ephem-app:/tmp/manual.pdf docs/manual/Sudan_MedSupply_ERP_User_Manual.pdf
```
Note: the container's `wkhtmltopdf` is **unpatched Qt** — no multi-input (cover/toc as
separate files) and footer/header switches are ignored. The HTML is therefore a single
self-contained file with CSS page-breaks and an in-page TOC.

## Gotchas learned
- Default pricelist is created in the chart's currency (USD) → forces invoices to USD.
  The seed sets all pricelists to SDG; the SO/invoice currency follows the **pricelist**.
- Manually creating receipt move lines bypasses **putaway** rules; the seed adds an
  explicit internal transfer to land insulin in Cold Storage.
- Inventory valuation is **manual/periodic** + FIFO costing so goods moves post without
  configuring valuation GL accounts. Switch to Automated after setting category accounts.
