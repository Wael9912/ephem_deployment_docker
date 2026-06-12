#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Post-uninstall verification that Spiffy's public attack surface is gone
(CUSTOM_THEME_PLAN.md §7 — verification, not assumption). Run in CI and in the
deploy runbook after any theme change.

Two checks:
 1. HTTP smoke — every route from the Spiffy inventory
    (docs/theme-audit/SPIFFY_AUDIT.md §4) must answer 404. Anything else
    (405/400/500…) means the path still routes somewhere.
 2. Registry enumeration — list every auth='public' / auth='none' route still
    registered DB-wide (via docker exec odoo shell), so new public surface
    can't sneak in unnoticed. Known-core routes are whitelisted; the rest are
    printed for review and fail the run unless --warn-only.

Usage:
    python3 scripts/check_public_endpoints.py [--base http://localhost:8069]
        [--db erpmedsupply] [--container ephem-app] [--warn-only] [--no-enum]
"""
import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request

# Spiffy route inventory — SPIFFY_AUDIT.md §4 (public, user, none; all must 404
# once spiffy_theme_backend is uninstalled).
SPIFFY_ROUTES = [
    "/color/pallet/", "/color/pallet/data/", "/get/model/record",
    "/get-favorite-apps", "/get/active/menu", "/get/appsearch/data",
    "/get/tab/title/", "/get/active/lang", "/change/active/lang",
    "/update-user-fav-apps", "/remove-user-fav-apps", "/active/dark/mode",
    "/get/dark/mode/data", "/update/bookmark/panel/show",
    "/sidebar/behavior/update", "/get/bookmark/link", "/add/bookmark/link",
    "/update/bookmark/link", "/remove/bookmark/link",
    "/update/chatter/position", "/get/mutli/tab", "/add/mutli/tab",
    "/remove/multi/tab", "/update/tab/details", "/get/attachment/data",
    "/get/irmenu/icondata", "/show/user/todo/list/", "/create/todo",
    "/delete/todo", "/get/records/global/search", "/update/split/view",
    "/update/filter/row", "/filter/relational/field/list",
    "/filter/relational/field/data", "/selection/filter/list",
    "/text_color/label_color", "/attach/get_data", "/app/attachment/upload",
    "/theme_color/parameter_check", "/add/google/font", "/delete/google/font",
    "/update_single_font_selection", "/service_worker.js", "/pwa/enabled",
    "/pwa/offline", "/spiffy_theme_backend/1/manifest.json",
]

# Core/public routes that are expected and acceptable on a plain Odoo 18
# Community + Nile stack (verified against erpmedsupply_nile 2026-06-12).
# Prefix match. Anything NEW outside this list — a vendored addon shipping
# auth='public' surface like Spiffy did, or the eoc_* endpoints on ePHEM
# instances — gets flagged for review.
ENUM_WHITELIST_EXACT = {"/", "/robots.txt"}
ENUM_WHITELIST_PREFIXES = (
    # webclient plumbing ("/web" also covers /websocket, /web_editor,
    # /web_unsplash — all core on this stack)
    "/web", "/odoo", "/scoped_app",
    # RPC + realtime (core)
    "/xmlrpc", "/jsonrpc", "/bus/",
    # mail/discuss public surface (tokens required server-side)
    "/mail/", "/chat/", "/discuss/",
    # core modules present on the ERP stack
    "/base_import_module/login_upload",
    "/dashboard/", "/spreadsheet/", "/calendar/", "/payment/",
    "/report/download", "/base_setup/", "/portal/", "/my",
    "/digest/", "/html_editor/", "/invoice/transaction", "/logo",
    "/meet/", "/report/barcode", "/sms/status", "/terms",
)

# The smoke list in part 1 is the precise gate; part 2 is a tripwire for new
# public surface, which (as the Spiffy inventory shows) tends to mount outside
# the core prefixes.

ENUM_SNIPPET = r"""
import json
rmap = env['ir.http'].routing_map()
out = []
for rule in rmap.iter_rules():
    routing = getattr(rule.endpoint, 'routing', {})
    auth = routing.get('auth')
    if auth in ('public', 'none'):
        out.append({'rule': str(rule.rule), 'auth': auth,
                    'methods': sorted(m for m in (rule.methods or [])
                                      if m not in ('HEAD', 'OPTIONS'))})
print('ENUM_JSON_START')
print(json.dumps(sorted(out, key=lambda r: r['rule'])))
print('ENUM_JSON_END')
"""


def http_status(base, path, db):
    url = f"{base}{path}"
    req = urllib.request.Request(url, headers={"Cookie": f"frontend_lang=en_US"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return f"ERR {e}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:8069")
    ap.add_argument("--db", default="erpmedsupply")
    ap.add_argument("--container", default="ephem-app")
    ap.add_argument("--warn-only", action="store_true")
    ap.add_argument("--no-enum", action="store_true",
                    help="skip the docker-exec registry enumeration")
    args = ap.parse_args()

    failures = 0

    print(f"== 1. Spiffy route smoke ({len(SPIFFY_ROUTES)} routes, expect 404) ==")
    for path in SPIFFY_ROUTES:
        status = http_status(args.base, path, args.db)
        ok = status == 404
        if not ok:
            failures += 1
        print(f"  {'OK  ' if ok else 'FAIL'} {status:>4}  {path}")

    if not args.no_enum:
        print("\n== 2. Remaining auth=public/none routes (registry) ==")
        cmd = ["docker", "exec", "-i", args.container, "odoo", "shell",
               "-c", "/etc/odoo/odoo.conf", "-d", args.db,
               "--http-port=8079", "--gevent-port=8080", "--log-level=critical"]
        proc = subprocess.run(cmd, input=ENUM_SNIPPET, capture_output=True,
                              text=True, timeout=300)
        raw = proc.stdout
        try:
            payload = raw.split("ENUM_JSON_START")[1].split("ENUM_JSON_END")[0]
            routes = json.loads(payload.strip())
        except (IndexError, json.JSONDecodeError):
            print("  ERROR: could not enumerate routes")
            print(proc.stderr[-2000:])
            sys.exit(2)
        flagged = [r for r in routes
                   if r["rule"] not in ENUM_WHITELIST_EXACT
                   and not r["rule"].startswith(ENUM_WHITELIST_PREFIXES)]
        print(f"  total public/none routes: {len(routes)}, "
              f"outside whitelist: {len(flagged)}")
        for r in flagged:
            print(f"  REVIEW {r['auth']:<6} {','.join(r['methods']) or 'GET':<9} {r['rule']}")
        failures += len(flagged)

    print(f"\n{'PASS' if failures == 0 else 'FAIL'} ({failures} finding(s))")
    if failures and not args.warn_only:
        sys.exit(1)


if __name__ == "__main__":
    main()
