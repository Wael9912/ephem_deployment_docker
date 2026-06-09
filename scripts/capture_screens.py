# -*- coding: utf-8 -*-
"""
Capture real screenshots from the running Odoo (erpmedsupply) for the user
manual. Drives a headless Chromium via Playwright, logging in as admin and
deep-linking into the actual demo records.

Usage:
    python3 scripts/capture_screens.py en
    python3 scripts/capture_screens.py ar
"""
import os
import sys
import time
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8069"
USER, PWD = "admin", "admin"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANG = sys.argv[1] if len(sys.argv) > 1 else "en"
OUT = os.path.join(ROOT, "docs", "manual", "img", LANG)
os.makedirs(OUT, exist_ok=True)

# (filename, deep-link path, optional selector to wait for beyond default)
SHOTS = [
    ("apps_home",      "/odoo",                                              None),
    ("inventory",      "/odoo/inventory",                                    None),
    ("products_list",  "/odoo/action-stock.product_template_action_product", None),
    ("product_insulin","/odoo/action-stock.product_template_action_product/3", None),
    ("lots_expiry",    "/odoo/action-stock.action_production_lot_form",      None),
    ("locations",      "/odoo/action-stock.action_location_form",            None),
    ("transfers",      "/odoo/action-stock.action_picking_tree_all",         None),
    ("purchase_usd",   "/odoo/action-purchase.purchase_form_action/2",       None),
    ("sale_order",     "/odoo/action-sale.action_orders/1",                  None),
    ("customer_invoice","/odoo/action-account.action_move_out_invoice_type/2", None),
    ("currency_rates", "/odoo/action-base.action_currency_form/1",           None),
    ("accounting",     "/odoo/accounting",                                   None),
    ("contacts",       "/odoo/contacts",                                     None),
]


def settle(page, extra=None):
    try:
        page.wait_for_load_state("networkidle", timeout=20000)
    except Exception:
        pass
    # wait for the action content to render
    for sel in (".o_action_manager", ".o_content"):
        try:
            page.wait_for_selector(sel, timeout=15000)
            break
        except Exception:
            continue
    # let lazy widgets / kanban images paint
    page.wait_for_timeout(1800)
    if extra:
        try:
            page.wait_for_selector(extra, timeout=8000)
        except Exception:
            pass


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--no-sandbox"])
        ctx = browser.new_context(
            viewport={"width": 1480, "height": 940},
            device_scale_factor=2,
            locale="ar-SD" if LANG == "ar" else "en-US",
        )
        page = ctx.new_page()

        # ---- login page (clean, before auth) ----
        # dbfilter matches >1 DB, so pre-select erpmedsupply to land on the form
        page.goto(BASE + "/web/login?db=erpmedsupply", wait_until="networkidle")
        page.wait_for_selector("input[name=login]", state="visible", timeout=15000)
        page.wait_for_timeout(800)
        page.screenshot(path=os.path.join(OUT, "login.png"))

        # ---- authenticate ----
        page.fill("input[name=login]", USER)
        page.fill("input[name=password]", PWD)
        page.click("button[type=submit]")
        # Odoo holds a long-poll socket so 'networkidle' never fires; wait for the navbar
        page.wait_for_selector(".o_main_navbar", timeout=30000)
        page.wait_for_timeout(2000)

        for name, path, extra in SHOTS:
            try:
                page.goto(BASE + path, wait_until="commit")
                settle(page, extra)
                page.screenshot(path=os.path.join(OUT, name + ".png"))
                print("OK  ", name)
            except Exception as e:
                print("FAIL", name, "->", repr(e)[:120])
        browser.close()


if __name__ == "__main__":
    main()
