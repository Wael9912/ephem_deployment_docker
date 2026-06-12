# -*- coding: utf-8 -*-
"""Comprehensive nile-theme QA matrix.

Engines x viewports x dropdown types. Flags any dropdown whose menu lands
>40px away from its toggle (mis-positioned) or at (0,0).
Usage: python3 scripts/qa_matrix.py [db]
"""
import os
import sys
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8069"
DB = sys.argv[1] if len(sys.argv) > 1 else "erpmedsupply"
USER, PWD = "admin", "admin"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "theme-audit", "qa", "img")
os.makedirs(OUT, exist_ok=True)

VIEWPORTS = [(1920, 1080), (1366, 768), (1280, 800), (1024, 768), (768, 900), (390, 844)]

DROPDOWNS = [
    # (label, page path, toggle selector)
    ("user_menu", "/odoo/action-sale.action_orders", ".o_user_menu button"),
    ("cog_actions", "/odoo/action-sale.action_orders", ".o_cp_action_menus .dropdown-toggle"),
    ("search_toggler", "/odoo/action-sale.action_orders", ".o_searchview_dropdown_toggler"),
    ("navbar_section", "/odoo/action-sale.action_orders", ".o_menu_sections .o-dropdown"),
    ("list_optional_cols", "/odoo/action-sale.action_orders", ".o_optional_columns_dropdown .dropdown-toggle, .o_optional_columns_dropdown_toggle"),
    ("activity_menu", "/odoo/action-sale.action_orders", ".o_menu_systray .o-mail-ActivityMenu button, .o_menu_systray [title='Activities']"),
]


def login(page):
    page.goto(f"{BASE}/web/login?db={DB}", timeout=30000)
    if page.locator("input[name=login]").count():
        page.fill("input[name=login]", USER)
        page.fill("input[name=password]", PWD)
        page.click("button[type=submit]")
    page.wait_for_selector(".o_main_navbar, .o_home_menu", timeout=20000)
    page.wait_for_timeout(1000)


def run_engine(p, engine_name):
    browser = getattr(p, engine_name).launch()
    issues = []
    errors = []
    for w, h in VIEWPORTS:
        ctx = browser.new_context(viewport={"width": w, "height": h})
        page = ctx.new_page()
        page.on("pageerror", lambda e, w=w: errors.append(f"[{engine_name} {w}px] {e}"))
        page.on("console", lambda m, w=w: errors.append(f"[{engine_name} {w}px console] {m.text[:200]}") if m.type == "error" else None)
        try:
            login(page)
        except Exception as e:
            issues.append(f"[{engine_name} {w}x{h}] LOGIN FAILED: {e}")
            ctx.close()
            continue
        cur_path = None
        for label, path, sel in DROPDOWNS:
            try:
                if path != cur_path:
                    page.goto(f"{BASE}/odoo" if path == "/" else f"{BASE}{path}")
                    page.wait_for_selector(".o_action_manager .o_view_controller, .o_list_view", timeout=20000)
                    page.wait_for_timeout(1200)
                    cur_path = path
                tog = page.locator(sel).first
                if not tog.count() or not tog.is_visible():
                    continue
                trect = tog.bounding_box()
                tog.click()
                page.wait_for_timeout(600)
                menu = page.locator(".o-dropdown--menu, .o_popover").first
                if not menu.count():
                    issues.append(f"[{engine_name} {w}x{h}] {label}: menu never appeared")
                    continue
                mrect = menu.bounding_box()
                # full-screen mobile menus are fine; flag only desktop anomalies
                anchored = (
                    abs(mrect["y"] - (trect["y"] + trect["height"])) < 60
                    or abs((mrect["x"] + mrect["width"]) - (trect["x"] + trect["width"])) < 60
                    or abs(mrect["x"] - trect["x"]) < 60
                    or mrect["width"] >= w * 0.9  # fullscreen mobile pattern
                )
                at_origin = mrect["x"] < 2 and mrect["y"] < 2
                if (not anchored) or (at_origin and trect["x"] > 100 and w > 768):
                    issues.append(
                        f"[{engine_name} {w}x{h}] {label}: MISPOSITIONED toggle={trect} menu={mrect}"
                    )
                    page.screenshot(path=os.path.join(OUT, f"bug_{engine_name}_{w}_{label}.png"))
                page.keyboard.press("Escape")
                page.wait_for_timeout(300)
            except Exception as e:
                issues.append(f"[{engine_name} {w}x{h}] {label}: ERROR {str(e)[:200]}")
        ctx.close()
    browser.close()
    return issues, errors


with sync_playwright() as p:
    all_issues, all_errors = [], []
    for eng in ("chromium", "webkit"):
        try:
            i, e = run_engine(p, eng)
            all_issues += i
            all_errors += e
        except Exception as ex:
            all_issues.append(f"[{eng}] ENGINE FAILED: {ex}")

    print("=== ISSUES ===")
    for i in all_issues or ["none"]:
        print(" *", i)
    print("=== JS ERRORS ===")
    seen = set()
    for e in all_errors:
        if e not in seen:
            seen.add(e)
            print(" *", e)
