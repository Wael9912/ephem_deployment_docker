#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────
#  ePHEM database backup — real pg_dump via the running Postgres container.
#
#  Produces a timestamped, gzip-compressed custom-format dump and prunes old
#  backups by retention count. Designed to be run by cron / a systemd timer.
#
#  Usage:
#    bash scripts/backup_db.sh                 # back up $DB_NAME (default ephem_uganda)
#    DB_NAME=other bash scripts/backup_db.sh   # back up a specific database
#    RETENTION=30 bash scripts/backup_db.sh    # keep the newest 30 dumps
#
#  Env overrides:
#    DB_CONTAINER  Postgres container name      (default: ephem-db)
#    DB_USER       Postgres role                (default: odoo)
#    DB_NAME       database to dump             (default: ephem_uganda)
#    BACKUP_DIR    output directory             (default: <repo>/backups)
#    RETENTION     dumps to keep per database   (default: 14)
# ──────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DB_CONTAINER="${DB_CONTAINER:-ephem-db}"
DB_USER="${DB_USER:-odoo}"
DB_NAME="${DB_NAME:-ephem_uganda}"
BACKUP_DIR="${BACKUP_DIR:-${REPO_ROOT}/backups}"
RETENTION="${RETENTION:-14}"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
OUTFILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.dump.gz"
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

# ── Retention: keep the newest ${RETENTION} dumps for THIS database ────────
log "Pruning old backups (keeping newest ${RETENTION} for '${DB_NAME}')."
mapfile -t OLD < <(ls -1t "${BACKUP_DIR}/${DB_NAME}_"*.dump.gz 2>/dev/null | tail -n +"$((RETENTION + 1))")
for f in "${OLD[@]}"; do
    [ -n "${f}" ] || continue
    rm -f "${f}"
    log "  pruned $(basename "${f}")"
done

log "Backup complete."
