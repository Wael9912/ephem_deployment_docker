#!/usr/bin/env bash
# One-shot clean-break swap of erpmedsupply from the 4 old nile modules to the
# single consolidated nile_theme (+ nile_brand_medsupply). Idempotent-ish: safe
# to re-run. A pre-swap backup already exists at
# backups/erpmedsupply_pre_consolidation_20260614.dump (rollback: pg_restore).
set -euo pipefail

DEPLOY=/Users/waelabdalla/Documents/ephem-deploy
THEME=/Users/waelabdalla/Documents/odoo-nile-theme
DB=erpmedsupply
cd "$DEPLOY"

echo "==> 1/5 stop odoo"
docker compose stop odoo

echo "==> 2/5 uninstall old nile chain (source was temporarily restored so this is clean)"
docker compose run --rm -T odoo odoo shell -d "$DB" --no-http <<'PY'
env["ir.module.module"].update_list()
old = env["ir.module.module"].search([
    ("name","in",["nile_core","nile_components","nile_shell","nile_config","nile_brand_medsupply"]),
    ("state","=","installed")])
print("uninstalling:", old.mapped("name"))
old.button_immediate_uninstall()
env.cr.commit()
print("post-uninstall:", {m.name: m.state for m in env["ir.module.module"].search([("name","like","nile_%")])})
PY

echo "==> 3/5 install nile_theme + nile_brand_medsupply (with WCAG gate)"
docker compose run --rm -T odoo odoo -d "$DB" -i nile_theme,nile_brand_medsupply \
  --test-enable --test-tags /nile_theme --stop-after-init --log-level=warn

echo "==> 4/5 remove the temporary old-module source (back to the committed clean tree)"
rm -rf "$THEME/nile_core" "$THEME/nile_components" "$THEME/nile_shell" "$THEME/nile_config"
git -C "$THEME" reset -q -- nile_core nile_components nile_shell nile_config 2>/dev/null || true

echo "==> 5/5 restart odoo"
docker compose up -d odoo

echo "==> DONE. Final nile module states:"
docker exec ephem-db psql -U odoo -d "$DB" -tAc \
  "select name,state from ir_module_module where name like 'nile_%' and state!='uninstalled' order by name;"
echo "Expect: nile_brand_medsupply|installed  and  nile_theme|installed"
