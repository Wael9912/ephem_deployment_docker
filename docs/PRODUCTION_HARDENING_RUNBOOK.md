# ePHEM Production Hardening Runbook

Human-executed steps for the three launch blockers. The automated prep (gitignore,
templates, fresh local secrets, backup/restore scripts) is already done in the working
tree. **This runbook covers the irreversible / outward actions that a human must run
deliberately.** Nothing here was executed automatically.

> Assumptions used in the commands below. Override the env vars if yours differ.
>
> | Thing            | Value          |
> |------------------|----------------|
> | Postgres container | `ephem-db`   |
> | Odoo container     | `ephem-app`  |
> | Postgres role      | `odoo`       |
> | Live database      | `erpmedsupply` |
> | Repo path          | `/opt/ephem-deploy` (adjust) |

---

## 0. What was already prepared for you (no action needed)

- `odoo.conf` was removed from the git **index** (`git rm --cached`) — the file still
  exists locally. It is now in `.gitignore`.
- `odoo.conf.example`, `odoo.conf.prod`, `odoo.conf.dev` committed templates created
  (placeholder `CHANGE_ME` secrets, prod-hardened: `proxy_mode=True`, `list_db=False`,
  `log_level=info`, `workers=2`, no `dev_mode`, sane limits).
- Fresh strong passwords were generated and written into the **local untracked**
  `.env` and `odoo.conf` (so the files are ready). **They were NOT applied to the
  running database** — see §1.
- `scripts/backup_db.sh`, `scripts/restore_db.sh`, `scripts/backup_db.cron.example`
  created and syntax-checked.

> The new local secrets are already in `.env` / `odoo.conf`. Treat those files as
> sensitive; they are gitignored. The *old leaked* secret that had to be purged from
> history is written here as `<OLD-PASSWORD-REDACTED>` (the literal value is
> deliberately not repeated in this document; it was purged from git history on
> 2026-06-13 — see §2).

---

## 1. Rotate `admin_passwd` and `db_password` on the LIVE system

The fresh values are already in your local `.env` and `odoo.conf`. The DB password
inside the Postgres volume still holds the OLD value, so you must ALTER the role to
match before restarting, or Odoo will fail authentication.

### 1a. Take a backup first (always)

```bash
cd /opt/ephem-deploy
bash scripts/backup_db.sh
ls -lh backups/
```

### 1b. Rotate the Postgres role password to match the new `.env`

```bash
cd /opt/ephem-deploy
NEW_DB_PASS="$(grep '^POSTGRES_PASSWORD=' .env | cut -d= -f2-)"

# Apply the new password to the live Postgres role:
docker exec -i ephem-db psql -U odoo -d postgres -v ON_ERROR_STOP=1 \
  -c "ALTER USER odoo WITH PASSWORD '${NEW_DB_PASS}';"
```

### 1c. Recreate the Odoo container so it reads the new `.env` + `odoo.conf`

`db_password` in `odoo.conf` and `POSTGRES_PASSWORD` in `.env` are already the new
value. Recreate (not just restart) so env changes take effect:

```bash
cd /opt/ephem-deploy
docker compose up -d odoo
docker compose logs --tail=30 odoo   # confirm: NO "password authentication failed"
```

The `admin_passwd` (Odoo master password) takes effect on this restart automatically —
it is read from `odoo.conf` and is not stored in the DB.

### 1d. Verify

```bash
docker compose ps
curl -sI http://localhost:8069/web/login | head -1   # expect 200/303
```

### 1e. Rotate Odoo LOGIN credentials at DEPLOY time (admin + demo users)

§1a–1d rotate the *infrastructure* secrets (Postgres role password and the Odoo
master password). The **application logins** are a separate rotation and must be done
the moment a seeded database lands on a real server:

- `admin` / `admin` — the Odoo administrator login.
- The five demo users seeded by `scripts/seed_more.py`: `amira`, `khalid`, `sara`,
  `mohammed`, `layla` — all with password `demo1234`.

Rotate all six in one shot via the Odoo shell (prints the new passwords once — store
them in a password manager immediately):

```bash
docker exec -i ephem-app odoo shell -d erpmedsupply --no-http <<'PY'
import secrets
for login in ['admin', 'amira', 'khalid', 'sara', 'mohammed', 'layla']:
    user = env['res.users'].search([('login', '=', login)])
    if user:
        new_pwd = secrets.token_urlsafe(16)
        user.password = new_pwd
        print(f"{login}: {new_pwd}")
    else:
        print(f"{login}: NOT FOUND (ok if not seeded)")
env.cr.commit()
PY
```

