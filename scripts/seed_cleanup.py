# -*- coding: utf-8 -*-
# One-time cleanup to bring the live erpmedsupply demo to a consistent, polished
# state for the manual + screenshots. Each section commits independently so a
# later failure never rolls back an earlier fix.
#   A. Restore the coherent USD rate history (600 -> 700 SDG/USD).
#   B. Recreate the USD vendor bill valued at the 700-era rate.
#   C. Put the reconciliation bank statement on "Bank of Khartoum (SDG)".
#   D. Deactivate the empty auto-created generic "Bank"/"Cash" journals.
#
#   odoo shell -d erpmedsupply --no-http < scripts/seed_cleanup.py
from datetime import date

def out(m):
    print("[CLEAN] %s" % m)

company = env.company
J = env["account.journal"]
Move = env["account.move"]
Stmt = env["account.bank.statement"]
usd = env["res.currency"].search([("name", "=", "USD")], limit=1)

# ---- A. USD rate history --------------------------------------------------
try:
    Rate = env["res.currency.rate"]
    Rate.search([("currency_id", "=", usd.id)]).unlink()
    for d, n in [("2025-06-01", 2400.0), ("2025-09-01", 3000.0), ("2026-01-01", 3600.0),
                 ("2026-04-01", 4200.0), ("2026-06-01", 4500.0)]:
        Rate.create({"currency_id": usd.id, "name": d, "company_id": company.id, "rate": 1.0 / n})
    env.cr.commit()
    out("A: USD rates reset (1 USD = %.0f SDG today)." % usd._convert(
        1.0, company.currency_id, company, date(2026, 6, 9)))
except Exception as e:
    env.cr.rollback()
    out("A FAILED: %s" % e)

# ---- B. Recreate the USD vendor bill at the 700-era rate ------------------
try:
    sup_gulf = env["res.partner"].search([("name", "=", "Gulf MedTrade FZE (USD)")], limit=1)
    insulin = env["product.product"].search([("default_code", "=", "MED-INSULIN")], limit=1)
    for m in Move.search([("move_type", "=", "in_invoice"), ("ref", "=", "DEMO-AP-USD")]):
        if m.state == "posted":
            m.button_draft()
        m.unlink()
    gbill = Move.create({
        "move_type": "in_invoice", "partner_id": sup_gulf.id, "currency_id": usd.id,
        "invoice_date": date(2026, 5, 28), "invoice_date_due": date(2026, 6, 27),
        "ref": "DEMO-AP-USD",
        "invoice_line_ids": [(0, 0, {"product_id": insulin.id, "quantity": 30, "price_unit": 14.0})],
    })
    gbill.action_post()
    env.cr.commit()
    out("B: USD vendor bill %s = %s USD recreated at 700-era rate." % (gbill.name, gbill.amount_total))
except Exception as e:
    env.cr.rollback()
    out("B FAILED: %s" % e)

# ---- C. Move the reconciliation statement onto Bank of Khartoum (SDG) -----
try:
    bnksd = J.search([("code", "=", "BNKSD")], limit=1)
    cus_hosp = env["res.partner"].search([("name", "=", "Khartoum Teaching Hospital")], limit=1)
    cus_clinic = env["res.partner"].search([("name", "=", "Omdurman Family Clinic")], limit=1)
    for s in Stmt.search([("name", "=", "STMT/2026/06/KRT")]):
        for line in s.line_ids:
            mv = line.move_id
            if mv:
                partials = (mv.line_ids.mapped("matched_debit_ids")
                            | mv.line_ids.mapped("matched_credit_ids"))
                partials.unlink()
                fulls = mv.line_ids.mapped("full_reconcile_id")
                if fulls:
                    fulls.unlink()
        s.line_ids.unlink()
        s.unlink()
    StLine = env["account.bank.statement.line"]
    def inv_total(partner):
        m = Move.search([("move_type", "=", "out_invoice"), ("state", "=", "posted"),
                         ("partner_id", "=", partner.id)], order="id", limit=1)
        return m.amount_total if m else 0.0
    lines = [(0, 0, {"payment_ref": ref, "amount": amt, "partner_id": p.id,
                     "date": date(2026, 6, 9), "journal_id": bnksd.id})
             for ref, amt, p in [("Transfer - Khartoum Teaching Hospital", inv_total(cus_hosp), cus_hosp),
                                 ("Transfer - Omdurman Family Clinic", inv_total(cus_clinic), cus_clinic)]]
    st = Stmt.create({"name": "STMT/2026/06/KRT", "journal_id": bnksd.id, "line_ids": lines})
    env.cr.commit()
    out("C: statement %s on %s with %d lines." % (st.name, bnksd.name, len(st.line_ids)))
except Exception as e:
    env.cr.rollback()
    out("C FAILED (statement left as-is): %s" % str(e)[:160])

# ---- D. Deactivate empty generic default bank/cash journals ---------------
try:
    def empty(j):
        return (Move.search_count([("journal_id", "=", j.id)]) == 0
                and env["account.payment"].search_count([("journal_id", "=", j.id)]) == 0
                and Stmt.search_count([("journal_id", "=", j.id)]) == 0)
    for code in ("BNK1", "CSH1"):
        j = J.search([("code", "=", code)], limit=1)
        if j and empty(j):
            j.active = False
            out("D: deactivated empty generic journal %s (%s)." % (code, j.name))
        elif j:
            out("D: journal %s not empty — left active." % code)
    env.cr.commit()
except Exception as e:
    env.cr.rollback()
    out("D FAILED: %s" % e)

out("Active bank/cash journals now:")
for j in J.search([("type", "in", ["bank", "cash"])], order="type,code"):
    out("  %-6s %-26s %-5s %s" % (j.code, j.name, j.type, j.currency_id.name or company.currency_id.name))
out("DONE.")
