# -*- coding: utf-8 -*-
# Extra seed for the Sudan medical-supply ERP demo: role users, payments,
# extra invoices for aged reports, reordering rules, a draft RFQ, and a
# best-effort bank statement for the reconciliation showcase.
#
# Run AFTER scripts/seed_medsupply.py with:
#   odoo shell -d erpmedsupply --no-http < scripts/seed_more.py
# Every section is independently guarded so the script is safe to re-run.

from datetime import date, timedelta

def out(msg):
    print("[SEED+] %s" % msg)

company = env.company
Partner = env["res.partner"]
Move = env["account.move"]
Journal = env["account.journal"]

def P(code):
    return env["product.product"].search([("default_code", "=", code)], limit=1)

def partner(name):
    return Partner.search([("name", "=", name)], limit=1)

sdg = env["res.currency"].search([("name", "=", "SDG")], limit=1)
bank_sdg = Journal.search([("code", "=", "BNKSD")], limit=1)
cash_sdg = Journal.search([("code", "=", "CSHSD")], limit=1)
cus_hosp = partner("Khartoum Teaching Hospital")
cus_clinic = partner("Omdurman Family Clinic")
cus_redc = partner("Sudanese Red Crescent")
cus_pharm = partner("Bahri Community Pharmacy")
sup_local = partner("Nile Medical Supplies Co.")
sup_gulf = partner("Gulf MedTrade FZE (USD)")
today = date(2026, 6, 9)

# ============================================================ 0. FISCAL CONSISTENCY
# generic_coa ships its 15% taxes with country_id = US, while the company is in
# Sudan. Direct (non-SO) invoice posts then fail Odoo's tax/fiscal-country check.
# Align the fiscal country and the sale/purchase taxes (and their tax group) to
# Sudan so the demo is fiscally consistent. Idempotent.
sudan = env["res.country"].search([("code", "=", "SD")], limit=1)
try:
    if sudan and "account_fiscal_country_id" in company._fields \
            and company.account_fiscal_country_id.id != sudan.id:
        company.account_fiscal_country_id = sudan.id
    biz_taxes = env["account.tax"].search(
        ["|", ("type_tax_use", "=", "sale"), ("type_tax_use", "=", "purchase")])
    for t in biz_taxes:
        if sudan and t.country_id.id != sudan.id:
            g = t.tax_group_id
            if g and g.country_id.id != sudan.id:
                g.country_id = sudan.id
            t.write({"country_id": sudan.id, "tax_group_id": g.id})
    env.cr.commit()
    out("Fiscal country + %d taxes aligned to Sudan." % len(biz_taxes))
except Exception as e:
    out("Fiscal alignment skipped: %s" % e)

# ============================================================ 1. ROLE USERS
# One representative user per business role, so "Users & Companies" and the
# roles/permissions chapter can be documented and screenshotted concretely.
Users = env["res.users"]

def grp(xmlid):
    try:
        return env.ref(xmlid).id
    except Exception:
        return None

ROLE_USERS = [
    ("Amira Hassan (Procurement Officer)", "amira",
     ["purchase.group_purchase_user", "stock.group_stock_user",
      "account.group_account_invoice"]),
    ("Khalid Osman (Sales Representative)", "khalid",
     ["sales_team.group_sale_salesman_all_leads", "stock.group_stock_user"]),
    ("Sara Ahmed (Warehouse Keeper)", "sara",
     ["stock.group_stock_manager"]),
    ("Mohammed Ali (Accountant)", "mohammed",
     ["account.group_account_user", "purchase.group_purchase_user",
      "sales_team.group_sale_salesman"]),
    ("Layla Ibrahim (General Manager)", "layla",
     ["sales_team.group_sale_manager", "purchase.group_purchase_manager",
      "stock.group_stock_manager", "account.group_account_manager",
      "base.group_system"]),
]

for name, login, group_xmlids in ROLE_USERS:
    if Users.with_context(active_test=False).search([("login", "=", login)], limit=1):
        out("User %s already exists." % login)
        continue
    gids = [g for g in (grp(x) for x in group_xmlids) if g]
    try:
        u = Users.create({
            "name": name,
            "login": login,
            "password": "demo1234",
            "lang": "en_US",
            "groups_id": [(6, 0, gids)],
        })
        out("Created user %s (%s) with %d role groups." % (login, name, len(gids)))
    except Exception as e:
        out("User %s creation failed: %s" % (login, e))
env.cr.commit()
out("=== role users committed ===")

# ============================================================ 2. PAYMENTS
# Register payments against the two existing posted customer invoices, one
# through the bank journal and one through the cash safe, plus the vendor bill.
def register_payment(move, journal, when):
    if not move or not journal:
        return
    if move.payment_state in ("paid", "in_payment", "reversed"):
        out("  %s already %s — skip payment." % (move.name, move.payment_state))
        return
    try:
        wiz = env["account.payment.register"].with_context(
            active_model="account.move", active_ids=move.ids
        ).create({"journal_id": journal.id, "payment_date": when})
        wiz._create_payments()
        out("  Paid %s via %s -> state=%s" % (move.name, journal.name, move.payment_state))
    except Exception as e:
        out("  Payment for %s failed: %s" % (move.name, e))

