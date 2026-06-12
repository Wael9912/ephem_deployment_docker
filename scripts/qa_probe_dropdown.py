# -*- coding: utf-8 -*-
"""QA probe: reproduce the dropdown mis-positioning bug on the live nile DB.

Logs console errors, opens several dropdowns, reports their bounding rects.
Usage: python3 scripts/qa_probe_dropdown.py [db]
"""
import json
import os
import sys
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8069"
DB = sys.argv[1] if len(sys.argv) > 1 else "erpmedsupply"
USER, PWD = "admin", "admin"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "theme-audit", "qa", "img")
os.makedirs(OUT, exist_ok=True)

console_msgs = []
page_errors = []


def login(page):
    page.goto(f"{BASE}/web/login?db={DB}")
    page.fill("input[name=login]", USER)
    page.fill("input[name=password]", PWD)
    page.click("button[type=submit]")
    page.wait_for_selector(".o_main_navbar", timeout=20000)
    page.wait_for_timeout(1500)


def probe_dropdown(page, label, toggle_sel, menu_sel=".o-dropdown--menu"):
    """Click toggle, report menu rect vs toggle rect."""
    try:
        toggle = page.locator(toggle_sel).first
        toggle.wait_for(state="visible", timeout=8000)
        trect = toggle.bounding_box()
        toggle.click()
        page.wait_for_timeout(800)
        menu = page.locator(menu_sel).first
        mrect = menu.bounding_box() if menu.count() else None
        styles = None
        if menu.count():
            styles = menu.evaluate(
                """el => {
                    const cs = getComputedStyle(el);
                    return {position: cs.position, top: cs.top, left: cs.left,
                            transform: cs.transform, inset: cs.inset,
                            cls: el.className,
                            parentCls: el.parentElement.className,
                            inlineStyle: el.getAttribute('style')};
                }"""
            )
        print(f"--- {label} ---")
        print(f"  toggle rect: {trect}")
        print(f"  menu rect:   {mrect}")
        print(f"  menu styles: {json.dumps(styles, indent=2) if styles else None}")
        page.screenshot(path=os.path.join(OUT, f"dropdown_{label}.png"))
        page.keyboard.press("Escape")
        page.wait_for_timeout(400)
    except Exception as e:
        print(f"--- {label} --- FAILED: {e}")
        page.screenshot(path=os.path.join(OUT, f"dropdown_{label}_fail.png"))


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.on("console", lambda m: console_msgs.append((m.type, m.text)) if m.type in ("error", "warning") else None)
    page.on("pageerror", lambda e: page_errors.append(str(e)))

    login(page)

    # font-size baseline
    fs = page.evaluate("""() => {
        const cs = getComputedStyle(document.body);
        const root = getComputedStyle(document.documentElement);
        return {bodyFont: cs.fontFamily, bodySize: cs.fontSize, rootSize: root.fontSize};
    }""")
    print("FONT:", json.dumps(fs, indent=2))

    # user menu (top right avatar)
    probe_dropdown(page, "user_menu", ".o_user_menu button, .o_user_menu .dropdown-toggle")

    # go to sale orders list for cog / filter dropdowns
    page.goto(f"{BASE}/odoo/action-sale.action_orders")
    page.wait_for_selector(".o_list_view, .o_view_controller", timeout=20000)
    page.wait_for_timeout(1500)

    probe_dropdown(page, "favorites_searchbar", ".o_searchview_dropdown_toggler, .o_cp_searchview .dropdown-toggle")
    probe_dropdown(page, "cog_menu", ".o_cp_action_menus .dropdown-toggle, button[title='Actions']")

    # navbar menu sections (e.g. Orders menu in Sales app)
    probe_dropdown(page, "navbar_section", ".o_menu_sections .dropdown-toggle, .o_menu_sections button")

    print("\n=== PAGE ERRORS ===")
    for e in page_errors:
        print(" *", e)
    print("=== CONSOLE (err/warn) ===")
    for t, m in console_msgs:
        print(f" [{t}] {m[:300]}")

    browser.close()