Alternatively, deactivate the demo users instead of rotating them if production does
not need them (Settings → Users → Archive). Verify afterwards that `admin/admin` and
`<user>/demo1234` are rejected on the login page.

---

## 2. Purge the leaked secret from git history — DONE 2026-06-13

> **STATUS: COMPLETED on 2026-06-13.** The history purge was executed with
> `git filter-repo --replace-text` (Option A below), replacing every occurrence of the
> old password with `REDACTED` across all commits. Verified clean with:
>
> ```bash
> git log --all -p | grep -c '<OLD-PASSWORD-REDACTED>'   # printed 0
> ```
>
> (substitute the literal old password — written as `<OLD-PASSWORD-REDACTED>`
> throughout this document — when re-running the check). The steps below are kept as
> the record of what was done and as the procedure for any future leak.

`odoo.conf` was committed with the old password (`<OLD-PASSWORD-REDACTED>`). Removing
it from the index (already done) does NOT remove it from past commits — history had to
be rewritten.

> **This rewrites every commit hash and requires a force-push.** Coordinate with anyone
> who has a clone — they must re-clone or hard-reset afterward. Do a mirror backup first.

### 2a. Back up the repo (so the rewrite is reversible)

```bash
cd /opt/ephem-deploy
git bundle create ../ephem-deploy-prepurge.bundle --all
# or: cp -a .git ../ephem-deploy-git-backup
```

### 2b. Option A — git-filter-repo (recommended)

Install once:

```bash
pip install git-filter-repo      # or: brew install git-filter-repo
```

Create a replacement rules file and run it:

```bash
cd /opt/ephem-deploy

cat > /tmp/secrets.txt <<'EOF'
<OLD-PASSWORD-REDACTED>==>REDACTED
EOF
# (put the literal old password before the ==>, one rule per line)

git filter-repo --replace-text /tmp/secrets.txt

# Also strip the file itself from all of history (belt and braces):
git filter-repo --path odoo.conf --invert-paths --force

rm -f /tmp/secrets.txt
```

> `git filter-repo` removes the `origin` remote by design. Re-add it before pushing:
>
> ```bash
> git remote add origin git@github.com:Wael9912/ephem_deployment_docker.git
> ```

### 2b. Option B — BFG Repo-Cleaner (alternative)

```bash
cd /opt
echo '<OLD-PASSWORD-REDACTED>' > replacements.txt   # the literal old password, one secret per line
java -jar bfg.jar --replace-text replacements.txt ephem-deploy/.git
java -jar bfg.jar --delete-files odoo.conf    ephem-deploy/.git
cd ephem-deploy
git reflog expire --expire=now --all && git gc --prune=now --aggressive
rm -f /opt/replacements.txt
```

### 2c. Verify the secret is gone, then force-push

```bash
cd /opt/ephem-deploy
git log --all -p | grep -c '<OLD-PASSWORD-REDACTED>'   # MUST print 0 (use the literal old password)
git push origin --force --all
git push origin --force --tags
```

> Even after purging history, treat the old password (`<OLD-PASSWORD-REDACTED>`) as
> permanently compromised. §1 already rotated it to a fresh value — do not reuse the
> old one anywhere.

---

## 3. Backups — install, run, and TEST a restore

### 3a. Install the schedule

Pick cron or systemd from `scripts/backup_db.cron.example`. For systemd:

```bash
# After creating the two unit files shown in backup_db.cron.example:
sudo systemctl daemon-reload
sudo systemctl enable --now ephem-backup.timer
systemctl list-timers ephem-backup.timer
```

### 3b. Run one backup now

```bash
cd /opt/ephem-deploy
bash scripts/backup_db.sh
tail -n 5 backups/backup.log
ls -lh backups/erpmedsupply_*.dump.gz | tail -1
```

### 3c. TESTED restore procedure (restore into a SCRATCH db — non-destructive)

Never test a restore by overwriting the live DB. Use a scratch target:

```bash
cd /opt/ephem-deploy
LATEST="$(ls -1t backups/erpmedsupply_*.dump.gz | head -1)"
echo "Restoring: $LATEST"

# Restore into ephem_restore_test (created/dropped automatically by the script):
bash scripts/restore_db.sh "$LATEST" --target ephem_restore_test --yes
```

Verify the scratch DB has data, then clean it up:

```bash
# Row sanity check (expect a non-zero count of installed modules):
docker exec -i ephem-db psql -U odoo -d ephem_restore_test \
  -c "SELECT count(*) AS modules FROM ir_module_module WHERE state='installed';"

# Drop the scratch DB once satisfied:
docker exec -i ephem-db psql -U odoo -d postgres \
  -c "DROP DATABASE IF EXISTS ephem_restore_test;"
```

