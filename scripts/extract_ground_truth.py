# -*- coding: utf-8 -*-
# Extract ground-truth UI/data inventories from the running erpmedsupply DB so
# the manual can be written without hallucinating field names, menu paths,
# buttons, or demo figures. Prints one JSON blob between markers to stdout.
#
#   odoo shell -d erpmedsupply --no-http < scripts/extract_ground_truth.py
import json
from lxml import etree

def fields_get(model):
    try:
        return env[model].fields_get()
    except Exception:
        return {}

def form_inventory(model, view_type="form"):
    """Return {fields:[...], buttons:[...], statusbar:[...], pages:[...]} for a model's view."""
    res = {"model": model, "fields": [], "buttons": [], "statusbar_states": [], "smart_buttons": []}
    try:
        view = env[model].get_view(view_type=view_type)
    except Exception as e:
        res["error"] = str(e)[:200]
        return res
    arch = view.get("arch")
    if not arch:
        res["error"] = "no arch"
        return res
    meta = fields_get(model)
    try:
        root = etree.fromstring(arch.encode("utf-8"))
    except Exception as e:
        res["error"] = "parse: %s" % str(e)[:120]
        return res

    def page_of(el):
        p = el.getparent()
        names = []
        while p is not None:
            if p.tag == "page" and p.get("string"):
                names.append(p.get("string"))
            if p.tag == "header":
                names.append("__header__")
            p = p.getparent()
        return names[0] if names else "main"

    seen = set()
    for fld in root.iter("field"):
        name = fld.get("name")
        if not name or name in seen:
            continue
        # skip fields living inside an embedded one2many sub-view's own <field>s? keep top-level + line fields
        seen.add(name)
        m = meta.get(name, {})
        page = page_of(fld)
        # detect smart-button stat fields (inside div.oe_button_box) loosely by invisible? skip
        entry = {
            "name": name,
            "label": fld.get("string") or m.get("string") or name,
            "type": m.get("type"),
            "help": (fld.get("help") or m.get("help") or "").strip()[:300],
            "required": bool(fld.get("required")) or bool(m.get("required")),
            "readonly": bool(fld.get("readonly")),
            "page": page,
        }
        if m.get("selection"):
            try:
                entry["selection"] = [s[1] for s in m["selection"]][:12]
            except Exception:
                pass
        if m.get("relation"):
            entry["relation"] = m["relation"]
        res["fields"].append(entry)

    for btn in root.iter("button"):
        s = btn.get("string")
        if s:
            item = {"label": s, "name": btn.get("name"), "type": btn.get("type"),
                    "class": btn.get("class") or ""}
            if "oe_stat_button" in (btn.get("class") or ""):
                res["smart_buttons"].append(item)
            elif page_of(btn) == "__header__" or btn.getparent().tag == "header":
                res["buttons"].append(item)
            else:
                res["buttons"].append(item)

    # statusbar states (the workflow stages shown top-right)
    for fld in root.iter("field"):
        if fld.get("widget") == "statusbar":
            m = meta.get(fld.get("name"), {})
            if m.get("selection"):
                res["statusbar_states"] = [s[1] for s in m["selection"]]
            break
    return res


# --------------------------------------------------------------- menu tree
def menu_tree():
    Menu = env["ir.ui.menu"].with_context(lang="en_US")
    out = []
    def walk(menu, depth):
        act = menu.action
        act_model = ""
        if act and hasattr(act, "res_model"):
            act_model = act.res_model or ""
        out.append({"depth": depth, "name": menu.name or "", "model": act_model})
        for c in menu.child_id.sorted(lambda m: (m.sequence, m.id)):
            walk(c, depth + 1)
    roots = Menu.search([("parent_id", "=", False)]).sorted(lambda m: (m.sequence, m.id))
    # only business apps relevant to the manual
    keep = {"Sales", "Purchase", "Inventory", "Accounting", "Contacts", "Settings", "Dashboards"}
    for r in roots:
        if r.name in keep:
            walk(r, 0)
    return out


# --------------------------------------------------------------- roles
def roles():
    cats = ["Sales", "Purchase", "Inventory", "Accounting", "Administration",
            "Invoicing", "Contact Creation"]
    Group = env["res.groups"].with_context(lang="en_US")
    data = {}
    for g in Group.search([]):
        cat = g.category_id.name if g.category_id else "Other"
        if cat not in cats:
            continue
        data.setdefault(cat, []).append({
            "name": g.name,
            "members": g.users.filtered(lambda u: not u.share).mapped("login"),
        })
    users = []
    for u in env["res.users"].search([("share", "=", False)], order="id"):
        users.append({"login": u.login, "name": u.name,
                      "groups": u.groups_id.filtered(
                          lambda x: x.category_id.name in cats).mapped(
                          lambda x: "%s/%s" % (x.category_id.name, x.name))})
    return {"categories": data, "users": users}


