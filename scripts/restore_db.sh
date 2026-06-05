#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────
#  ePHEM database restore — restores a backup_db.sh dump into Postgres.
#
#  DESTRUCTIVE: by default it DROPS and recreates the target database.
#  Always test-restore into a scratch DB name first (see --target).
#
#  Usage:
#    bash scripts/restore_db.sh <dump.gz>
#    bash scripts/restore_db.sh <dump.gz> --target ephem_restore_test
#    bash scripts/restore_db.sh <dump.gz> --yes            # skip confirmation
#
#  Env overrides (same defaults as backup_db.sh):
#    DB_CONTAINER (ephem-db)  DB_USER (odoo)  DB_NAME (ephem_uganda)
#    ODOO_CONTAINER (ephem-app) — stopped during restore so it can't reconnect.
# ──────────────────────────────────────────────────────────────────────────
set -euo pipefail

DB_CONTAINER="${DB_CONTAINER:-ephem-db}"
DB_USER="${DB_USER:-odoo}"
ODOO_CONTAINER="${ODOO_CONTAINER:-ephem-app}"

DUMP=""
TARGET="${DB_NAME:-ephem_uganda}"
ASSUME_YES="no"

while [ $# -gt 0 ]; do
    case "$1" in
        --target) TARGET="$2"; shift 2 ;;
        --yes|-y) ASSUME_YES="yes"; shift ;;
        -*) echo "Unknown option: $1" >&2; exit 2 ;;
        *) DUMP="$1"; shift ;;
    esac
done

if [ -z "${DUMP}" ] || [ ! -f "${DUMP}" ]; then
    echo "ERROR: pass a path to an existing .dump.gz file." >&2
    echo "Usage: bash scripts/restore_db.sh <dump.gz> [--target DB] [--yes]" >&2
    exit 2
fi

if ! docker ps --format '{{.Names}}' | grep -qx "${DB_CONTAINER}"; then
    echo "ERROR: container '${DB_CONTAINER}' is not running." >&2
    exit 1
fi

echo "About to restore:"
echo "  dump      : ${DUMP}"
echo "  into DB   : ${TARGET}  (will be DROPPED and recreated)"
echo "  container : ${DB_CONTAINER}"
if [ "${ASSUME_YES}" != "yes" ]; then
    read -r -p "Type the target DB name to confirm: " CONFIRM
    if [ "${CONFIRM}" != "${TARGET}" ]; then
        echo "Confirmation did not match. Aborting."
        exit 1
    fi
fi

# Stop Odoo so it releases connections to the target DB (best effort).
if docker ps --format '{{.Names}}' | grep -qx "${ODOO_CONTAINER}"; then
    echo "Stopping ${ODOO_CONTAINER} to release DB connections..."
    docker stop "${ODOO_CONTAINER}" >/dev/null
    STOPPED_ODOO="yes"
else
    STOPPED_ODOO="no"
fi

echo "Terminating remaining connections to '${TARGET}'..."
docker exec -i "${DB_CONTAINER}" psql -U "${DB_USER}" -d postgres -v ON_ERROR_STOP=1 -c \
    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${TARGET}' AND pid <> pg_backend_pid();" >/dev/null || true

echo "Dropping and recreating '${TARGET}'..."
docker exec -i "${DB_CONTAINER}" psql -U "${DB_USER}" -d postgres -v ON_ERROR_STOP=1 \
    -c "DROP DATABASE IF EXISTS \"${TARGET}\";" \
    -c "CREATE DATABASE \"${TARGET}\" OWNER \"${DB_USER}\";"

echo "Restoring dump (this can take a while)..."
# gunzip the .gz and pipe into pg_restore inside the container.
gunzip -c "${DUMP}" | docker exec -i "${DB_CONTAINER}" \
    pg_restore -U "${DB_USER}" -d "${TARGET}" --no-owner --role="${DB_USER}" --clean --if-exists

echo "Restore finished into '${TARGET}'."

if [ "${STOPPED_ODOO}" = "yes" ]; then
    echo "Restarting ${ODOO_CONTAINER}..."
    docker start "${ODOO_CONTAINER}" >/dev/null
fi

echo "Done. Verify the app loads and data is present."
