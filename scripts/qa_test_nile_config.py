# -*- coding: utf-8 -*-
"""Functional test of the nile_config systray configurator.

Opens dialog, previews + saves prefs, verifies persistence and runtime
application (html attrs, root font-size, palette style, dark bundle),
then restores defaults.
Usage: python3 scripts/qa_test_nile_config.py [db]
"""
import os
import sys
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8069"
DB = sys.argv[1] if len(sys.argv) > 1 else "erpmedsupply"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "theme-audit", "qa", "img")
os.makedirs(OUT, exist_ok=True)

errors = []
failures = []


def check(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name + (f" ({detail})" if detail else ""))
    if not cond:
        failures.append(f"{name}: {detail}")


def login(page):
    page.goto(f"{BASE}/web/login?db={DB}", timeout=30000)
    if page.locator("input[name=login]").count():
        page.fill("input[name=login]", "admin")
        page.fill("input[name=password]", "admin")
        page.click("button[type=submit]")
    page.wait_for_selector(".o_main_navbar", timeout=20000)
    page.wait_for_timeout(1500)


def open_dialog(page):
    page.locator(".o_nile_theme_systray").click()
    page.wait_for_selector(".o_nile_theme_dialog", timeout=8000)
    page.wait_for_timeout(400)


with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()
    page.on("pageerror", lambda e: errors.append(str(e)[:300]))
    page.on("console", lambda m: errors.append("console: " + m.text[:300]) if m.type == "error" else None)

    login(page)

    # 1. systray button present
    check("systray button visible", page.locator(".o_nile_theme_systray").is_visible())

    # 2. dialog opens with sections
    open_dialog(page)
    check("company section (admin)", page.locator(".o_nile_theme_dialog section").count() >= 2)
    check("6 preset swatches + custom", page.locator(".o_nile_swatch").count() == 7)
    page.screenshot(path=os.path.join(OUT, "nile_config_dialog.png"))

    # 3. live preview: pick blue preset -> navbar recolors instantly
    page.locator(".o_nile_swatch").nth(1).click()  # blue
    page.wait_for_timeout(400)
    navbar_bg = page.evaluate("getComputedStyle(document.querySelector('.o_main_navbar')).backgroundColor")
    check("live preview navbar blue", navbar_bg == "rgb(29, 78, 216)", navbar_bg)

    # 4. font scale preview
    page.locator(".o_nile_theme_dialog .row").nth(1).locator(".btn-group .btn").nth(2).click()
    page.wait_for_timeout(300)
    root_fs = page.evaluate("getComputedStyle(document.documentElement).fontSize")
    check("live preview large font", root_fs == "17px", root_fs)

    # 5. density preview
    page.locator(".o_nile_theme_dialog .row").nth(2).locator(".btn-group .btn").nth(1).click()
    page.wait_for_timeout(300)
    pad = page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--nile-density-row-pad-block').trim()")
    check("live preview compact density", pad == "4px", pad)

    # 6. discard restores
    page.locator(".modal-footer .btn-secondary").click()
    page.wait_for_timeout(500)
    navbar_bg = page.evaluate("getComputedStyle(document.querySelector('.o_main_navbar')).backgroundColor")
    root_fs = page.evaluate("getComputedStyle(document.documentElement).fontSize")
    check("discard restores navbar", navbar_bg == "rgb(14, 116, 144)", navbar_bg)
    check("discard restores font", root_fs == "16px", root_fs)

    # 7. save flow: blue + large + compact, then verify after reload
    open_dialog(page)
    page.locator(".o_nile_swatch").nth(1).click()
    page.locator(".o_nile_theme_dialog .row").nth(1).locator(".btn-group .btn").nth(2).click()
    page.locator(".o_nile_theme_dialog .row").nth(2).locator(".btn-group .btn").nth(1).click()
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
    page.screenshot(path=os.path.join(OUT, "nile_config_saved_blue_large_compact.png"))

    # 9. restore defaults (teal preset, defaults, dark off)
    open_dialog(page)
    page.locator(".o_nile_swatch").nth(0).click()
    page.locator(".o_nile_theme_dialog .row").nth(1).locator(".btn-group .btn").nth(1).click()
    page.locator(".o_nile_theme_dialog .row").nth(2).locator(".btn-group .btn").nth(0).click()
    page.locator(".modal-footer .btn-primary").click()
    page.wait_for_selector(".o_main_navbar", timeout=25000)
    page.wait_for_timeout(2500)
    navbar_bg = page.evaluate("getComputedStyle(document.querySelector('.o_main_navbar')).backgroundColor")
    root_fs = page.evaluate("getComputedStyle(document.documentElement).fontSize")
    dark_link = page.evaluate("[...document.styleSheets].some(s => (s.href||'').includes('assets_web_dark'))")
    check("restored teal", navbar_bg == "rgb(14, 116, 144)", navbar_bg)
    check("restored default font", root_fs == "16px", root_fs)
    check("dark bundle never active (no toggle in Community)", not dark_link)
    page.screenshot(path=os.path.join(OUT, "nile_config_restored.png"))

    b.close()

print("\n=== RESULT ===")
print("FAILURES:", failures or "none")
print("JS ERRORS:")
for e in dict.fromkeys(errors) or ["none"]:
    print(" *", e)
sys.exit(1 if failures else 0)
