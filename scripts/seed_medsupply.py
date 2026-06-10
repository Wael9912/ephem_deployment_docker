# -*- coding: utf-8 -*-
# Seed script for the Sudan medical-supply ERP demo (Odoo 18 Community).
# Run with:  odoo shell -d erpmedsupply --no-http < scripts/seed_medsupply.py
# Idempotent-ish: bails early if it has already seeded (marker partner present).

import logging
from datetime import date, timedelta

_logger = logging.getLogger("seed_medsupply")

def out(msg):
    print("[SEED] %s" % msg)

company = env.company
Partner = env["res.partner"]

# ---------------------------------------------------------------- guard
if Partner.search([("name", "=", "Khartoum Teaching Hospital")], limit=1):
    out("Demo data already present — nothing to do.")
else:
    # ============================================================ PHASE A
    # ---- Company / country -------------------------------------------
    sudan = env["res.country"].search([("code", "=", "SD")], limit=1)
    company.write({
        "name": "Sudan MedSupply Co.",
        "city": "Khartoum",
        "country_id": sudan.id if sudan else False,
    })
    out("Company: %s  country=%s" % (company.name, company.country_id.name))

    # ---- Currencies: SDG (base) + USD (reference) --------------------
    Currency = env["res.currency"]
    sdg = Currency.with_context(active_test=False).search([("name", "=", "SDG")], limit=1)
    usd = Currency.with_context(active_test=False).search([("name", "=", "USD")], limit=1)
    if not sdg:
        sdg = Currency.create({"name": "SDG", "symbol": "ج.س", "active": True})
    sdg.active = True
    usd.active = True
    out("Currencies active: SDG=%s USD=%s" % (sdg.id, usd.id))

    # ---- Chart of accounts (needed for invoices/journals) -----------
    ChartTemplate = env["account.chart.template"]
    has_chart = env["account.account"].search_count([("company_ids", "in", company.id)]) \
        if "company_ids" in env["account.account"]._fields \
        else env["account.account"].search_count([("company_id", "=", company.id)])
    if not has_chart:
        try:
            ChartTemplate.try_loading("generic_coa", company=company, install_demo=False)
            out("Loaded generic_coa chart of accounts.")
        except Exception as e:
            mapping = ChartTemplate._get_chart_template_mapping()
            code = next(iter(mapping)) if mapping else None
            out("generic_coa failed (%s); falling back to %s" % (e, code))
            if code:
                ChartTemplate.try_loading(code, company=company, install_demo=False)
    else:
        out("Chart of accounts already present.")

    # ---- Force base currency to SDG ---------------------------------
    company.currency_id = sdg.id
    out("Company base currency set to SDG.")

    # ---- Force all pricelists to SDG --------------------------------
    # The default pricelist is created in the chart-template currency (USD)
    # at install time; domestic sales must be in SDG, and the sale order's
    # currency follows its pricelist.
    plists = env["product.pricelist"].search([])
    if plists:
        plists.write({"currency_id": sdg.id})
    out("All pricelists set to SDG (%d)." % len(plists))

    # ---- Enable multi-currency + inventory groups -------------------
    settings_vals = {
        "group_multi_currency": True,
        "group_stock_multi_locations": True,
        "group_stock_production_lot": True,
        "group_uom": True,
    }
    cfg = env["res.config.settings"].create(settings_vals)
    cfg.execute()
    out("Enabled: multi-currency, multi-locations, lots, UoM.")

    # ---- USD exchange-rate history (1 USD = N SDG) -------------------
    # Odoo's canonical `rate` field is foreign-per-company (USD per 1 SDG),
    # so 1 USD = N SDG is stored as rate = 1/N. Setting `company_rate`
    # directly inverts the conversion on this build (1 USD would read as
    # 1/N SDG), so we always write the `rate` field.
    Rate = env["res.currency.rate"]
    # Realistic Sudanese-pound depreciation, ending at the real ~4,500 SDG/USD.
    usd_history = [
        ("2025-06-01", 2400.0),
        ("2025-09-01", 3000.0),
        ("2026-01-01", 3600.0),
        ("2026-04-01", 4200.0),
        ("2026-06-01", 4500.0),
    ]
    for d, sdg_per_usd in usd_history:
        existing = Rate.search([("currency_id", "=", usd.id), ("name", "=", d),
                                ("company_id", "=", company.id)], limit=1)
        if existing:
            continue
        vals = {"currency_id": usd.id, "name": d, "company_id": company.id,
                "rate": 1.0 / sdg_per_usd}
        Rate.create(vals)
    out("Seeded %d USD rate records (1 USD = 600..700 SDG over time)." % len(usd_history))

    # ---- Units of measure ------------------------------------------
    uom_unit = env.ref("uom.product_uom_unit")

    # ---- Product categories: FIFO costing + FEFO removal -----------
    Category = env["product.category"]
    fefo = env["product.removal"].search([("method", "=", "fefo")], limit=1)

    def make_cat(name):
        cat = Category.search([("name", "=", name)], limit=1)
        if not cat:
            cat = Category.create({"name": name})
        vals = {"property_cost_method": "fifo"}
        # manual_periodic keeps the demo robust without configuring valuation
        # accounts; flip to 'real_time' after setting stock accounts.
        vals["property_valuation"] = "manual_periodic"
        if fefo:
            vals["removal_strategy_id"] = fefo.id
        cat.write(vals)
        return cat

    cat_pharma = make_cat("Pharmaceuticals")
    cat_consum = make_cat("Medical Consumables")
    cat_device = make_cat("Medical Devices")
    out("Categories set (FIFO costing, FEFO removal where available).")

    # ---- Warehouses -------------------------------------------------
    Warehouse = env["stock.warehouse"]
    wh_main = Warehouse.search([("company_id", "=", company.id)], limit=1)
    if wh_main:
        wh_main.write({"name": "Khartoum Central Warehouse", "code": "KRT"})
    else:
        wh_main = Warehouse.create({"name": "Khartoum Central Warehouse",
                                    "code": "KRT", "company_id": company.id})
    wh_port = Warehouse.search([("code", "=", "PRT")], limit=1)
    if not wh_port:
        wh_port = Warehouse.create({"name": "Port Sudan Warehouse",
                                    "code": "PRT", "company_id": company.id})
    out("Warehouses: %s, %s" % (wh_main.name, wh_port.name))

    # ---- Internal sub-locations (cold chain / quarantine) ----------
    Location = env["stock.location"]
    def sub_loc(name, parent):
        loc = Location.search([("name", "=", name), ("location_id", "=", parent.id)], limit=1)
        if not loc:
            loc = Location.create({"name": name, "location_id": parent.id, "usage": "internal"})
        return loc
    loc_cold = sub_loc("Cold Storage (2-8C)", wh_main.lot_stock_id)
    loc_quar = sub_loc("Quarantine", wh_main.lot_stock_id)
    loc_exp = sub_loc("Expired / Damaged", wh_main.lot_stock_id)
    out("Sub-locations: Cold Storage, Quarantine, Expired/Damaged.")

    # ---- Products ---------------------------------------------------
    Product = env["product.product"]
    today = date(2026, 6, 9)

    def make_product(name, ref, category, cost, price, tracking, expiry_days, cold=False):
        p = Product.search([("default_code", "=", ref)], limit=1)
        if p:
            return p
        vals = {
            "name": name,
            "default_code": ref,
            "type": "consu",
            "categ_id": category.id,
            "uom_id": uom_unit.id,
            "uom_po_id": uom_unit.id,
            "standard_price": cost,
            "list_price": price,
            "tracking": tracking,
        }
        if "is_storable" in Product._fields:
            vals["is_storable"] = True
        if tracking == "lot" and "use_expiration_date" in Product._fields:
            vals["use_expiration_date"] = True
            vals["expiration_time"] = expiry_days
        return Product.create(vals)

    # Prices in SDG, set for the real ~4,500 SDG/USD economy. Imported items
    # (insulin, BP monitor) are bought in USD; their SDG cost is re-derived by the
    # receipt at 4,500 (insulin 14*4500=63,000; BP monitor 42*4500=189,000) — the
    # seed cost below matches so the product form reads sensibly either way.
    P = {}
    P["para"] = make_product("Paracetamol 500mg Tablets (100s)", "MED-PARA-500", cat_pharma, 7700, 11500, "lot", 730)
    P["amox"] = make_product("Amoxicillin 250mg Capsules (100s)", "MED-AMOX-250", cat_pharma, 16000, 23000, "lot", 540)
    P["insulin"] = make_product("Insulin Vial 10ml", "MED-INSULIN", cat_pharma, 63000, 90000, "lot", 365, cold=True)
    P["antisep"] = make_product("Antiseptic Solution 500ml", "MED-ANTISEP", cat_pharma, 9600, 14800, "lot", 365)
    P["gloves"] = make_product("Surgical Gloves (Box of 100)", "CON-GLOVES", cat_consum, 19300, 29000, "lot", 1095)
    P["mask"] = make_product("N95 Face Mask (Box of 20)", "CON-N95", cat_consum, 32000, 48000, "lot", 1460)
    P["syringe"] = make_product("Syringe 5ml (Box of 100)", "CON-SYR-5", cat_consum, 12900, 20600, "lot", 1825)
    P["cannula"] = make_product("IV Cannula 18G (Box of 50)", "CON-IVCAN", cat_consum, 25700, 38600, "lot", 1460)
    P["bpmon"] = make_product("Digital Blood Pressure Monitor", "DEV-BPMON", cat_device, 189000, 285000, "none", 0)
    P["thermo"] = make_product("Digital Thermometer", "DEV-THERMO", cat_device, 22500, 35400, "none", 0)
    out("Created %d medical products." % len(P))

    # ---- Cold-chain putaway: insulin -> Cold Storage ----------------
    try:
        env["stock.putaway.rule"].create({
            "product_id": P["insulin"].id,
            "location_in_id": wh_main.lot_stock_id.id,
            "location_out_id": loc_cold.id,
        })
        out("Putaway rule: Insulin -> Cold Storage.")
    except Exception as e:
        out("Putaway rule skipped: %s" % e)

    # ---- Suppliers --------------------------------------------------
    def make_partner(name, supplier=False, customer=False, currency=None, city="Khartoum"):
        p = Partner.search([("name", "=", name)], limit=1)
        if not p:
            vals = {"name": name, "company_type": "company", "city": city,
                    "country_id": sudan.id if sudan else False,
                    "supplier_rank": 1 if supplier else 0,
                    "customer_rank": 1 if customer else 0}
            p = Partner.create(vals)
        if currency:
            if "property_purchase_currency_id" in Partner._fields:
                p.property_purchase_currency_id = currency.id
        return p

    sup_local = make_partner("Nile Medical Supplies Co.", supplier=True)
    sup_khpharma = make_partner("Khartoum Pharma Imports", supplier=True)
    sup_gulf = make_partner("Gulf MedTrade FZE (USD)", supplier=True, currency=usd, city="Dubai")
    if sudan and sup_gulf:
        uae = env["res.country"].search([("code", "=", "AE")], limit=1)
        if uae:
            sup_gulf.country_id = uae.id
    out("Suppliers: Nile, Khartoum Pharma, Gulf MedTrade (USD).")

    # ---- Customers --------------------------------------------------
    cus_hosp = make_partner("Khartoum Teaching Hospital", customer=True)
    cus_clinic = make_partner("Omdurman Family Clinic", customer=True, city="Omdurman")
    cus_redc = make_partner("Sudanese Red Crescent", customer=True)
    cus_pharm = make_partner("Bahri Community Pharmacy", customer=True, city="Bahri")
    out("Customers: Teaching Hospital, Omdurman Clinic, Red Crescent, Bahri Pharmacy.")

    # ---- Vendor pricelists (supplierinfo) --------------------------
    SupplierInfo = env["product.supplierinfo"]
    def vendor_price(product, vendor, price, currency=None, delay=7):
        if SupplierInfo.search([("partner_id", "=", vendor.id),
                                ("product_tmpl_id", "=", product.product_tmpl_id.id)], limit=1):
            return
        vals = {"partner_id": vendor.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "price": price, "delay": delay, "min_qty": 1}
        if currency and "currency_id" in SupplierInfo._fields:
            vals["currency_id"] = currency.id
        SupplierInfo.create(vals)
    vendor_price(P["para"], sup_local, 7700)
    vendor_price(P["amox"], sup_local, 16000)
    vendor_price(P["antisep"], sup_khpharma, 9600)
    vendor_price(P["gloves"], sup_khpharma, 19300)
    vendor_price(P["insulin"], sup_gulf, 14.0, currency=usd, delay=21)   # priced in USD
    vendor_price(P["bpmon"], sup_gulf, 42.0, currency=usd, delay=21)     # priced in USD
    out("Vendor pricelists set (Gulf MedTrade priced in USD).")

    # ---- Banks + journals (bank accounts + cash 'money safe') ------
    Bank = env["res.bank"]
    def make_bank(name, bic):
        b = Bank.search([("name", "=", name)], limit=1)
        if not b:
            b = Bank.create({"name": name, "bic": bic})
        return b
    bok = make_bank("Bank of Khartoum", "BKHTSDKH")
    fib = make_bank("Faisal Islamic Bank of Sudan", "FIBSSDKH")

    Journal = env["account.journal"]
    def make_journal(name, code, jtype, currency=None):
        j = Journal.search([("code", "=", code), ("company_id", "=", company.id)], limit=1)
        if not j:
            vals = {"name": name, "code": code, "type": jtype, "company_id": company.id}
            if currency:
                vals["currency_id"] = currency.id
            j = Journal.create(vals)
        elif currency:
            j.currency_id = currency.id
        return j
    j_bank_sdg = make_journal("Bank of Khartoum (SDG)", "BNKSD", "bank")
    j_bank_usd = make_journal("USD Bank Account", "BNKUS", "bank", currency=usd)
    j_safe_sdg = make_journal("Main Cash Safe (SDG)", "CSHSD", "cash")
    j_safe_usd = make_journal("USD Cash Safe", "CSHUS", "cash", currency=usd)
    out("Journals: 2 bank (SDG/USD) + 2 cash safes (SDG/USD).")

    env.cr.commit()
    out("=== PHASE A committed (config + master data) ===")

    # ============================================================ PHASE B
    # ---- Helper: receive a confirmed PO with lots + expiry ---------
    def assign_lots_and_validate_receipt(picking, lot_prefix):
        picking.action_confirm()
        picking.action_assign()
        for i, move in enumerate(picking.move_ids):
            qty = move.product_uom_qty
            move.move_line_ids.unlink()
            ml_vals = {
                "move_id": move.id,
                "picking_id": picking.id,
                "product_id": move.product_id.id,
                "product_uom_id": move.product_uom.id,
                "location_id": move.location_id.id,
                "location_dest_id": move.location_dest_id.id,
                "quantity": qty,
            }
            if move.product_id.tracking == "lot":
                ml_vals["lot_name"] = "%s-%02d" % (lot_prefix, i + 1)
                if "expiration_date" in env["stock.move.line"]._fields:
                    days = move.product_id.expiration_time or 365
                    ml_vals["expiration_date"] = today + timedelta(days=days)
            env["stock.move.line"].create(ml_vals)
            move.picked = True
        res = picking.with_context(skip_backorder=True, skip_sms=True).button_validate()
        return res

    # ---- Purchase 1: local supplier (SDG) --------------------------
    PO = env["purchase.order"]
    po1 = PO.create({
        "partner_id": sup_local.id,
        "order_line": [
            (0, 0, {"product_id": P["para"].id, "product_qty": 200, "price_unit": 7700}),
            (0, 0, {"product_id": P["amox"].id, "product_qty": 150, "price_unit": 16000}),
            (0, 0, {"product_id": P["antisep"].id, "product_qty": 100, "price_unit": 9600}),
        ],
    })
    po1.button_confirm()
    for pk in po1.picking_ids:
        assign_lots_and_validate_receipt(pk, "LOT-NILE")
    bill1 = po1.action_create_invoice()
    out("PO1 %s confirmed, received, billed. State=%s" % (po1.name, po1.state))

    # ---- Purchase 2: Gulf MedTrade in USD --------------------------
    po2 = PO.create({
        "partner_id": sup_gulf.id,
        "currency_id": usd.id,
        "order_line": [
            (0, 0, {"product_id": P["insulin"].id, "product_qty": 50, "price_unit": 14.0}),
            (0, 0, {"product_id": P["bpmon"].id, "product_qty": 10, "price_unit": 42.0}),
        ],
    })
    po2.button_confirm()
    for pk in po2.picking_ids:
        assign_lots_and_validate_receipt(pk, "LOT-GULF")
    out("PO2 %s (USD) confirmed & received. Amount=%s %s" % (
        po2.name, po2.amount_total, po2.currency_id.name))

    # ---- Internal transfer: insulin -> Cold Storage (cold chain) ---
    itype = env["stock.picking.type"].search(
        [("code", "=", "internal"), ("warehouse_id", "=", wh_main.id)], limit=1)
    ins_q = env["stock.quant"].search(
        [("product_id", "=", P["insulin"].id),
         ("location_id", "=", wh_main.lot_stock_id.id),
         ("quantity", ">", 0)], limit=1)
    if itype and ins_q:
        tr = env["stock.picking"].create({
            "picking_type_id": itype.id,
            "location_id": wh_main.lot_stock_id.id,
            "location_dest_id": loc_cold.id,
            "move_ids": [(0, 0, {
                "name": "Insulin to Cold Storage",
                "product_id": P["insulin"].id,
                "product_uom_qty": ins_q.quantity,
                "product_uom": P["insulin"].uom_id.id,
                "location_id": wh_main.lot_stock_id.id,
                "location_dest_id": loc_cold.id,
            })],
        })
        tr.action_confirm()
        tr.action_assign()
        for move in tr.move_ids:
            move.picked = True
        tr.with_context(skip_backorder=True, skip_sms=True).button_validate()
        out("Internal transfer %s: Insulin -> Cold Storage." % tr.name)

    # ---- Receive consumables so we have sellable stock -------------
    po3 = PO.create({
        "partner_id": sup_khpharma.id,
        "order_line": [
            (0, 0, {"product_id": P["gloves"].id, "product_qty": 80, "price_unit": 19300}),
            (0, 0, {"product_id": P["mask"].id, "product_qty": 60, "price_unit": 32000}),
            (0, 0, {"product_id": P["syringe"].id, "product_qty": 120, "price_unit": 12900}),
        ],
    })
    po3.button_confirm()
    for pk in po3.picking_ids:
        assign_lots_and_validate_receipt(pk, "LOT-KHP")
    out("PO3 %s confirmed & received." % po3.name)

    env.cr.commit()
    out("=== Purchases committed ===")

    # ---- Sales: deliver (FEFO) + invoice ---------------------------
    def validate_delivery(picking):
        picking.action_confirm()
        picking.action_assign()
        for move in picking.move_ids:
            if not move.move_line_ids:
                move.quantity = move.product_uom_qty
            move.picked = True
        return picking.with_context(skip_backorder=True, skip_sms=True).button_validate()

    SO = env["sale.order"]
    so1 = SO.create({
        "partner_id": cus_hosp.id,
        "order_line": [
            (0, 0, {"product_id": P["para"].id, "product_uom_qty": 50, "price_unit": 11500}),
            (0, 0, {"product_id": P["gloves"].id, "product_uom_qty": 20, "price_unit": 29000}),
            (0, 0, {"product_id": P["syringe"].id, "product_uom_qty": 30, "price_unit": 20600}),
        ],
    })
    so1.action_confirm()
    for pk in so1.picking_ids:
        validate_delivery(pk)
    inv1 = so1._create_invoices()
    inv1.action_post()
    out("SO1 %s confirmed, delivered, invoiced %s (%s). Inv state=%s" % (
        so1.name, inv1.name, inv1.amount_total, inv1.state))

    so2 = SO.create({
        "partner_id": cus_clinic.id,
        "order_line": [
            (0, 0, {"product_id": P["amox"].id, "product_uom_qty": 40, "price_unit": 23000}),
            (0, 0, {"product_id": P["mask"].id, "product_uom_qty": 15, "price_unit": 48000}),
        ],
    })
    so2.action_confirm()
    for pk in so2.picking_ids:
        validate_delivery(pk)
    inv2 = so2._create_invoices()
    inv2.action_post()
    out("SO2 %s confirmed, delivered, invoiced %s. Inv state=%s" % (
        so2.name, inv2.name, inv2.state))

    # ---- A draft quotation (pipeline demo) -------------------------
    SO.create({
        "partner_id": cus_redc.id,
        "order_line": [
            (0, 0, {"product_id": P["insulin"].id, "product_uom_qty": 10, "price_unit": 90000}),
            (0, 0, {"product_id": P["bpmon"].id, "product_uom_qty": 3, "price_unit": 285000}),
        ],
    })
    out("Draft quotation for Sudanese Red Crescent created.")

    env.cr.commit()
    out("=== PHASE B committed (purchases + sales) ===")

