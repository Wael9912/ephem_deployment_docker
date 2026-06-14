#!/usr/bin/env bash
# Remove the 4 orphaned, source-removed module CATALOG rows that linger in the
# Apps list after the consolidation swap (nile_core/components/shell/config).
# They are already 'uninstalled' (no app data); this just deletes the leftover
# ir.module.module records so they stop showing in Apps. nile_brand_cmp/ephem
# are intentionally KEPT (uninstalled here, but their source still exists).
set -euo pipefail
docker exec -i ephem-app odoo shell -d erpmedsupply --no-http <<'PY'
recs = env["ir.module.module"].search([
    ("name", "in", ["nile_core", "nile_components", "nile_shell", "nile_config"]),
    ("state", "=", "uninstalled")])
print("purging:", recs.mapped("name"))
recs.unlink()
env.cr.commit()
print("remaining nile records:", env["ir.module.module"].search([("name", "like", "nile_%")]).mapped("name"))
PY
