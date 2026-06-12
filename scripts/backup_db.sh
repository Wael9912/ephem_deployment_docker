#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────
#  ePHEM database backup — pg_dump + Odoo filestore via the running containers.
#
#  Produces, per run:
#    <db>_<timestamp>.dump.gz       gzip'd custom-format pg_dump
#    <db>_filestore_<timestamp>.tgz tar of /var/lib/odoo/filestore/<db>
#  and prunes old backups of each kind by retention count. Designed to be
#  run by cron / a systemd timer.
#
#  Usage:
#    bash scripts/backup_db.sh                 # back up $DB_NAME (default erpmedsupply)
#    DB_NAME=other bash scripts/backup_db.sh   # back up a specific database
#    RETENTION=30 bash scripts/backup_db.sh    # keep the newest 30 of each artifact
#
#  Env overrides:
#    DB_CONTAINER    Postgres container name      (default: ephem-db)
#    ODOO_CONTAINER  Odoo container name          (default: ephem-app)
#    DB_USER         Postgres role                (default: odoo)
#    DB_NAME         database to dump             (default: erpmedsupply)
#    FILESTORE_ROOT  filestore root in container  (default: /var/lib/odoo/filestore)
#    BACKUP_DIR      output directory             (default: <repo>/backups)
#    RETENTION       backups to keep per database (default: 14, per artifact kind)
# ──────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DB_CONTAINER="${DB_CONTAINER:-ephem-db}"
ODOO_CONTAINER="${ODOO_CONTAINER:-ephem-app}"
DB_USER="${DB_USER:-odoo}"
DB_NAME="${DB_NAME:-erpmedsupply}"
FILESTORE_ROOT="${FILESTORE_ROOT:-/var/lib/odoo/filestore}"
BACKUP_DIR="${BACKUP_DIR:-${REPO_ROOT}/backups}"
RETENTION="${RETENTION:-14}"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
OUTFILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.dump.gz"
FSFILE="${BACKUP_DIR}/${DB_NAME}_filestore_${TIMESTAMP}.tgz"
LOGFILE="${BACKUP_DIR}/backup.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "${LOGFILE}"; }

mkdir -p "${BACKUP_DIR}"

# Verify the container is up before attempting the dump.
if ! docker ps --format '{{.Names}}' | grep -qx "${DB_CONTAINER}"; then
    log "ERROR: container '${DB_CONTAINER}' is not running. Aborting."
    exit 1
fi

log "Starting backup of '${DB_NAME}' from container '${DB_CONTAINER}'."

# pg_dump custom format (-Fc) → gzip. Custom format is compressed already but
# we gzip on top for a stable, restorable .gz artifact and consistent naming.
# Stream the dump out of the container; never write secrets to disk here.
if docker exec -i "${DB_CONTAINER}" \
        pg_dump -U "${DB_USER}" -Fc "${DB_NAME}" 2>>"${LOGFILE}" \
        | gzip > "${OUTFILE}"; then
    SIZE="$(du -h "${OUTFILE}" | cut -f1)"
    log "OK: wrote ${OUTFILE} (${SIZE})."
else
    log "ERROR: pg_dump failed. Removing partial file ${OUTFILE}."
    rm -f "${OUTFILE}"
    exit 1
fi

# Integrity sanity check: the gzip must be valid.
if ! gzip -t "${OUTFILE}" 2>>"${LOGFILE}"; then
    log "ERROR: ${OUTFILE} failed gzip integrity test. Removing."
    rm -f "${OUTFILE}"
    exit 1
fi

# ── Filestore backup: tar /var/lib/odoo/filestore/<db> from the Odoo app ───
if ! docker ps --format '{{.Names}}' | grep -qx "${ODOO_CONTAINER}"; then
    log "ERROR: container '${ODOO_CONTAINER}' is not running. Aborting filestore backup."
    exit 1
fi

if ! docker exec "${ODOO_CONTAINER}" test -d "${FILESTORE_ROOT}/${DB_NAME}"; then
    log "ERROR: no filestore at ${FILESTORE_ROOT}/${DB_NAME} in '${ODOO_CONTAINER}'. Aborting."
    exit 1
fi

log "Starting filestore backup of '${DB_NAME}' from container '${ODOO_CONTAINER}'."
if docker exec "${ODOO_CONTAINER}" \
        tar -czf - -C "${FILESTORE_ROOT}" "${DB_NAME}" 2>>"${LOGFILE}" \
        > "${FSFILE}"; then
    SIZE="$(du -h "${FSFILE}" | cut -f1)"
    log "OK: wrote ${FSFILE} (${SIZE})."
else
    log "ERROR: filestore tar failed. Removing partial file ${FSFILE}."
    rm -f "${FSFILE}"
    exit 1
fi

# Integrity sanity check: the tgz must be valid.
if ! gzip -t "${FSFILE}" 2>>"${LOGFILE}"; then
    log "ERROR: ${FSFILE} failed gzip integrity test. Removing."
    rm -f "${FSFILE}"
    exit 1
fi

# ── Retention: keep the newest ${RETENTION} of each artifact for THIS DB ───
log "Pruning old backups (keeping newest ${RETENTION} per kind for '${DB_NAME}')."
mapfile -t OLD < <(ls -1t "${BACKUP_DIR}/${DB_NAME}_"[0-9]*.dump.gz 2>/dev/null | tail -n +"$((RETENTION + 1))")
for f in "${OLD[@]}"; do
    [ -n "${f}" ] || continue
    rm -f "${f}"
    log "  pruned $(basename "${f}")"
done
mapfile -t OLD_FS < <(ls -1t "${BACKUP_DIR}/${DB_NAME}_filestore_"[0-9]*.tgz 2>/dev/null | tail -n +"$((RETENTION + 1))")
for f in "${OLD_FS[@]}"; do
    [ -n "${f}" ] || continue
    rm -f "${f}"
    log "  pruned $(basename "${f}")"
done

log "Backup complete."
