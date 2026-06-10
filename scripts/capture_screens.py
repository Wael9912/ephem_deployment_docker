# -*- coding: utf-8 -*-
"""
Capture real screenshots from the running Odoo (erpmedsupply) for the user
manual. Drives a headless Chromium (Playwright), logs in as admin, dismisses
onboarding/tour overlays, deep-links into the actual demo records, and (where
useful) opens a specific notebook tab before shooting.

The Spiffy backend theme is active, so these reflect the real, themed UI.

Usage:
    python3 scripts/capture_screens.py en      # admin lang must be en_US
    python3 scripts/capture_screens.py ar      # admin lang must be ar_001
"""
import os
import sys
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8069"
USER, PWD = "admin", "admin"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANG = sys.argv[1] if len(sys.argv) > 1 else "en"
OUT = os.path.join(ROOT, "docs", "manual", "img", LANG)
os.makedirs(OUT, exist_ok=True)

# resolved demo-record ids (see scripts/get_ids / extract_ground_truth)
ID = dict(tmpl_insulin=3, tmpl_para=1, po_usd=2, po_rfq=4, so_hosp=1, so_draft=3,
          inv_hosp=2, inv_overdue=5, bill_usd=4, pay_in=2, partner_hosp=10,
          partner_gulf=9, journal_bank=9, user_layla=10, usd_ccy=1, wh_main=1,
          lot_insulin=4, stmt=1, receipt=1, delivery=6, cat_pharma=4)


def A(xmlid, rid=None):
    """Deep-link URL for an action (optionally a specific record)."""
    return "/odoo/action-%s%s" % (xmlid, ("/%d" % rid) if rid else "")


# (filename, path, optional notebook-tab index to open before shooting)
SHOTS = [
    # ---- home + dashboards -------------------------------------------------
    ("apps_home",        "/odoo",                                              None),
    ("inventory_overview", "/odoo/inventory",                                  None),
    ("sales_dashboard",  "/odoo/sales",                                        None),
    ("accounting_dashboard", "/odoo/accounting",                              None),
    ("settings_general", A("base_setup.action_general_configuration"),         None),
    # ---- configuration -----------------------------------------------------
    ("company",          A("base.action_res_company_form"),                    None),
    ("currencies_list",  A("base.action_currency_form"),                       None),
    ("currency_usd",     A("base.action_currency_form", ID["usd_ccy"]),        None),
    ("contacts_list",    "/odoo/contacts",                                     None),
    ("contact_customer", A("contacts.action_contacts", ID["partner_hosp"]),    None),
    ("contact_customer_salespurchase", A("contacts.action_contacts", ID["partner_hosp"]), 1),
    ("contact_customer_accounting",    A("contacts.action_contacts", ID["partner_hosp"]), 3),
    ("contact_supplier", A("contacts.action_contacts", ID["partner_gulf"]),    None),
    ("warehouses",       A("stock.action_warehouse_form"),                     None),
    ("locations_list",   A("stock.action_location_form"),                      None),
    ("uom_list",         A("uom.product_uom_form_action"),                     None),
    ("categories_list",  A("product.product_category_action_form"),            None),
    ("journals_list",    A("account.action_account_journal_form"),             None),
    ("journal_bank",     A("account.action_account_journal_form", ID["journal_bank"]), None),
    ("chart_of_accounts", A("account.action_account_form"),                    None),
    ("taxes_list",       A("account.action_tax_form"),                         None),
    # ---- inventory & items -------------------------------------------------
    ("products_list",    A("stock.product_template_action_product"),           None),
    ("product_insulin",  A("stock.product_template_action_product", ID["tmpl_insulin"]), None),
    ("product_insulin_inventory", A("stock.product_template_action_product", ID["tmpl_insulin"]), 3),
    ("product_insulin_purchase",  A("stock.product_template_action_product", ID["tmpl_insulin"]), 2),
    ("lots_list",        A("stock.action_production_lot_form"),                None),
    ("lot_insulin",      A("stock.action_production_lot_form", ID["lot_insulin"]), None),
    ("reordering_rules", A("stock.action_orderpoint"),                         None),
    ("onhand_quants",    A("stock.dashboard_open_quants"),                     None),
    # ---- warehouse operations ---------------------------------------------
    ("transfers_all",    A("stock.action_picking_tree_all"),                   None),
    ("receipt_form",     A("stock.action_picking_tree_all", ID["receipt"]),    None),
    ("delivery_form",    A("stock.action_picking_tree_all", ID["delivery"]),   None),
    # ---- procurement -------------------------------------------------------
    ("purchase_orders",  A("purchase.purchase_form_action"),                   None),
    ("po_usd",           A("purchase.purchase_form_action", ID["po_usd"]),     None),
    ("rfq_list",         A("purchase.purchase_rfq"),                           None),
    ("po_rfq",           A("purchase.purchase_form_action", ID["po_rfq"]),     None),
    # ---- sales -------------------------------------------------------------
    ("quotations_list",  A("sale.action_quotations"),                          None),
    ("sale_orders_list", A("sale.action_orders"),                              None),
    ("sale_order",       A("sale.action_orders", ID["so_hosp"]),               None),
    ("sale_quotation_draft", A("sale.action_orders", ID["so_draft"]),          None),
    # ---- accounting --------------------------------------------------------
    ("customer_invoices_list", A("account.action_move_out_invoice_type"),      None),
    ("customer_invoice", A("account.action_move_out_invoice_type", ID["inv_hosp"]), None),
    ("customer_invoice_overdue", A("account.action_move_out_invoice_type", ID["inv_overdue"]), None),
    ("vendor_bills_list", A("account.action_move_in_invoice_type"),            None),
    ("vendor_bill_usd",  A("account.action_move_in_invoice_type", ID["bill_usd"]), None),
    ("payments_list",    A("account.action_account_payments"),                 None),
    ("payment_form",     A("account.action_account_payments", ID["pay_in"]),   None),
    ("bank_reconcile",   A("account_reconcile_oca.action_bank_statement_line_reconcile"), None),
    ("report_balance_sheet", A("accounting_pdf_reports.action_account_report_bs"), None),
    ("report_aged_receivable", A("accounting_pdf_reports.action_account_aged_receivable"), None),
    # ---- administration / roles -------------------------------------------
    ("users_list",       A("base.action_res_users"),                           None),
    ("user_role",        A("base.action_res_users", ID["user_layla"]),         0),
]

