# -*- coding: utf-8 -*-
"""Targeted UI-audit capture for the Nile theme refinement pass.

Captures the specific things the broad sweep misses and that the user flagged:
  * the Theme Settings dialog (the panel to be redesigned),
  * open menus / dropdowns (the "buttons on the menu" that may not be themed),
  * a grouped kanban header (the "column value glued to the corner" bug),
  * a PALETTE-DIFF: the same screens rendered with the company palette at the
    default 'teal' vs switched to 'blue'. Any surface that stays teal in the
    blue shot is one the runtime re-point sheet does NOT cover => the root
    cause of "the color theme doesn't apply on <x>". Restores the palette and
    admin lang afterwards.

Usage: python3 scripts/qa_audit_capture.py [db]
"""
import os
import sys
import xmlrpc.client
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8069"
DB = sys.argv[1] if len(sys.argv) > 1 else "erpmedsupply"
USER, PWD = "admin", "admin"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "theme-audit", "qa", "audit")

# Screens used for the palette diff (kept short — accent-bearing surfaces).
DIFF_SHOTS = [
    ("sale_form", "/odoo/action-sale.action_orders/1", ".o_form_view"),
    ("sale_list", "/odoo/action-sale.action_orders", ".o_list_view, .o_kanban_view"),
    ("settings", "/odoo/action-base_setup.action_general_configuration", ".o_form_view, .settings"),
]
# Candidate grouped kanban boards (first that loads wins).
KANBAN_CANDIDATES = [
    ("crm_pipeline", "/odoo/crm"),
    ("project", "/odoo/project"),
    ("sale_kanban", "/odoo/action-sale.action_orders"),
]


def rpc():
    common = xmlrpc.client.ServerProxy(f"{BASE}/xmlrpc/2/common")
    uid = common.authenticate(DB, USER, PWD, {})
    models = xmlrpc.client.ServerProxy(f"{BASE}/xmlrpc/2/object")
    return uid, models


def get_company_and_preset(uid, models):
    cid = models.execute_kw(DB, uid, PWD, "res.users", "read",
                            [[uid], ["company_id"]])[0]["company_id"][0]
    preset = models.execute_kw(DB, uid, PWD, "res.company", "read",
                               [[cid], ["nile_palette_preset"]])[0]["nile_palette_preset"]
    return cid, preset


def set_lang(uid, models, lang):
    models.execute_kw(DB, uid, PWD, "res.users", "write", [[uid], {"lang": lang}])


def set_preset(uid, models, cid, preset):
    models.execute_kw(DB, uid, PWD, "res.company", "write",
                      [[cid], {"nile_palette_preset": preset}])


def login(page):
    page.goto(f"{BASE}/web/login?db={DB}")
    if page.locator("input[name=login]").count():
        page.fill("input[name=login]", USER)
        page.fill("input[name=password]", PWD)
        page.click("button[type=submit]")
    page.wait_for_selector(".o_main_navbar", timeout=20000)
    page.wait_for_timeout(1200)


def shot(page, name):
    os.makedirs(OUT, exist_ok=True)
    page.screenshot(path=os.path.join(OUT, f"{name}.png"), full_page=False)
    print(" *", name)


with sync_playwright() as p:
    uid, models = rpc()
    cid, orig_preset = get_company_and_preset(uid, models)
    print(f"company={cid} original preset={orig_preset}")
    set_lang(uid, models, "en_US")

    b = p.chromium.launch()
    try:
        ctx = b.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        login(page)

        # ---- 1. Theme Settings dialog ----
        try:
            page.click(".o_nile_theme_systray")
            page.wait_for_selector(".o_nile_theme_dialog", timeout=8000)
            page.wait_for_timeout(700)
            shot(page, "theme_dialog")
            page.keyboard.press("Escape")
            page.wait_for_timeout(400)
        except Exception as e:
            print(" ! theme_dialog FAIL", str(e)[:160])

        # ---- 2. Open menus / dropdowns ("buttons on the menu") ----
        try:
            page.goto(f"{BASE}/odoo/action-sale.action_orders")
            page.wait_for_selector(".o_main_navbar", timeout=15000)
            page.wait_for_timeout(1200)
            # apps menu (grid)
            tgl = page.locator(".o_navbar_apps_menu button, .o_menu_toggle").first
            if tgl.count():
                tgl.click()
                page.wait_for_timeout(700)
                shot(page, "apps_menu")
                page.keyboard.press("Escape")
                page.wait_for_timeout(300)
            # a top menu section dropdown (e.g. "Orders"/"Products")
            sec = page.locator(".o_main_navbar .o_menu_sections .dropdown-toggle").first
            if sec.count():
                sec.click()
                page.wait_for_timeout(600)
                shot(page, "menu_section_open")
                page.keyboard.press("Escape")
                page.wait_for_timeout(300)
            # user systray menu (top-right)
            usr = page.locator(".o_user_menu .dropdown-toggle, .o_user_menu button").first
            if usr.count():
                usr.click()
                page.wait_for_timeout(600)
                shot(page, "user_menu_open")
                page.keyboard.press("Escape")
                page.wait_for_timeout(300)
        except Exception as e:
            print(" ! menus FAIL", str(e)[:160])

        # ---- 3. Grouped kanban header (column value / count placement) ----
        for name, path in KANBAN_CANDIDATES:
            try:
                page.goto(f"{BASE}{path}")
                page.wait_for_selector(".o_kanban_view.o_kanban_grouped, .o_kanban_renderer.o_kanban_grouped",
                                       timeout=8000)
                page.wait_for_timeout(1400)
                shot(page, f"kanban_grouped_{name}")
                break
            except Exception:
                continue
        else:
            print(" ! no grouped kanban loaded")

        # ---- 4. PALETTE DIFF: teal (orig) vs blue ----
        def capture_palette(tag):
            for name, path, sel in DIFF_SHOTS:
                try:
                    page.goto(f"{BASE}{path}")
                    if sel:
                        page.wait_for_selector(sel, timeout=15000)
                    page.wait_for_timeout(1400)
                    shot(page, f"palette_{tag}_{name}")
                except Exception as e:
                    print(f" ! palette_{tag}_{name} FAIL", str(e)[:120])

        capture_palette("base")  # whatever the company is set to now (default teal)
        set_preset(uid, models, cid, "blue")
        page.wait_for_timeout(500)
        # hard reload so the server re-injects the runtime <style> palette
        page.goto(f"{BASE}/web?reload=1")
        page.wait_for_timeout(1500)
        capture_palette("blue")

        ctx.close()
    finally:
        # restore palette + lang no matter what
        set_preset(uid, models, cid, orig_preset or "teal")
        set_lang(uid, models, "ar_001")
        b.close()
        print(f"restored preset={orig_preset or 'teal'} lang=ar_001")