# ================================================================ SUMMARY
out("---------------- SUMMARY ----------------")
out("Base currency      : %s" % company.currency_id.name)
out("Active currencies  : %s" % ", ".join(
    env["res.currency"].search([("active", "=", True)]).mapped("name")))
out("USD rate records   : %d" % env["res.currency.rate"].search_count(
    [("currency_id.name", "=", "USD")]))
out("Warehouses         : %d" % env["stock.warehouse"].search_count([]))
out("Products           : %d" % env["product.product"].search_count(
    [("default_code", "like", "MED-")]) and env["product.product"].search_count(
    [("default_code", "!=", False)]))
out("Customers          : %d" % env["res.partner"].search_count([("customer_rank", ">", 0)]))
out("Suppliers          : %d" % env["res.partner"].search_count([("supplier_rank", ">", 0)]))
out("Bank journals      : %d" % env["account.journal"].search_count([("type", "=", "bank")]))
out("Cash safes         : %d" % env["account.journal"].search_count([("type", "=", "cash")]))
out("Purchase orders    : %d" % env["purchase.order"].search_count([]))
out("Sales orders       : %d" % env["sale.order"].search_count([]))
out("Posted cust. invs  : %d" % env["account.move"].search_count(
    [("move_type", "=", "out_invoice"), ("state", "=", "posted")]))
out("----------------------------------------")
out("DONE.")
