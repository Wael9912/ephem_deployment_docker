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
> | Live database      | `ephem_uganda` |
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
> sensitive; they are gitignored. The *old leaked* secret that must be purged from
> history is: `***REMOVED***`.

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

---

## 2. Purge the leaked secret from git history

`odoo.conf` was committed with the password `***REMOVED***`. Removing it from the
index (already done) does NOT remove it from past commits. You must rewrite history.

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
***REMOVED***==>REDACTED
EOF

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
echo '***REMOVED***' > replacements.txt   # one secret per line
java -jar bfg.jar --replace-text replacements.txt ephem-deploy/.git
java -jar bfg.jar --delete-files odoo.conf    ephem-deploy/.git
cd ephem-deploy
git reflog expire --expire=now --all && git gc --prune=now --aggressive
rm -f /opt/replacements.txt
```

### 2c. Verify the secret is gone, then force-push

```bash
cd /opt/ephem-deploy
git log --all -p | grep -c '***REMOVED***'   # MUST print 0
git push origin --force --all
git push origin --force --tags
```

> Even after purging history, treat `***REMOVED***` as permanently compromised.
> §1 already rotated it to a fresh value — do not reuse the old one anywhere.

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
ls -lh backups/ephem_uganda_*.dump.gz | tail -1
```

### 3c. TESTED restore procedure (restore into a SCRATCH db — non-destructive)

Never test a restore by overwriting the live DB. Use a scratch target:

```bash
cd /opt/ephem-deploy
LATEST="$(ls -1t backups/ephem_uganda_*.dump.gz | head -1)"
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