A restore that yields a sensible module count and clean logs means your backups are
real and recoverable. Record the date you last verified this here:

```
Last verified restore: __________  by __________
```

### 3d. Off-host copies

`backups/` lives on the same host as Postgres. For disaster recovery, sync it off-box
(adjust target):

```bash
rsync -avz /opt/ephem-deploy/backups/ backup-user@offsite-host:/srv/ephem-backups/
```

---

## 4. Switch the server to the production config posture

```bash
cd /opt/ephem-deploy
cp odoo.conf.prod odoo.conf
# Re-apply your live secrets into odoo.conf (admin_passwd, db_password) — they are
# the same fresh values now in .env. Then:
docker compose up -d odoo
docker compose logs --tail=30 odoo
```

Confirm in the running config that `proxy_mode=True`, `list_db=False`, and there is
**no** `dev_mode` line.

---

## 5. Minimal addon set for production (med-supply ERP)

The med-supply ERP runs from **two dedicated, self-contained repos** — it no longer
depends on the `borse/ePHEM` platform monorepo. The production server clones exactly
these two beside `docker-compose.yml`; the base compose mounts them at
`/mnt/extra-addons` and `/mnt/nile-theme`:

Production clones are **pinned to release tags** for reproducibility — never a
moving branch. The current pinned set lives in [`DEPLOY_PINS.md`](DEPLOY_PINS.md)
(the single source of truth; bump it on each release).

| Repo | Pinned tag | Mount | Contents |
|---|---|---|---|
| [`Wael9912/erpmedsupply-addons`](https://github.com/Wael9912/erpmedsupply-addons) | `v18.0.1.0.0` | `/mnt/extra-addons` | the 14 ERP addons (below) |
| [`Wael9912/odoo-nile-theme`](https://github.com/Wael9912/odoo-nile-theme) | `v18.0.1.2.0` | `/mnt/nile-theme` | the `nile_*` theme stack |

```bash
cd /opt/ephem-deploy            # or wherever docker-compose.yml lives
# Pinned tags (see DEPLOY_PINS.md). Use --branch <tag> for a detached, reproducible checkout.
git clone -b v18.0.1.0.0 https://github.com/Wael9912/erpmedsupply-addons.git
git clone -b v18.0.1.2.0 https://github.com/Wael9912/odoo-nile-theme.git
docker compose up -d            # base compose, NO override → ERP-only topology
```

### `erpmedsupply-addons` (14 addons)

| Group | Directories |
|---|---|
| OCA bank-reconcile stack | `account_reconcile_model_oca`, `account_reconcile_oca`, `account_statement_base` |
| Odoo Mates accounting | `accounting_pdf_reports`, `om_account_accountant`, `om_account_asset`, `om_account_budget`, `om_account_daily_reports`, `om_account_followup`, `om_fiscal_year`, `om_recurring_payments` |
| OCA web UX | `web_responsive`, `web_chatter_position` |
| Local UX tweak | `ui_kanban_first` |

Dependency closure was verified: every module these depend on resolves to **core
Odoo**, one of the 14, or a `nile_*` module. Nothing reaches into `borse/ePHEM`.

### `odoo-nile-theme` — ship only these 5

`nile_core`, `nile_shell`, `nile_components`, `nile_config`, `nile_brand_medsupply`.
Do **not** ship `nile_brand_cmp` / `nile_brand_ephem` (other-product brand packs, not
installed in `erpmedsupply`).

### Decoupled from borse/ePHEM

The local `custom-addons/` checkout of `borse/ePHEM` (all `cmp_*`, `eoc_*`, `ephem_*`,
`openeducat_*`, the retired `spiffy_theme_backend` / `medsupply_ui_refresh` /
`eoc_theme_backend`, `bank-payment-18.0`, and misc `auditlog`/`dms`/`payroll`/etc.) is
**dev-only** — it is mounted exclusively by `docker-compose.override.yml` for
multi-product development. None of it ships to the ERP server.

### Re-verify before each deploy

Re-run the query above after any module install/uninstall and diff against this list;
anything new that is not a core-image module must be added to the copy set:

```bash
docker exec ephem-db psql -U odoo -d erpmedsupply -tAc \
  "SELECT name FROM ir_module_module WHERE state='installed' ORDER BY name" \
  | comm -23 - <(docker exec ephem-app ls /usr/lib/python3/dist-packages/odoo/addons | sort)
```
