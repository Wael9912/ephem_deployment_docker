# -*- coding: utf-8 -*-
"""Phase-3 dark-skin QA sweep.

Captures the main backend views across {light, dark} x {en_US, ar_001} and runs
automated checks:
  * horizontal overflow / broken images / JS errors / Alexandria font (as the
    light sweep does), plus
  * a DARK-MODE LUMINANCE PROBE: for key surfaces, compute the relative
    luminance of the resolved background-color and flag any that are still
    "light" (lum > 0.5) while dark mode is active — i.e. core chrome the dark
    skin missed. This is the gap-finder for the visual pass.

Dark mode is driven by the `color_scheme=dark` cookie (read server-side by
web.webclient_bootstrap to pick web.assets_web_dark) plus the matching
res.users.nile_dark_mode pref so the theme service doesn't reload mid-capture.

Usage: python3 scripts/qa_dark_sweep.py [db]
"""
import os
import sys
import xmlrpc.client
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8069"
DB = sys.argv[1] if len(sys.argv) > 1 else "erpmedsupply"
USER, PWD = "admin", "admin"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "theme-audit", "qa", "dark-sweep")

SHOTS = [
    ("inventory_overview", "/odoo/inventory", ".o_kanban_view, .o_content"),
    ("products_kanban", "/odoo/action-stock.product_template_action_product", ".o_kanban_view"),
    ("sale_orders_list", "/odoo/action-sale.action_orders", ".o_list_view, .o_kanban_view"),
    ("sale_order_form", "/odoo/action-sale.action_orders/1", ".o_form_view"),
    ("invoices", "/odoo/action-account.action_move_out_invoice_type", ".o_list_view, .o_kanban_view"),
    ("settings", "/odoo/action-base_setup.action_general_configuration", ".o_form_view, .settings"),
    ("partners_kanban", "/odoo/action-base.action_partner_form", ".o_kanban_view, .o_list_view"),
]

CHECKS = """() => {
  const out = {};
  out.hOverflow = document.documentElement.scrollWidth - document.documentElement.clientWidth;
  out.brokenImgs = [...document.images].filter(i => i.complete && i.naturalWidth === 0 && i.src && !i.src.startsWith('data:')).map(i => i.src.slice(0, 120));
  const cs = getComputedStyle(document.body);
  out.font = cs.fontFamily.split(',')[0];
  return out;
}"""

# Resolve a color string to relative luminance; flag light surfaces in dark mode.
PROBE = """(selectors) => {
  function lum(str) {
    const m = (str || '').match(/[\\d.]+/g);
    if (!m || m.length < 3) return null;
    let [r, g, b, a] = m.map(Number);
    if (a !== undefined && a === 0) return null; // transparent: inherits, skip
    [r, g, b] = [r, g, b].map(v => { v /= 255; return v <= 0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); });
    return 0.2126*r + 0.7152*g + 0.0722*b;
  }
  const res = {};
  for (const sel of selectors) {
    const el = [...document.querySelectorAll(sel)].find(e => e.offsetParent !== null);
    if (!el) continue;
    const cs = getComputedStyle(el);
    res[sel] = { bg: cs.backgroundColor, bgLum: lum(cs.backgroundColor), color: cs.color, colorLum: lum(cs.color) };
  }
  return res;
}"""

# Surfaces that MUST be dark when dark mode is on.
DARK_SURFACES = [
    ".o_web_client", ".o_control_panel", ".o_searchview",
    ".o_list_table thead th", ".o_form_sheet", ".o_notebook .nav-tabs",
    ".o_data_row > .o_data_cell", ".o_kanban_renderer", ".o_setting_box",
    ".o-mail-Composer-input", ".o_searchview_facet",
    ".o_kanban_record", ".o_kanban_record .o_kanban_record_title",
    ".o-mail-ChatterContainer", ".settings", ".o_arrow_button",
    ".o_tag.o_tag_color_0", ".btn-secondary", ".o_list_actions_header",
]


def set_admin_prefs(lang, dark):
    common = xmlrpc.client.ServerProxy(f"{BASE}/xmlrpc/2/common")
    uid = common.authenticate(DB, USER, PWD, {})
    models = xmlrpc.client.ServerProxy(f"{BASE}/xmlrpc/2/object")
    models.execute_kw(DB, uid, PWD, "res.users", "write",
                      [[uid], {"lang": lang, "nile_dark_mode": dark}])


def sweep(ctx, lang, scheme):
    out = os.path.join(OUT, scheme, lang)
    os.makedirs(out, exist_ok=True)
    findings, errors = [], []
    page = ctx.new_page()
    page.on("pageerror", lambda e: errors.append(f"[{scheme}/{lang}] {str(e)[:200]}"))
    page.on("console", lambda m: errors.append(f"[{scheme}/{lang} console] {m.text[:160]}") if m.type == "error" else None)

    page.goto(f"{BASE}/web/login?db={DB}")
    if page.locator("input[name=login]").count():
        page.fill("input[name=login]", USER)
        page.fill("input[name=password]", PWD)
        page.click("button[type=submit]")
    page.wait_for_selector(".o_main_navbar", timeout=20000)
    page.wait_for_timeout(1500)

    for name, path, sel in SHOTS:
        try:
            page.goto(f"{BASE}{path}")
            if sel:
                page.wait_for_selector(sel, timeout=20000)
            page.wait_for_timeout(1600)
            checks = page.evaluate(CHECKS)
            if checks["hOverflow"] > 2:
                findings.append(f"[{scheme}/{lang}] {name}: h-overflow {checks['hOverflow']}px")
            if checks["brokenImgs"]:
                findings.append(f"[{scheme}/{lang}] {name}: broken imgs {checks['brokenImgs']}")
            if "Alexandria" not in checks["font"]:
                findings.append(f"[{scheme}/{lang}] {name}: font fallback {checks['font']}")
            if scheme == "dark":
                probe = page.evaluate(PROBE, DARK_SURFACES)
                for s, v in probe.items():
                    if v["bgLum"] is not None and v["bgLum"] > 0.5:
                        findings.append(f"[dark/{lang}] {name}: LIGHT surface '{s}' bg={v['bg']} lum={v['bgLum']:.2f}")
                    if v["colorLum"] is not None and v["bgLum"] is not None and abs(v["colorLum"] - v["bgLum"]) < 0.15:
                        findings.append(f"[dark/{lang}] {name}: LOW-CONTRAST '{s}' text~bg ({v['color']} on {v['bg']})")
            page.screenshot(path=os.path.join(out, f"{name}.png"), full_page=False)
        except Exception as e:
            findings.append(f"[{scheme}/{lang}] {name}: NAV FAIL {str(e)[:160]}")
    page.close()
    return findings, errors


with sync_playwright() as p:
    b = p.chromium.launch()
    all_findings, all_errors = [], []
    for scheme in ("light", "dark"):
        for lang in ("en_US", "ar_001"):
            set_admin_prefs(lang, scheme == "dark")
            ctx = b.new_context(viewport={"width": 1440, "height": 900})
            if scheme == "dark":
                ctx.add_cookies([{"name": "color_scheme", "value": "dark", "url": BASE}])
            f, e = sweep(ctx, lang, scheme)
            all_findings += f
            all_errors += e
            ctx.close()
    b.close()
    set_admin_prefs("ar_001", False)  # restore live-demo default (AR, light)

    print("=== FINDINGS ===")
    for f in all_findings or ["none"]:
        print(" *", f)
    print("=== JS ERRORS ===")
    for e in dict.fromkeys(all_errors) or ["none"]:
        print(" *", e)
