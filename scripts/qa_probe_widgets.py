# -*- coding: utf-8 -*-
"""Probe exotic overlay widgets: many2one autocomplete, date picker, kanban
card menu, command palette — with and without prefers-reduced-motion.
Usage: python3 scripts/qa_probe_widgets.py [db] [chromium|webkit]
"""
import os
import sys
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8069"
DB = sys.argv[1] if len(sys.argv) > 1 else "erpmedsupply"
ENGINE = sys.argv[2] if len(sys.argv) > 2 else "chromium"
USER, PWD = "admin", "admin"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "theme-audit", "qa", "img")
os.makedirs(OUT, exist_ok=True)

issues, errors = [], []


def login(page):
    page.goto(f"{BASE}/web/login?db={DB}", timeout=30000)
    if page.locator("input[name=login]").count():
        page.fill("input[name=login]", USER)
        page.fill("input[name=password]", PWD)
        page.click("button[type=submit]")
    page.wait_for_selector(".o_main_navbar", timeout=20000)
    page.wait_for_timeout(1200)


def check(page, label, toggle, menu_sel):
    trect = toggle.bounding_box()
    page.wait_for_timeout(700)
    menu = page.locator(menu_sel).first
    if not menu.count() or not menu.is_visible():
        issues.append(f"{label}: menu did not appear")
        page.screenshot(path=os.path.join(OUT, f"widget_{label}_missing.png"))
        return
    mrect = menu.bounding_box()
    near = (
        abs(mrect["y"] - (trect["y"] + trect["height"])) < 80
        or abs((trect["y"]) - (mrect["y"] + mrect["height"])) < 80
    )
    at_origin = mrect["x"] < 2 and mrect["y"] < 2
    if at_origin or not near:
        issues.append(f"{label}: MISPOSITIONED toggle={trect} menu={mrect}")
        page.screenshot(path=os.path.join(OUT, f"widget_{label}_bug.png"))
    else:
        print(f"  OK {label}: menu at ({mrect['x']:.0f},{mrect['y']:.0f}) toggle at ({trect['x']:.0f},{trect['y']:.0f})")


def run(p, reduced):
    browser = getattr(p, ENGINE).launch()
    ctx = browser.new_context(
        viewport={"width": 1440, "height": 900},
        reduced_motion="reduce" if reduced else "no-preference",
    )
    page = ctx.new_page()
    page.on("pageerror", lambda e: errors.append(f"[reduced={reduced}] {e}"))
    page.on("console", lambda m: errors.append(f"[reduced={reduced} console] {m.text[:200]}") if m.type == "error" else None)
    tag = "rm" if reduced else "std"
    print(f"--- engine={ENGINE} reduced_motion={reduced} ---")
    login(page)

    # form view: many2one + date picker
    page.goto(f"{BASE}/odoo/action-sale.action_orders/new")
    page.wait_for_selector(".o_form_view", timeout=20000)
    page.wait_for_timeout(1200)

    m2o = page.locator(".o_field_many2one input").first
    if m2o.count():
        m2o.click()
        check(page, f"{tag}_many2one", m2o, ".o-autocomplete--dropdown-menu, .o-autocomplete.dropdown ul")
        page.keyboard.press("Escape")

    dt = page.locator(".o_field_date input, input.o_input[data-field*='date'], .o_field_widget[name*='date'] input").first
    if dt.count():
        dt.click()
        check(page, f"{tag}_datepicker", dt, ".o_datetime_picker")
        page.keyboard.press("Escape")

    # status bar dropdown? skip on new record. kanban card menu:
    page.goto(f"{BASE}/odoo/action-stock.product_template_action_product")
    page.wait_for_selector(".o_kanban_renderer", timeout=20000)
    page.wait_for_timeout(1200)
    card_menu = page.locator(".o_kanban_record .o_dropdown_kanban .dropdown-toggle, .o_kanban_record button.o-dropdown").first
    if card_menu.count():
        card_menu.hover()
        card_menu.click()
        check(page, f"{tag}_kanban_card_menu", card_menu, ".o-dropdown--menu")
        page.keyboard.press("Escape")
    else:
        print("  (no kanban card menu toggle found)")

    # command palette
    page.keyboard.press("Control+k" if ENGINE == "chromium" else "Meta+k")
    page.wait_for_timeout(700)
    pal = page.locator(".o_command_palette")
    if pal.count():
        r = pal.first.bounding_box()
        print(f"  OK {tag}_command_palette at ({r['x']:.0f},{r['y']:.0f}) w={r['width']:.0f}")
    else:
        issues.append(f"{tag}: command palette did not open")
    page.keyboard.press("Escape")

    page.screenshot(path=os.path.join(OUT, f"widgets_{ENGINE}_{tag}.png"))
    ctx.close()
    browser.close()


with sync_playwright() as p:
    run(p, reduced=False)
    run(p, reduced=True)

print("=== ISSUES ===")
for i in issues or ["none"]:
    print(" *", i)
print("=== JS ERRORS ===")
for e in dict.fromkeys(errors) or ["none"]:
    print(" *", e)
