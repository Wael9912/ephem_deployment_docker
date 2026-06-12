# -*- coding: utf-8 -*-
"""Visual QA sweep: full-page shots EN+AR across the demo's main views,
plus automated checks (horizontal overflow, broken images, JS errors).

Switches admin lang via XML-RPC (ORM => caches invalidate properly).
Usage: python3 scripts/qa_visual_sweep.py [db]
"""
import os
import sys
import xmlrpc.client
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8069"
DB = sys.argv[1] if len(sys.argv) > 1 else "erpmedsupply"
USER, PWD = "admin", "admin"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "theme-audit", "qa", "sweep")

SHOTS = [
    ("login", "/web/login", None),
    ("inventory_overview", "/odoo/inventory", ".o_kanban_view, .o_content"),
    ("products_kanban", "/odoo/action-stock.product_template_action_product", ".o_kanban_view"),
    ("sale_orders_list", "/odoo/action-sale.action_orders", ".o_list_view"),
    ("sale_order_form", "/odoo/action-sale.action_orders/1", ".o_form_view"),
    ("purchase_list", "/odoo/action-purchase.purchase_rfq", ".o_list_view, .o_kanban_view"),
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
  out.fontSize = cs.fontSize;
  return out;
}"""


def set_admin_lang(lang):
    common = xmlrpc.client.ServerProxy(f"{BASE}/xmlrpc/2/common")
    uid = common.authenticate(DB, USER, PWD, {})
    models = xmlrpc.client.ServerProxy(f"{BASE}/xmlrpc/2/object")
    models.execute_kw(DB, uid, PWD, "res.users", "write", [[uid], {"lang": lang}])


def sweep(page, lang):
    out = os.path.join(OUT, lang)
    os.makedirs(out, exist_ok=True)
    findings = []
    errors = []
    page.on("pageerror", lambda e: errors.append(f"[{lang}] {str(e)[:200]}"))
    page.on("console", lambda m: errors.append(f"[{lang} console] {m.text[:200]}") if m.type == "error" else None)

    page.goto(f"{BASE}/web/login?db={DB}")
    if page.locator("input[name=login]").count():
        page.fill("input[name=login]", USER)
        page.fill("input[name=password]", PWD)
        page.click("button[type=submit]")
    page.wait_for_selector(".o_main_navbar", timeout=20000)
    page.wait_for_timeout(1500)

    for name, path, sel in SHOTS:
        try:
            if name == "login":
                # capture login from a fresh anonymous context at the end instead
                continue
            page.goto(f"{BASE}{path}")
            if sel:
                page.wait_for_selector(sel, timeout=20000)
            page.wait_for_timeout(1600)
            checks = page.evaluate(CHECKS)
            if checks["hOverflow"] > 2:
                findings.append(f"[{lang}] {name}: horizontal overflow {checks['hOverflow']}px")
            if checks["brokenImgs"]:
                findings.append(f"[{lang}] {name}: broken imgs {checks['brokenImgs']}")
            if "Alexandria" not in checks["font"]:
                findings.append(f"[{lang}] {name}: font fallback active: {checks['font']}")
            page.screenshot(path=os.path.join(out, f"{name}.png"), full_page=False)
        except Exception as e:
            findings.append(f"[{lang}] {name}: NAV FAIL {str(e)[:160]}")
    return findings, errors


with sync_playwright() as p:
    b = p.chromium.launch()
    all_findings, all_errors = [], []
    for lang in ("en_US", "ar_001"):
        set_admin_lang(lang)
        ctx = b.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        f, e = sweep(page, lang)
        all_findings += f
        all_errors += e
        ctx.close()

    # anonymous login page
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()
    page.goto(f"{BASE}/web/login?db={DB}")
    page.wait_for_timeout(1500)
    os.makedirs(os.path.join(OUT, "anon"), exist_ok=True)
    page.screenshot(path=os.path.join(OUT, "anon", "login.png"))
    checks = page.evaluate(CHECKS)
    if checks["brokenImgs"]:
        all_findings.append(f"[anon] login: broken imgs {checks['brokenImgs']}")
    ctx.close()
    b.close()

    # restore admin to Arabic (live demo default)
    set_admin_lang("ar_001")

    print("=== FINDINGS ===")
    for f in all_findings or ["none"]:
        print(" *", f)
    print("=== JS ERRORS ===")
    for e in dict.fromkeys(all_errors) or ["none"]:
        print(" *", e)
