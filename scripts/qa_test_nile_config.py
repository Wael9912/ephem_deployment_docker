# -*- coding: utf-8 -*-
"""Functional test of the nile_config systray configurator (tabbed layout).

Opens the dialog, exercises each tab (Brand / Typography / Display), checks
live preview + persistence + runtime application, verifies the HSV picker and
the systray globe, then restores the company's ORIGINAL palette and admin prefs.
Usage: python3 scripts/qa_test_nile_config.py [db]
"""
import os
import sys
import xmlrpc.client
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8069"
DB = sys.argv[1] if len(sys.argv) > 1 else "erpmedsupply"
USER = PWD = "admin"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "theme-audit", "qa", "img")
os.makedirs(OUT, exist_ok=True)

errors, failures = [], []


def check(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name + (f" ({detail})" if detail else ""))
    if not cond:
        failures.append(f"{name}: {detail}")


# --- restore handles (read original company palette so we leave it untouched) ---
common = xmlrpc.client.ServerProxy(f"{BASE}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f"{BASE}/xmlrpc/2/object")
cid = models.execute_kw(DB, uid, PWD, "res.users", "read", [[uid], ["company_id"]])[0]["company_id"][0]
orig = models.execute_kw(DB, uid, PWD, "res.company", "read",
                         [[cid], ["nile_palette_preset", "nile_color_primary"]])[0]
orig_lang = models.execute_kw(DB, uid, PWD, "res.users", "read", [[uid], ["lang"]])[0]["lang"]
# The demo admin runs in Arabic; switch to English so role-name selectors match.
models.execute_kw(DB, uid, PWD, "res.users", "write", [[uid], {"lang": "en_US"}])


def login(page):
    page.goto(f"{BASE}/web/login?db={DB}", timeout=30000)
    if page.locator("input[name=login]").count():
        page.fill("input[name=login]", USER)
        page.fill("input[name=password]", PWD)
        page.click("button[type=submit]")
    page.wait_for_selector(".o_main_navbar", timeout=20000)
    page.wait_for_timeout(1500)


def open_dialog(page):
    page.locator(".o_nile_theme_systray").click()
    page.wait_for_selector(".o_nile_theme_dialog", timeout=8000)
    page.wait_for_timeout(400)


def tab(page, name):
    page.get_by_role("tab", name=name).click()
    page.wait_for_timeout(250)


with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()
    page.on("pageerror", lambda e: errors.append(str(e)[:300]))
    page.on("console", lambda m: errors.append("console: " + m.text[:300]) if m.type == "error" else None)

    login(page)

    # 1. systray buttons present (brush + globe)
    check("theme brush visible", page.locator(".o_nile_theme_systray").is_visible())
    check("language globe visible", page.locator(".o_nile_lang_systray").is_visible())

    # 2. dialog opens on Brand tab with palette swatches
    open_dialog(page)
    check("3 tabs present", page.locator(".o_nile_tabs .nav-link").count() == 3)
    check("6 presets + custom swatch", page.locator(".o_nile_swatch").count() == 7)

    # 3. Brand: blue preset -> live navbar recolor
    page.locator(".o_nile_swatch").nth(1).click()
    page.wait_for_timeout(400)
    navbar_bg = page.evaluate("getComputedStyle(document.querySelector('.o_main_navbar')).backgroundColor")
    check("live preview navbar blue", navbar_bg == "rgb(29, 78, 216)", navbar_bg)

    # 4. Brand: custom swatch reveals the HSV picker, hex edit drives preview
    page.locator(".o_nile_swatch_custom").click()
    page.wait_for_timeout(300)
    check("HSV picker shown on custom", page.locator(".o_nile_color_picker").is_visible())
    hexf = page.locator(".o_nile_hex_input")
    hexf.fill("#AA3344")
    hexf.dispatch_event("input")
    page.wait_for_timeout(300)
    navbar_bg = page.evaluate("getComputedStyle(document.querySelector('.o_main_navbar')).backgroundColor")
    check("hex input drives preview", navbar_bg == "rgb(170, 51, 68)", navbar_bg)
    page.screenshot(path=os.path.join(OUT, "nile_config_brand_hsv.png"))

    # 5. Typography: large font preview
    tab(page, "Typography")
    page.get_by_role("button", name="Large").click()
    page.wait_for_timeout(300)
    root_fs = page.evaluate("getComputedStyle(document.documentElement).fontSize")
    check("live preview large font", root_fs == "17px", root_fs)

    # 6. Display: compact density preview
    tab(page, "Display")
    page.get_by_role("button", name="Compact").click()
    page.wait_for_timeout(300)
    pad = page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--nile-density-row-pad-block').trim()")
    check("live preview compact density", pad == "4px", pad)

    # 7. discard restores the saved look
    page.locator(".modal-footer .btn-secondary").click()
    page.wait_for_timeout(500)
    root_fs = page.evaluate("getComputedStyle(document.documentElement).fontSize")
    check("discard restores font size", root_fs == "16px", root_fs)

    # 8. save flow: blue + large + compact -> verify after reload
    open_dialog(page)
    page.locator(".o_nile_swatch").nth(1).click()  # Brand tab (default), blue
    tab(page, "Typography")
    page.get_by_role("button", name="Large").click()
    tab(page, "Display")
    page.get_by_role("button", name="Compact").click()
    page.locator(".modal-footer .btn-primary").click()
    page.wait_for_selector(".o_main_navbar", timeout=25000)
    page.wait_for_timeout(2500)
    navbar_bg = page.evaluate("getComputedStyle(document.querySelector('.o_main_navbar')).backgroundColor")
    root_fs = page.evaluate("getComputedStyle(document.documentElement).fontSize")
    pad = page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--nile-density-row-pad-block').trim()")
    check("persisted navbar blue", navbar_bg == "rgb(29, 78, 216)", navbar_bg)
    check("persisted large font", root_fs == "17px", root_fs)
    check("persisted compact density", pad == "4px", pad)
    btn_bg = page.evaluate("""() => {
        const el = document.querySelector('.o_control_panel .btn-primary, .btn-primary');
        return el ? getComputedStyle(el).backgroundColor : null;
    }""")
    check("btn-primary follows palette", btn_bg == "rgb(29, 78, 216)", str(btn_bg))

    # 9. restore admin prefs to defaults (font/size/density) via the dialog
    open_dialog(page)
    tab(page, "Typography")
    page.get_by_role("button", name="Default").click()
    tab(page, "Display")
    page.get_by_role("button", name="Comfortable").click()
    page.locator(".modal-footer .btn-primary").click()
    page.wait_for_selector(".o_main_navbar", timeout=25000)
    page.wait_for_timeout(2000)
    root_fs = page.evaluate("getComputedStyle(document.documentElement).fontSize")
    check("restored default font", root_fs == "16px", root_fs)
    dark_link = page.evaluate("[...document.styleSheets].some(s => (s.href||'').includes('assets_web_dark'))")
    check("dark bundle off", not dark_link)

    # 10. globe language switch persists (admin is en_US here; switch to Arabic)
    page.locator(".o_nile_lang_systray").click()
    page.wait_for_timeout(600)
    page.locator(".o-dropdown--menu .dropdown-item, .o_nile_lang_menu .dropdown-item") \
        .filter(has_text="Arab").first.click()
    page.wait_for_selector(".o_main_navbar", timeout=20000)
    page.wait_for_timeout(1500)
    lang_now = models.execute_kw(DB, uid, PWD, "res.users", "read", [[uid], ["lang"]])[0]["lang"]
    check("globe switches language (persisted)", lang_now == "ar_001", lang_now)

    b.close()

# Restore the company's ORIGINAL palette (the dialog left it on blue/custom).
models.execute_kw(DB, uid, PWD, "res.company", "write", [[cid], {
    "nile_palette_preset": orig["nile_palette_preset"],
    "nile_color_primary": orig["nile_color_primary"] or False,
}])
models.execute_kw(DB, uid, PWD, "res.users", "write", [[uid], {"lang": orig_lang}])
print(f"\n(restored company palette -> {orig['nile_palette_preset']}, admin lang -> {orig_lang})")

print("=== RESULT ===")
print("FAILURES:", failures or "none")
print("JS ERRORS:")
for e in dict.fromkeys(errors) or ["none"]:
    print(" *", e)
sys.exit(1 if failures else 0)
