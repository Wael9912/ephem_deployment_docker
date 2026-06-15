#!/bin/bash
# ──────────────────────────────────────────────────────────────────────────
# ePHEM — New Tenant (Customer) Provisioner
#
# One command to bring a new medical-supply customer to life on the shared
# stack: creates their database, installs the production module set, obtains
# the SSL certificate for their subdomain, and wires up per-subdomain routing.
#
# Model: one database + one subdomain per customer on the shared Odoo stack.
#   acme.yourdomain.com  ->  database "acme"   (routed by dbfilter = ^%d$)
#   beta.yourdomain.com  ->  database "beta"
# Each customer's data is fully isolated in its own database and filestore.
# (For full container-level isolation per customer, run a separate stack per
#  tenant — see docs/Hosting_Guide_DigitalOcean_vs_Hetzner.pdf.)
#
# Usage:
#   ./scripts/new-tenant.sh SLUG DOMAIN EMAIL [options]
#
# Arguments:
#   SLUG     Database name = first label of the subdomain (e.g. "acme")
#   DOMAIN   Full subdomain pointing at this server (e.g. acme.yourdomain.com)
#   EMAIL    Admin email for the Let's Encrypt certificate
#
# Options:
#   --from-template DB   Clone an existing (pre-configured) database instead of
#                        a fresh install. Great for a "golden" template tenant.
#   --modules "a,b,c"    Override the module set installed on a fresh database.
#   --no-ssl             Skip the certificate step (e.g. behind Cloudflare).
#   --yes                Don't prompt for confirmation.
#
# Examples:
#   ./scripts/new-tenant.sh acme acme.yourdomain.com admin@yourdomain.com
#   ./scripts/new-tenant.sh beta beta.yourdomain.com admin@yourdomain.com --from-template template
# ──────────────────────────────────────────────────────────────────────────

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE="docker compose -f $SCRIPT_DIR/docker-compose.yml"
ODOO_CONF="$SCRIPT_DIR/odoo.conf"

# Production module set for a medical-supply customer (see PRODUCTION_HARDENING_RUNBOOK.md §5).
DEFAULT_MODULES="contacts,stock,purchase,sale_management,account,product_expiry,stock_landed_costs,om_account_accountant,accounting_pdf_reports,account_reconcile_oca,web_responsive,web_chatter_position,nile_theme,nile_brand_medsupply"

# ── Parse arguments ────────────────────────────────────────────────────────
if [ $# -lt 3 ]; then
    sed -n '2,40p' "$0" | sed 's/^# \{0,1\}//'
    exit 1
fi

SLUG="$1"; DOMAIN="$2"; EMAIL="$3"; shift 3
TEMPLATE=""; MODULES="$DEFAULT_MODULES"; DO_SSL=1; ASSUME_YES=0

while [ $# -gt 0 ]; do
    case "$1" in
        --from-template) TEMPLATE="$2"; shift 2 ;;
        --modules)       MODULES="$2";  shift 2 ;;
        --no-ssl)        DO_SSL=0;       shift ;;
        --yes)           ASSUME_YES=1;   shift ;;
        *) echo -e "${RED}Unknown option: $1${NC}"; exit 1 ;;
    esac
done

# ── Validate ───────────────────────────────────────────────────────────────
if ! echo "$SLUG" | grep -qE '^[a-z0-9_]+$'; then
    echo -e "${RED}✗ SLUG must be lowercase letters, digits, or underscores (got '$SLUG').${NC}"
    echo "  It must match the first label of the domain so routing works."
    exit 1
fi

EXPECTED_LABEL="${DOMAIN%%.*}"
if [ "$SLUG" != "$EXPECTED_LABEL" ]; then
    echo -e "${YELLOW}! Heads up:${NC} SLUG ('$SLUG') is not the first label of DOMAIN ('$EXPECTED_LABEL')."
    echo "  With dbfilter = ^%d\$, the subdomain decides the database, so '$DOMAIN'"
    echo "  will look for a database named '$EXPECTED_LABEL', not '$SLUG'."
    [ "$ASSUME_YES" -eq 1 ] || { read -p "  Continue anyway? (y/n) " -n1 -r; echo; [[ $REPLY =~ ^[Yy]$ ]] || exit 1; }
fi

echo ""
echo "========================================="
echo "  ePHEM — Provision New Tenant"
echo "========================================="
echo ""
echo -e "  Customer DB : ${BLUE}$SLUG${NC}"
echo -e "  Domain      : ${BLUE}$DOMAIN${NC}"
echo -e "  SSL email   : $EMAIL"
if [ -n "$TEMPLATE" ]; then
    echo -e "  Source      : clone of '${BLUE}$TEMPLATE${NC}'"
else
    echo -e "  Modules     : $MODULES"
fi
echo -e "  SSL         : $([ "$DO_SSL" -eq 1 ] && echo enabled || echo skipped)"
echo ""
[ "$ASSUME_YES" -eq 1 ] || { read -p "Proceed? (y/n) " -n1 -r; echo; [[ $REPLY =~ ^[Yy]$ ]] || { echo "Aborted."; exit 1; }; }

# ── Pre-flight: stack must be up ───────────────────────────────────────────
if ! $COMPOSE ps db --format '{{.Status}}' 2>/dev/null | grep -qi up; then
    echo -e "${RED}✗ The database container isn't running. Start the stack first: docker compose up -d${NC}"
    exit 1
fi

# ── Guard: refuse if the database already exists ───────────────────────────
DB_EXISTS=$($COMPOSE exec -T db psql -U odoo -d postgres -tAc \
    "SELECT 1 FROM pg_database WHERE datname = '$SLUG';" 2>/dev/null | tr -d '\r')
