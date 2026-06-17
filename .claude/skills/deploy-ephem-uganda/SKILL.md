---
name: deploy-ephem-uganda
description: >-
  Runbook for upgrading/installing Odoo addons on the live ephem_uganda database
  (ephem-app container) and troubleshooting the ePHEM Analytics dashboard
  builder. Use when asked to deploy, upgrade, or fix ephem_analytics /
  ephem_bridge / ephem_connect (or any module) on ephem_uganda, when dashboards
  won't load/edit, or when widgets show errors. Encodes the exact upgrade +
  live-worker code-reload + cross-module-asset + access-group gotchas learned
  the hard way.
---

# Deploying to ephem_uganda

`ephem_uganda` runs in container **`ephem-app`** (image `ephem-cmp:dev`), Postgres
in **`ephem-db`**. Addons are bind-mounted from this repo's `custom-addons/`
(a SEPARATE nested git repo, remote `github.com/borse/ePHEM`) → `/mnt/extra-addons`,
plus `~/Documents/odoo-nile-theme` → `/mnt/nile-theme`. The mounted working tree
IS what Odoo serves, so editing files on disk changes what's deployed (code reload
still required — see step 3).

## Hard rules
- **`ephem_uganda` is PURE-ePHEM.** Do **NOT** install `ephem_analytics_cmp`
  (the CMP overlay) here — its manifest forbids it without cmp_core/
  cmp_question_bank/cmp_deployment. Keep the overlay source on disk (other DBs on
  the shared mount may be CMP) but never `-i` it on ephem_uganda.
- **Never `-u eoc_base`** — it cascade-reparses the whole EOC country stack and
  detonates pre-existing gutted-feature view refs. Leave EOC modules un-upgraded.
- **Live-DB writes are usually classifier-gated to the USER.** The `-u` upgrade
  via the entrypoint has been allowed; `kill -HUP`, `docker restart`, direct
  `psql`, and dumping the DB password are gated → hand those to the user
  (suggest `! <cmd>`).
- The **latest analytics** lives on branches `ephem-ai` and
  `18_national_dev_dashboard_cached` (NOT `nile-theme`, which historically
  carried stale/partial copies). `ephem-ai` is byte-newest. Restore with
  `git checkout ephem-ai -- <path>` inside `custom-addons`.

## Procedure

### 1. Get the right code on disk (in custom-addons/)
```bash
cd custom-addons
# latest analytics set (only these paths — avoids pulling the retired ephem_ai_* modules):
git checkout ephem-ai -- ephem_analytics ephem_analytics_cmp
# back up anything you overwrite first; clean stale pycache:
find ephem_analytics ephem_analytics_cmp -name __pycache__ -type d -exec rm -rf {} +
python3 -m compileall -q ephem_analytics ephem_analytics_cmp   # sanity
```

### 2. Upgrade the modules (one-off process, NO container restart)
Route through `/entrypoint.sh` so it injects `--db_host/_user/_password` from the
container env (running `odoo` directly fails on a local socket). `ephem_uganda`
pure-ePHEM set:
```bash
docker exec ephem-app /entrypoint.sh -d ephem_uganda \
  -u ephem_analytics,ephem_bridge,ephem_connect \
  --stop-after-init --no-http
```
Success = `Modules loaded.` + `Registry loaded` + `Stopping gracefully`, no
traceback. Benign noise to ignore: `unknown parameter 'ondelete'/'tracking'`
(EOC field defs), `Model eoc.ai.* cannot be loaded` (retired AI modules),
RST `Undefined substitution "---"` (README rendering), the test-framework import
warning.

### 3. RE-IMPORT the code in the live workers — REQUIRED after any .py change
The `-u` updates the DB (ir.rule, columns) but the running prefork workers still
hold the OLD model classes in memory. A registry-signal reload rebuilds from
in-memory classes and does **not** re-read `.py`. Symptom if you skip this:
`ValueError: Invalid field cmp.dashboard.<newfield>` on every query → dashboards
fully down. Fix = make the Odoo master re-exec (re-imports all code):
```bash
docker exec ephem-app kill -HUP 1     # USER runs (classifier-gated)
```
This is Odoo's "phoenix" re-exec: it reuses PID 1's exact current `--db_password`
argv and does NOT re-run the entrypoint, so it bypasses the documented
password-drift restart risk. (The drift is not currently in effect — the env
password is valid — so `docker restart ephem-app` also works; restart policy is
`unless-stopped`.) Static assets (CSS/JS under `/<module>/static/...`) do NOT
need this — they're served live from disk; a browser hard-refresh suffices.

### 4. Verify
```bash
docker logs ephem-app --since 3m 2>&1 | grep -iE "Invalid field|Registry loaded|Traceback" | tail
docker exec ephem-app ps -eo pid,etimes,args | grep odoo   # fresh worker PIDs after HUP
```
Then hard-refresh the browser (Cmd+Shift+R) and open a dashboard.

## Known dashboard issues & fixes
- **"Can't edit dashboards"** → the user lacks the **`ePHEM Analytics / Editor`**
  group (Viewer is read-only; the module never auto-grants Editor, not even to
  admin; `dashboard_view.js` gates the Edit button solely on it). Fix in the UI:
  Settings → Users → [user] → set "ePHEM Analytics" = **Editor**.
- **Widgets show "cmp error" / a raw error tile** → a widget bound to a
  `cmp.dashboard.source` whose model isn't in the registry (CMP-era widget left
  on a pure-ePHEM DB). 9.10.0+ guards this in `cmp.dashboard.widget_data`
  (returns an empty payload); delete the now-empty tiles in the builder.
- **`AssetsLoadingError: .../leaflet-geoman/...`** (map view crashes) → the map
  widget runtime-loads Leaflet/Geoman/geojson from hardcoded
  `/eoc_base/static/src/lib/...` paths. The deployed eoc_base must carry them:
  `git checkout ephem-ai -- eoc_base/static/src/lib/leaflet-geoman` (leaflet/ +
  geojson/ are usually already present). Static files → hard-refresh only.

## Commit
After verifying, commit in `custom-addons` scoped to just the touched paths
(the repo is mid-other-work — never `git add -A`):
```bash
git commit -o ephem_analytics ephem_analytics_cmp eoc_base/static/src/lib/leaflet-geoman -m "..."
git push   # nile-theme tracks origin/nile-theme (borse/ePHEM)
```

See memory `[[ephem-modules-install-reality]]` and `[[ephem-app-db-password-drift]]`.
