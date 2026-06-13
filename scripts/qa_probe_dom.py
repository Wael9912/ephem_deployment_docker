# -*- coding: utf-8 -*-
"""Dump the exact DOM/class names of the surfaces the refinement touches, so the
SCSS selectors are right first time. Read-only. Usage: python3 scripts/qa_probe_dom.py [db]"""
import sys, xmlrpc.client
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8069"
DB = sys.argv[1] if len(sys.argv) > 1 else "erpmedsupply"
USER, PWD = "admin", "admin"

common = xmlrpc.client.ServerProxy(f"{BASE}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f"{BASE}/xmlrpc/2/object")
models.execute_kw(DB, uid, PWD, "res.users", "write", [[uid], {"lang": "en_US"}])

def dump(page, sel, label, outer=True, n=1):
    print(f"\n===== {label}  ({sel}) =====")
    js = """(args) => {
      const [sel, outer, n] = args;
      const els = [...document.querySelectorAll(sel)].slice(0, n);
      if (!els.length) return 'NO MATCH';
      return els.map(e => (outer ? e.outerHTML : e.innerHTML)).join('\\n--\\n');
    }"""
    try:
        html = page.evaluate(js, [sel, outer, n])
        print(html[:2200] if isinstance(html, str) else html)
    except Exception as e:
        print("ERR", str(e)[:160])

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_context(viewport={"width": 1440, "height": 900}).new_page()
    page.goto(f"{BASE}/web/login?db={DB}")
    if page.locator("input[name=login]").count():
        page.fill("input[name=login]", USER); page.fill("input[name=password]", PWD)
        page.click("button[type=submit]")
    page.wait_for_selector(".o_main_navbar", timeout=20000); page.wait_for_timeout(1200)

    # --- grouped kanban header (count placement) ---
    page.goto(f"{BASE}/odoo/action-sale.action_orders")
    page.wait_for_selector(".o_kanban_grouped", timeout=15000); page.wait_for_timeout(1400)
    dump(page, ".o_kanban_group .o_kanban_header", "KANBAN HEADER (with records)", n=2)
    dump(page, ".o_kanban_counter", "KANBAN COUNTER", n=2)
    # view switcher
    dump(page, ".o_cp_switch_buttons", "VIEW SWITCHER", n=1)

    # --- sale form: statusbar + notebook ---
    page.goto(f"{BASE}/odoo/action-sale.action_orders/1")
    page.wait_for_selector(".o_form_view", timeout=15000); page.wait_for_timeout(1400)
    dump(page, ".o_form_statusbar", "STATUSBAR", n=1)
    dump(page, ".o_notebook .nav-tabs", "NOTEBOOK NAV", n=1)
    dump(page, ".o-form-buttonbox .oe_stat_button", "STAT BUTTON", n=1)

    # --- settings rail ---
    page.goto(f"{BASE}/odoo/action-base_setup.action_general_configuration")
    page.wait_for_selector(".o_form_view, .settings", timeout=15000); page.wait_for_timeout(1600)
    dump(page, ".settings_tab", "SETTINGS RAIL CONTAINER", outer=False, n=1)
    dump(page, ".settings_tab .selected, .settings_tab .tab.selected, .o_setting_tab.selected", "SETTINGS ACTIVE TAB", n=1)

    models.execute_kw(DB, uid, PWD, "res.users", "write", [[uid], {"lang": "ar_001"}])
    b.close()
    print("\n(restored lang=ar_001)")
