# -*- coding: utf-8 -*-
"""
Phase-0 Nile spike: capture comparison screenshots from erpmedsupply_nile.

Usage:
    python3 scripts/spike_capture.py <variant> <lang>
        variant: spiffy | core | responsive
        lang:    en | ar   (admin user lang must already match)

Output: docs/theme-audit/phase0-spike/img/<variant>/<lang>/*.png
"""
import os
import sys
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8069"
DB = os.environ.get("SPIKE_DB", "erpmedsupply_nile")
USER, PWD = "admin", "admin"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VARIANT = sys.argv[1]
LANG = sys.argv[2]
OUT = os.path.join(ROOT, "docs", "theme-audit", "phase0-spike", "img", VARIANT, LANG)
os.makedirs(OUT, exist_ok=True)

# (filename, path) — reduced demo-relevant set; record ids from capture_screens.py
SHOTS = [
    ("inventory_overview", "/odoo/inventory"),
    ("products_kanban",    "/odoo/action-stock.product_template_action_product"),
    ("sale_orders_list",   "/odoo/action-sale.action_orders"),
    ("sale_order_form",    "/odoo/action-sale.action_orders/1"),
    ("settings_general",   "/odoo/action-base_setup.action_general_configuration"),
]

# app-launcher opener per variant
DRAWER_SEL = {
    "spiffy":     ["a.appDrawerToggle"],
    "core":       [".o_navbar_apps_menu button", ".o_menu_toggle"],
    "responsive": ["button.o_grid_apps_menu__button"],
    "nile":       ["button.o_grid_apps_menu__button"],  # Phase 1: full Nile stack
}

KILL_OVERLAYS = """() => {
  const sels = ['.o_onboarding_container','.o_onboarding','.o-tour-pointer',
    '.o_tooltip','.o_blockUI','.popover','.o_notification_manager .o_notification',
    '.o-mail-ChatWindow','.o_web_studio_upgrade'];
  for (const s of sels) document.querySelectorAll(s).forEach(e => e.remove());
}"""


def settle(page):
    for sel in (".o_form_view", ".o_list_view", ".o_kanban_view",
                ".o_action_manager", ".o_content"):
        try:
            page.wait_for_selector(sel, timeout=12000)
            break
        except Exception:
            continue
    page.wait_for_timeout(1400)
    try:
        page.evaluate(KILL_OVERLAYS)
    except Exception:
        pass
    page.wait_for_timeout(400)


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--no-sandbox"])
        ctx = browser.new_context(
            viewport={"width": 1480, "height": 940}, device_scale_factor=2,
            locale="ar-SD" if LANG == "ar" else "en-US")
        page = ctx.new_page()
        page.set_default_timeout(20000)

        page.goto(BASE + "/web/login?db=" + DB, wait_until="networkidle")
        page.wait_for_selector("input[name=login]", state="visible", timeout=15000)
        page.wait_for_timeout(700)
        page.screenshot(path=os.path.join(OUT, "login.png"))
        page.fill("input[name=login]", USER)
        page.fill("input[name=password]", PWD)
        page.click("button[type=submit]")
        page.wait_for_selector(".o_main_navbar", timeout=30000)
        page.wait_for_timeout(2200)

        # RTL bundle sanity: assert the served backend CSS URL contains /rtl/
        if LANG == "ar":
            rtl = page.evaluate(
                "() => [...document.querySelectorAll('link[rel=stylesheet]')]"
                ".map(l => l.href).filter(h => h.includes('web.assets'))")
            flipped = any(("/rtl/" in h) or (".rtl." in h) for h in rtl)
            print("RTL bundle check:", "OK" if flipped else "NOT FLIPPED", rtl[:3])

        ok = fail = 0

        # app launcher shot
        try:
            page.goto(BASE + "/odoo", wait_until="commit")
            settle(page)
            for sel in DRAWER_SEL.get(VARIANT, []):
                try:
                    page.eval_on_selector(sel, "e=>e.click()")
                    page.wait_for_timeout(1800)
                    break
                except Exception:
                    continue
            try:
                page.evaluate(KILL_OVERLAYS)
            except Exception:
                pass
            page.screenshot(path=os.path.join(OUT, "apps_home.png"))
            ok += 1
            print("OK  ", "apps_home")
        except Exception as e:
            fail += 1
            print("FAIL apps_home ->", repr(e)[:110])

        for name, path in SHOTS:
            try:
                page.goto(BASE + path, wait_until="commit")
                settle(page)
                page.screenshot(path=os.path.join(OUT, name + ".png"))
                ok += 1
                print("OK  ", name)
            except Exception as e:
                fail += 1
                print("FAIL", name, "->", repr(e)[:110])
        print("---- %s/%s: %d ok, %d failed ----" % (VARIANT, LANG, ok, fail))
        browser.close()


if __name__ == "__main__":
    main()