if [ "$DB_EXISTS" = "1" ]; then
    echo -e "${RED}✗ Database '$SLUG' already exists.${NC} Pick another slug, or drop it first."
    exit 1
fi

# ── Step 1: create the database ────────────────────────────────────────────
echo ""
if [ -n "$TEMPLATE" ]; then
    echo "==> Cloning database '$TEMPLATE' -> '$SLUG'..."
    SRC_EXISTS=$($COMPOSE exec -T db psql -U odoo -d postgres -tAc \
        "SELECT 1 FROM pg_database WHERE datname = '$TEMPLATE';" 2>/dev/null | tr -d '\r')
    if [ "$SRC_EXISTS" != "1" ]; then
        echo -e "${RED}✗ Template database '$TEMPLATE' does not exist.${NC}"; exit 1
    fi
    # Disconnect users from the template so it can be used as a CREATE TEMPLATE.
    $COMPOSE exec -T db psql -U odoo -d postgres -c \
        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='$TEMPLATE' AND pid<>pg_backend_pid();" >/dev/null 2>&1 || true
    $COMPOSE exec -T db psql -U odoo -d postgres -c \
        "CREATE DATABASE \"$SLUG\" WITH TEMPLATE \"$TEMPLATE\" OWNER odoo;" >/dev/null
    # Copy the template's filestore.
    FS="/var/lib/odoo/.local/share/Odoo/filestore"
    $COMPOSE exec -T odoo sh -c \
        "[ -d $FS/$TEMPLATE ] && { rm -rf $FS/$SLUG; cp -a $FS/$TEMPLATE $FS/$SLUG; } || true" 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Database cloned."
else
    echo "==> Creating database '$SLUG' and installing modules (this takes a few minutes)..."
    # --stop-after-init creates + initialises the DB regardless of dbfilter (dbfilter only
    # affects HTTP routing). A one-off container keeps the live workers untouched.
    $COMPOSE run --rm odoo odoo \
        -d "$SLUG" -i "$MODULES" \
        --without-demo=all --load-language=ar_001 \
        --stop-after-init
    echo -e "${GREEN}✓${NC} Database created and modules installed."
fi

# ── Step 2: per-subdomain routing (dbfilter = ^%d$) ────────────────────────
echo ""
echo "==> Checking routing config..."
if [ -f "$ODOO_CONF" ] && grep -qE '^\s*dbfilter\s*=\s*\^%d\$' "$ODOO_CONF"; then
    echo -e "${GREEN}✓${NC} dbfilter already = ^%d\$ (subdomain -> database). No change needed."
else
    echo -e "${YELLOW}!${NC} For multi-customer routing, dbfilter must be ^%d\$ (each subdomain"
    echo "  maps to the database of the same name) and list_db must be False."
    if [ "$ASSUME_YES" -eq 1 ] || { read -p "  Update odoo.conf and restart Odoo now? (y/n) " -n1 -r; echo; [[ $REPLY =~ ^[Yy]$ ]]; }; then
        cp "$ODOO_CONF" "$ODOO_CONF.bak.$(date +%Y%m%d%H%M%S)"
        if grep -qE '^\s*dbfilter\s*=' "$ODOO_CONF"; then
            sed -i.tmp -E 's|^\s*dbfilter\s*=.*|dbfilter = ^%d$|' "$ODOO_CONF"
        else
            printf '\ndbfilter = ^%%d$\n' >> "$ODOO_CONF"
        fi
        if grep -qE '^\s*list_db\s*=' "$ODOO_CONF"; then
            sed -i.tmp -E 's|^\s*list_db\s*=.*|list_db = False|' "$ODOO_CONF"
        else
            printf 'list_db = False\n' >> "$ODOO_CONF"
        fi
        rm -f "$ODOO_CONF.tmp"
        $COMPOSE restart odoo
        echo -e "${GREEN}✓${NC} Routing updated (backup saved as odoo.conf.bak.*), Odoo restarted."
    else
        echo -e "${YELLOW}  Skipped — set dbfilter = ^%d\$ yourself before the customer can log in.${NC}"
    fi
fi

# ── Step 3: SSL certificate for the new subdomain ──────────────────────────
if [ "$DO_SSL" -eq 1 ]; then
    echo ""
    echo "==> Requesting/expanding SSL certificate for $DOMAIN..."
    echo -e "${YELLOW}  (Make sure $DOMAIN already points to this server's IP.)${NC}"
    if [ -x "$SCRIPT_DIR/scripts/add-domain.sh" ]; then
        bash "$SCRIPT_DIR/scripts/add-domain.sh" "$DOMAIN" || \
            echo -e "${YELLOW}! add-domain.sh failed — run scripts/ssl-setup.sh manually.${NC}"
    else
        bash "$SCRIPT_DIR/scripts/ssl-setup.sh" "$DOMAIN" "$EMAIL" || \
            echo -e "${YELLOW}! SSL step failed — check DNS, then re-run scripts/ssl-setup.sh.${NC}"
    fi
fi

# ── Done ───────────────────────────────────────────────────────────────────
echo ""
echo "========================================="
echo -e "${GREEN}✓ Tenant '$SLUG' is provisioned.${NC}"
echo ""
echo "  URL          : https://$DOMAIN"
echo "  Database     : $SLUG"
echo "  Default login: admin  (set a strong password on first login)"
echo ""
echo "Next — finish onboarding using the checklist:"
echo "  docs/Customer_Onboarding_Checklist.pdf"
echo ""
echo "Don't forget to schedule nightly backups for this database:"
echo "  DB_NAME=$SLUG bash scripts/backup_db.sh"
echo "========================================="
echo ""