inv1 = Move.search([("move_type", "=", "out_invoice"), ("state", "=", "posted"),
                    ("partner_id", "=", cus_hosp.id)], order="id", limit=1)
inv2 = Move.search([("move_type", "=", "out_invoice"), ("state", "=", "posted"),
                    ("partner_id", "=", cus_clinic.id)], order="id", limit=1)
register_payment(inv1, bank_sdg, today)
register_payment(inv2, cash_sdg, today)

bill1 = Move.search([("move_type", "=", "in_invoice"), ("state", "=", "posted")],
                    order="id", limit=1)
if bill1:
    register_payment(bill1, bank_sdg, today)
env.cr.commit()
out("=== payments committed ===")

# ============================================================ 2b. VENDOR BILLS
# Post the draft vendor bill from PO1 and pay it; add a posted, unpaid USD bill
# from Gulf MedTrade so Aged Payable and multi-currency payables have data.
usd = env["res.currency"].search([("name", "=", "USD")], limit=1)
draft_bill = Move.search([("move_type", "=", "in_invoice"), ("state", "=", "draft")],
                         order="id", limit=1)
if draft_bill:
    try:
        if not draft_bill.invoice_date:
            draft_bill.invoice_date = date(2026, 5, 10)
        draft_bill.invoice_date_due = date(2026, 6, 9)
        draft_bill.action_post()
        out("Posted vendor bill %s (%s)." % (draft_bill.name, draft_bill.amount_total))
        register_payment(draft_bill, bank_sdg, today)
    except Exception as e:
        out("Posting/paying draft vendor bill failed: %s" % e)

if not Move.search([("move_type", "=", "in_invoice"), ("ref", "=", "DEMO-AP-USD")], limit=1):
    try:
        gbill = Move.create({
            "move_type": "in_invoice",
            "partner_id": sup_gulf.id,
            "currency_id": usd.id if usd else False,
            "invoice_date": date(2026, 5, 28),
            "invoice_date_due": date(2026, 6, 27),
            "ref": "DEMO-AP-USD",
            "invoice_line_ids": [
                (0, 0, {"product_id": P("MED-INSULIN").id, "quantity": 30, "price_unit": 14.0}),
            ],
        })
        gbill.action_post()
        out("Posted USD vendor bill %s total=%s %s (unpaid)." % (
            gbill.name, gbill.amount_total, gbill.currency_id.name))
    except Exception as e:
        out("USD vendor bill failed: %s" % e)
env.cr.commit()
out("=== vendor bills committed ===")

# ============================================================ 3. EXTRA INVOICES
# A few more posted customer invoices with staggered (some overdue) due dates so
# the Aged Receivable report and follow-up features have something to show.
def tax_for(company):
    # Reuse the exact sale tax already posted on an existing customer invoice
    # (guaranteed compatible with the fiscal country); fall back to a country-
    # matched sale tax, else no tax.
    existing = Move.search([("move_type", "=", "out_invoice"), ("state", "=", "posted")],
                           order="id", limit=1)
    used = existing.invoice_line_ids.filtered(lambda l: l.tax_ids)[:1].tax_ids if existing else None
    if used:
        return [(6, 0, used.ids)]
    fc = company.account_fiscal_country_id or company.country_id
    dom = [("type_tax_use", "=", "sale"), ("company_id", "=", company.id)]
    if fc:
        dom += ["|", ("country_id", "=", fc.id), ("country_id", "=", False)]
    t = env["account.tax"].search(dom, limit=1)
    return [(6, 0, t.ids)] if t else False

def make_invoice(cust, lines, inv_date, due_date, marker_ref):
    if Move.search([("move_type", "=", "out_invoice"), ("ref", "=", marker_ref)], limit=1):
        out("  Invoice %s already present — skip." % marker_ref)
        return None
    il = []
    sale_tax = tax_for(company)
    for prod, qty, price in lines:
        v = {"product_id": prod.id, "quantity": qty, "price_unit": price}
        if sale_tax:
            v["tax_ids"] = sale_tax
        il.append((0, 0, v))
    mv = Move.create({
        "move_type": "out_invoice",
        "partner_id": cust.id,
        "invoice_date": inv_date,
        "invoice_date_due": due_date,
        "ref": marker_ref,
        "invoice_line_ids": il,
    })
    mv.action_post()
    out("  Posted %s (%s) total=%s due=%s" % (mv.name, marker_ref, mv.amount_total, due_date))
    return mv

make_invoice(cus_redc,
             [(P("MED-AMOX-250"), 30, 23000), (P("CON-IVCAN"), 10, 38600)],
             date(2026, 3, 20), date(2026, 4, 19), "DEMO-AGED-1")   # overdue
make_invoice(cus_pharm,
             [(P("MED-PARA-500"), 60, 11500), (P("CON-N95"), 12, 48000)],
             date(2026, 4, 25), date(2026, 5, 25), "DEMO-AGED-2")   # overdue