KILL_OVERLAYS = """() => {
  const sels = ['.o_onboarding_container','.o_onboarding','.o-tour-pointer',
    '.o_tooltip','.o_blockUI','.popover','.o_notification_manager .o_notification',
    '.o-mail-ChatWindow','.o_web_studio_upgrade'];
  for (const s of sels) document.querySelectorAll(s).forEach(e => e.remove());
}"""


def settle(page, tab=None):
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
    if tab is not None:
        try:
            tabs = page.locator(".o_notebook .nav-link")
            if tabs.count() > tab:
                tabs.nth(tab).click()
                page.wait_for_timeout(700)
                page.locator(".o_notebook").scroll_into_view_if_needed(timeout=4000)
                page.wait_for_timeout(500)
        except Exception:
            pass
    page.wait_for_timeout(400)


def open_app_drawer(page):
    """Open the Spiffy full-screen app launcher for the home shot."""
    try:
        page.eval_on_selector("a.appDrawerToggle", "e=>e.click()")
        page.wait_for_timeout(1800)
    except Exception:
        pass


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--no-sandbox"])
        ctx = browser.new_context(
            viewport={"width": 1480, "height": 940}, device_scale_factor=2,
            locale="ar-SD" if LANG == "ar" else "en-US")
        page = ctx.new_page()
        page.set_default_timeout(20000)

        # login
        page.goto(BASE + "/web/login?db=erpmedsupply", wait_until="networkidle")
        page.wait_for_selector("input[name=login]", state="visible", timeout=15000)
        page.wait_for_timeout(700)
        page.screenshot(path=os.path.join(OUT, "login.png"))
        page.fill("input[name=login]", USER)
        page.fill("input[name=password]", PWD)
        page.click("button[type=submit]")
        page.wait_for_selector(".o_main_navbar", timeout=30000)
        page.wait_for_timeout(2200)

        ok = fail = 0
        for entry in SHOTS:
            name, path, tab = entry
            try:
                page.goto(BASE + path, wait_until="commit")
                settle(page, tab)
                if name == "apps_home":
                    open_app_drawer(page)
                    try:
                        page.evaluate(KILL_OVERLAYS)
                    except Exception:
                        pass
                page.screenshot(path=os.path.join(OUT, name + ".png"))
                ok += 1
                print("OK  ", name)
            except Exception as e:
                fail += 1
                print("FAIL", name, "->", repr(e)[:110])
        print("---- %s: %d ok, %d failed ----" % (LANG, ok, fail))
        browser.close()


if __name__ == "__main__":
    main()