# --------------------------------------------------------------- demo data
def demo():
    d = {}
    co = env.company
    d["company"] = {"name": co.name, "city": co.city,
                    "country": co.country_id.name,
                    "currency": co.currency_id.name,
                    "fiscal_country": co.account_fiscal_country_id.code if co.account_fiscal_country_id else None}
    d["currencies"] = env["res.currency"].search([("active", "=", True)]).mapped("name")
    d["usd_rates"] = [{"date": str(r.name), "sdg_per_usd": round(1.0 / r.rate, 2) if r.rate else None}
                      for r in env["res.currency.rate"].search([("currency_id.name", "=", "USD")], order="name")]
    d["warehouses"] = [{"name": w.name, "code": w.code} for w in env["stock.warehouse"].search([])]
    d["internal_locations"] = env["stock.location"].search(
        [("usage", "=", "internal"), ("name", "in",
         ["Cold Storage (2-8C)", "Quarantine", "Expired / Damaged"])]).mapped("complete_name")
    d["products"] = [{
        "name": p.name, "ref": p.default_code, "category": p.categ_id.name,
        "cost": p.standard_price, "price": p.list_price, "tracking": p.tracking,
        "expiry": bool(getattr(p, "use_expiration_date", False)),
        "on_hand": p.qty_available,
    } for p in env["product.product"].search([("default_code", "!=", False)], order="default_code")]
    d["customers"] = env["res.partner"].search([("customer_rank", ">", 0)]).mapped("name")
    d["suppliers"] = env["res.partner"].search([("supplier_rank", ">", 0)]).mapped("name")
    d["journals"] = [{"name": j.name, "code": j.code, "type": j.type,
                      "currency": j.currency_id.name or co.currency_id.name}
                     for j in env["account.journal"].search([("type", "in", ["bank", "cash", "sale", "purchase"])])]
    d["taxes"] = [{"name": t.name, "amount": t.amount, "type": t.type_tax_use,
                   "country": t.country_id.code} for t in env["account.tax"].search([])]
    d["purchase_orders"] = [{"name": po.name, "vendor": po.partner_id.name,
                             "state": po.state, "total": po.amount_total,
                             "currency": po.currency_id.name} for po in env["purchase.order"].search([], order="id")]
    d["sale_orders"] = [{"name": so.name, "customer": so.partner_id.name,
                         "state": so.state, "total": so.amount_total,
                         "currency": so.currency_id.name} for so in env["sale.order"].search([], order="id")]
    d["customer_invoices"] = [{"name": m.name, "customer": m.partner_id.name,
                               "state": m.state, "total": m.amount_total,
                               "tax": m.amount_tax, "currency": m.currency_id.name,
                               "due": str(m.invoice_date_due), "payment_state": m.payment_state}
                              for m in env["account.move"].search([("move_type", "=", "out_invoice")], order="id")]
    d["vendor_bills"] = [{"name": m.name, "vendor": m.partner_id.name, "state": m.state,
                          "total": m.amount_total, "currency": m.currency_id.name,
                          "payment_state": m.payment_state}
                         for m in env["account.move"].search([("move_type", "=", "in_invoice")], order="id")]
    d["payments"] = [{"name": p.name, "partner": p.partner_id.name, "amount": p.amount,
                      "journal": p.journal_id.name, "type": p.payment_type, "state": p.state}
                     for p in env["account.payment"].search([], order="id")]
    d["orderpoints"] = [{"product": o.product_id.default_code, "min": o.product_min_qty,
                         "max": o.product_max_qty} for o in env["stock.warehouse.orderpoint"].search([])]
    d["bank_statements"] = [{"name": s.name, "journal": s.journal_id.name,
                             "lines": len(s.line_ids)} for s in env["account.bank.statement"].search([])]
    d["lots"] = [{"name": l.name, "product": l.product_id.default_code,
                  "expiry": str(l.expiration_date) if getattr(l, "expiration_date", False) else None}
                 for l in env["stock.lot"].search([], order="id", limit=30)]
    return d


MODELS = [
    "res.partner", "product.template", "product.category", "stock.lot",
    "stock.location", "stock.warehouse", "stock.picking",
    "stock.warehouse.orderpoint", "purchase.order", "sale.order",
    "account.move", "account.payment", "account.payment.register",
    "account.journal", "res.currency", "res.users", "account.bank.statement",
]

result = {"forms": {}, "menu_tree": [], "roles": {}, "demo": {}}
for m in MODELS:
    result["forms"][m] = form_inventory(m)
try:
    result["menu_tree"] = menu_tree()
except Exception as e:
    result["menu_tree"] = [{"error": str(e)[:200]}]
try:
    result["roles"] = roles()
except Exception as e:
    result["roles"] = {"error": str(e)[:200]}
try:
    result["demo"] = demo()
except Exception as e:
    result["demo"] = {"error": str(e)[:200]}

print("===GT_JSON_START===")
print(json.dumps(result, ensure_ascii=False))
print("===GT_JSON_END===")