make_invoice(cus_hosp,
             [(P("MED-ANTISEP"), 40, 14800), (P("CON-SYR-5"), 25, 20600)],
             date(2026, 6, 1), date(2026, 7, 1), "DEMO-AGED-3")     # current
env.cr.commit()
out("=== extra invoices committed ===")

# ============================================================ 4. REORDERING RULES
Orderpoint = env["stock.warehouse.orderpoint"]
wh_main = env["stock.warehouse"].search([("code", "=", "KRT")], limit=1)
stock_loc = wh_main.lot_stock_id if wh_main else False

def make_orderpoint(prod, mn, mx):
    if not prod or not stock_loc:
        return
    if Orderpoint.search([("product_id", "=", prod.id), ("location_id", "=", stock_loc.id)], limit=1):
        out("  Orderpoint for %s exists — skip." % prod.default_code)
        return
    try:
        Orderpoint.create({"product_id": prod.id, "location_id": stock_loc.id,
                           "product_min_qty": mn, "product_max_qty": mx})
        out("  Reordering rule: %s min=%s max=%s" % (prod.default_code, mn, mx))
    except Exception as e:
        out("  Orderpoint for %s failed: %s" % (prod.default_code, e))

make_orderpoint(P("MED-PARA-500"), 50, 200)
make_orderpoint(P("MED-INSULIN"), 20, 80)
make_orderpoint(P("CON-GLOVES"), 30, 120)
env.cr.commit()
out("=== reordering rules committed ===")

# ============================================================ 5. DRAFT RFQ
# A draft purchase order (RFQ) so the purchasing pipeline shows a live draft.
PO = env["purchase.order"]
if not PO.search([("partner_id", "=", sup_local.id), ("state", "=", "draft")], limit=1):
    try:
        PO.create({
            "partner_id": sup_local.id,
            "order_line": [
                (0, 0, {"product_id": P("MED-PARA-500").id, "product_qty": 100, "price_unit": 1200}),
                (0, 0, {"product_id": P("MED-ANTISEP").id, "product_qty": 60, "price_unit": 1500}),
            ],
        })
        out("Draft RFQ for Nile Medical Supplies created.")
    except Exception as e:
        out("Draft RFQ failed: %s" % e)
else:
    out("Draft RFQ already present.")
env.cr.commit()

# ============================================================ 6. BANK STATEMENT (best effort)
# Unreconciled bank-statement line to showcase the reconciliation screen.
try:
    Stmt = env["account.bank.statement"]
    if bank_sdg and not Stmt.search([("name", "=", "STMT/2026/06/KRT")], limit=1):
        # statement amounts follow the actual posted invoice totals (price-scale safe)
        amt_hosp = inv1.amount_total if inv1 else 0.0
        amt_clinic = inv2.amount_total if inv2 else 0.0
        st = Stmt.create({
            "name": "STMT/2026/06/KRT",
            "journal_id": bank_sdg.id,
            "line_ids": [
                # set journal_id on each line so it lands on BNKSD, not the
                # generic default bank journal (statement.journal follows lines)
                (0, 0, {"payment_ref": "Transfer - Khartoum Teaching Hospital",
                        "amount": amt_hosp, "partner_id": cus_hosp.id,
                        "date": today, "journal_id": bank_sdg.id}),
                (0, 0, {"payment_ref": "Transfer - Omdurman Family Clinic",
                        "amount": amt_clinic, "partner_id": cus_clinic.id,
                        "date": today, "journal_id": bank_sdg.id}),
            ],
        })
        out("Bank statement %s created (for reconciliation demo)." % st.name)
    else:
        out("Bank statement already present or no bank journal.")
    env.cr.commit()
except Exception as e:
    out("Bank statement skipped: %s" % e)

# ============================================================ 7. DECLUTTER JOURNALS
# The accounting install auto-creates generic "Bank"/"Cash" journals in addition
# to our named ones; deactivate them if empty so the dashboard is clean.
try:
    def _empty(j):
        return (Move.search_count([("journal_id", "=", j.id)]) == 0
                and env["account.payment"].search_count([("journal_id", "=", j.id)]) == 0
                and env["account.bank.statement"].search_count([("journal_id", "=", j.id)]) == 0)
    for code in ("BNK1", "CSH1"):
        j = Journal.search([("code", "=", code)], limit=1)
        if j and _empty(j):
            j.active = False
            out("Deactivated empty generic journal %s." % code)
    env.cr.commit()
except Exception as e:
    out("Journal declutter skipped: %s" % e)

# ============================================================ SUMMARY
out("---------------- EXTRA SEED SUMMARY ----------------")
out("Users (total)      : %d" % env["res.users"].search_count([("share", "=", False)]))
out("Customer invoices  : %d posted" % Move.search_count(
    [("move_type", "=", "out_invoice"), ("state", "=", "posted")]))
out("Payments           : %d" % env["account.payment"].search_count([]))
out("Reordering rules   : %d" % env["stock.warehouse.orderpoint"].search_count([]))
out("Purchase orders    : %d (incl. drafts)" % env["purchase.order"].search_count([]))
out("Bank statements    : %d" % env["account.bank.statement"].search_count([]))
out("DONE (extra seed).")
