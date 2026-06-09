# -*- coding: utf-8 -*-
"""
Build the Sudan Medical-Supply ERP User Manual from a single content source
into a professionally formatted Word document (.docx) and an HTML file that is
converted to PDF with the Odoo container's wkhtmltopdf.

Usage:
    python3 scripts/build_manual.py
"""
import html as _html
import os

BRAND = "0E6E8E"        # teal
BRAND_DARK = "094E66"
ACCENT = "1F7A4D"       # medical green
LIGHT = "EAF3F6"        # light teal band
GREY = "F4F6F7"

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "manual")
TITLE = "Medical-Supply ERP"
SUBTITLE = "User Manual"
ORG = "Sudan MedSupply Co."
PLATFORM = "Built on ePHEM / Odoo 18 Community"
VERSION = "Version 1.0"
DATE = "June 2026"

# ----------------------------------------------------------------------------
# CONTENT SOURCE  — list of blocks. Block types:
#   ("h1"|"h2"|"h3", text)
#   ("p", text)
#   ("ul"|"ol", [items])
#   ("table", [headers], [[row], ...])
#   ("tip"|"warn"|"note", title, text)
# Inline **bold** is supported in p / list / callout / table text.
# ----------------------------------------------------------------------------
C = []
def h1(t): C.append(("h1", t))
def h2(t): C.append(("h2", t))
def h3(t): C.append(("h3", t))
def p(t): C.append(("p", t))
def ul(items): C.append(("ul", items))
def ol(items): C.append(("ol", items))
def table(headers, rows): C.append(("table", headers, rows))
def tip(title, t): C.append(("tip", title, t))
def warn(title, t): C.append(("warn", title, t))
def note(title, t): C.append(("note", title, t))

# ============================================================ 1. INTRODUCTION
h1("1. Introduction")
p("This manual describes the **Medical-Supply ERP** — an integrated business system for a "
  "company that imports, stores, and distributes medical supplies and pharmaceuticals. "
  "The system covers the full operational chain: master-data configuration, inventory and "
  "warehousing, procurement, sales, and accounting, with native **multi-currency** support "
  "(Sudanese Pound as the base currency and US Dollar as a reference currency).")
p("The system is built on **Odoo 18 Community** (the ePHEM deployment) and uses only "
  "Community and open-source (OCA / Odoo-Mates) modules — no proprietary Enterprise "
  "licences are required.")
h2("1.1 Who this manual is for")
ul(["**Administrators** who configure master data — warehouses, items, partners, banks, "
    "currencies and exchange rates.",
    "**Procurement officers** who raise purchase orders and receive goods.",
    "**Sales staff** who quote, sell, and deliver to customers.",
    "**Accountants** who manage invoices, payments, bank reconciliation and reports."])
h2("1.2 Key capabilities at a glance")
table(["Area", "What you can do"],
      [["Configuration", "Define company, currencies & rates, customers, suppliers, banks, cash safes, units, warehouses and product categories."],
       ["Inventory", "Register items with lot/batch and expiry tracking; manage on-hand stock and valuation."],
       ["Warehouse", "Run multiple warehouses and internal locations (e.g. cold storage, quarantine); receipts, deliveries and internal transfers."],
       ["Procurement", "RFQ → Purchase Order → Receipt → Vendor Bill, with vendor price lists and multi-currency purchasing."],
       ["Sales", "Quotation → Sales Order → Delivery → Customer Invoice, with price lists per currency."],
       ["Accounting", "Customer invoices, vendor bills, payments, bank reconciliation, financial reports, fiscal year and dunning."],
       ["Multi-currency", "SDG base + USD reference; dated exchange-rate history that is easy to update."]])

# ============================================================ 2. SYSTEM OVERVIEW
h1("2. System Overview")
h2("2.1 Building blocks")
p("The ERP is organised into cooperating Odoo applications. Each application adds menus, "
  "documents and reports, but they share the same products, partners and accounting.")
table(["Application", "Purpose"],
      [["Inventory", "Items, stock, warehouses, locations, lots, expiry, transfers."],
       ["Purchase", "Supplier orders and goods receipts."],
       ["Sales", "Customer quotations, orders and deliveries."],
       ["Invoicing / Accounting", "Invoices, bills, payments, journals, reports."],
       ["Contacts", "Customers and suppliers (a single contact can be both)."],
       ["Settings", "Company, currencies, users, and feature switches."]])
h2("2.2 Logging in")
ol(["Open the system URL in a web browser (for the local demo: **http://localhost:8069**).",
    "If a database list appears, choose **erpmedsupply**.",
    "Enter your user name and password. The default administrator is **admin / admin** "
    "on the demo database — change this password before going live."])
warn("Change default credentials", "The demo administrator password (**admin**) and the "
     "database master password must be changed before the system is used with real data.")
h2("2.3 Finding your way around")
ul(["The **top menu bar** switches between applications (Inventory, Purchase, Sales, Accounting…).",
    "Each application has its own **Configuration** sub-menu for setup tasks.",
    "Lists can be filtered, grouped and exported; most documents follow a "
    "**draft → confirmed → done** lifecycle shown by status buttons in the top-right."])

# ============================================================ 3. CONFIGURATION
h1("3. Configuration (Central Admin)")
p("Configuration is the heart of the system. Complete these steps **in order** before "
  "recording day-to-day transactions, because some settings (especially the base currency "
  "and chart of accounts) are difficult to change once transactions exist.")

h2("3.1 Company")
ol(["Go to **Settings → Users & Companies → Companies** and open your company.",
    "Set the legal name, address, tax number and logo.",
    "Set the **Country** to Sudan."])

h2("3.2 Currencies and exchange rates")
p("The system uses **SDG (Sudanese Pound)** as the company base currency and **USD** as a "
  "reference currency for imports and price quotations.")
ol(["Enable multi-currency: **Settings → Accounting → Currencies → tick Multi-Currencies**.",
    "Activate the currencies you use: **Settings → Currencies**, switch on **SDG** and **USD**.",
    "Confirm the company base currency is **SDG** (set on the company / chart of accounts)."])
h3("Recording a new USD exchange rate")
p("Exchange rates are stored as **dated records**, so the full history is preserved and any "
  "past document is valued at the rate that applied on its date.")
ol(["Open **Accounting → Configuration → Currencies** and click **USD**.",
    "Go to the **Rates** tab and click **Add a line**.",
    "Enter the **date** and the rate. The system lets you type the intuitive figure — "
    "**how many SDG equal 1 USD** (e.g. 700).",
    "Save. The new rate applies to all documents dated on or after that day."])
tip("Easy rate updates", "Because each change is a new dated line, you simply add a line "
    "whenever the rate moves — you never overwrite history. Reports and documents "
    "automatically use the correct rate for their date.")
note("Automatic rates (optional)", "Community Odoo does not fetch rates automatically. If you "
     "want scheduled updates from a provider, the OCA **currency_rate_update** module can be "
     "added later; otherwise rates are maintained by hand as above.")

h2("3.3 Customers and suppliers")
p("Customers and suppliers are both **Contacts**. A single contact can be both a customer and "
  "a supplier — do not create duplicates.")
ol(["Open **Contacts → New**.",
    "Choose **Company** or **Individual** and enter name, address and phone.",
    "On the **Sales & Purchasing** tab set the price list, payment terms and (for foreign "
    "suppliers) the purchase currency.",
    "On the **Accounting** tab set receivable/payable accounts and add bank accounts if needed."])
table(["Field", "Used for"],
      [["Customer / Vendor", "Determines whether the contact appears in Sales or Purchase."],
       ["Purchase currency", "Default currency for that supplier's orders (e.g. USD for imports)."],
       ["Price list", "Which selling prices and currency apply to this customer."],
       ["Bank accounts", "Needed to register or batch payments."]])

h2("3.4 Banks and money safes")
p("Money flows are tracked through **journals**. A **bank** needs both a bank record and a "
  "bank journal; a **money safe / cash box** is a **cash journal**.")
ol(["Create the institution: **Accounting → Configuration → Banks → New** (name, SWIFT/BIC).",
    "Create a **Bank** journal: **Accounting → Configuration → Journals → New**, Type = **Bank**. "
    "Set a currency for a foreign-currency account (e.g. a USD bank account).",
    "Create a **Cash** journal for each physical safe: Type = **Cash** (e.g. *Main Cash Safe (SDG)*, "
    "*USD Cash Safe*)."])
note("Why a cash journal is a 'safe'", "There is no separate 'safe' object. Each physical cash "
     "box or till is represented by its own **Cash journal**, so its balance and movements are "
     "tracked and reconciled independently.")

h2("3.5 Units of measure")
p("Enable **Units of Measure** (Settings) to buy, stock and sell in different units — for "
  "example purchase a *Box of 100* but issue *units*. Define units and their conversion "
  "factors under **Inventory → Configuration → Units of Measure**.")

h2("3.6 Warehouses and locations")
ol(["Go to **Inventory → Configuration → Warehouses** and create one per physical site "
    "(name + short code, e.g. *Khartoum Central / KRT*).",
    "Set the number of receipt and delivery steps on each warehouse as needed.",
    "Create internal **Locations** under a warehouse for special storage: "
    "**Cold Storage (2-8°C)**, **Quarantine**, **Expired / Damaged**."])
tip("Cold chain", "Temperature-controlled storage is modelled as an internal **location**. "
    "A **putaway rule** can automatically route a product (e.g. insulin) into Cold Storage "
    "when it is received.")

h2("3.7 Product categories")
p("Product categories control how stock is costed and removed.")
table(["Setting", "Recommended value", "Effect"],
      [["Costing Method", "FIFO", "Stock is valued first-in-first-out."],
       ["Inventory Valuation", "Manual / Periodic*", "Avoids needing valuation accounts up front."],
       ["Force Removal Strategy", "FEFO", "Goods nearest to expiry are issued first."]])
note("Automated valuation", "*The demo uses periodic valuation so goods movements post without "
     "extra account setup. To post stock value to the ledger in real time, set the category's "
     "Stock Input/Output/Valuation accounts and a Stock journal, then switch Valuation to "
     "**Automated**.")

# ============================================================ 4. INVENTORY
h1("4. Inventory & Items")
h2("4.1 Registering an item")
ol(["Open **Inventory → Products → Products → New**.",
    "Enter the name and **Internal Reference** (SKU) and **Barcode**.",
    "Set **Product Type = Goods** and switch on **Track Inventory** so stock is counted.",
    "Assign the **Product Category** (e.g. Pharmaceuticals).",
    "Set the **Cost** and **Sales Price**.",
    "On the **Inventory** tab set **Tracking = By Lots** and enable **Expiration Date** for "
    "medicines and consumables."])
h2("4.2 Lot / batch and expiry tracking")
p("Lot tracking records which **batch** each unit belongs to; expiry tracking records the "
  "**expiration date** of each batch. Together they give full traceability and drive FEFO.")
ul(["On receipt the system asks for the **lot number** and **expiry date**.",
    "Stock can be traced by lot for recalls and audits.",
    "Near-expiry stock is highlighted and issued first under FEFO."])
h2("4.3 Checking stock on hand")
p("Open a product and use the **On Hand** / **Forecasted** smart buttons, or go to "
  "**Inventory → Products → Products** and review the on-hand column. "
  "**Inventory → Reporting** provides valuation and movement analysis.")

# ============================================================ 5. WAREHOUSE
h1("5. Warehouse Operations")
h2("5.1 Receipts (goods in)")
ol(["Receipts are generated from confirmed purchase orders (see Procurement).",
    "Open the receipt, enter the **lot number** and **expiry date** for each line, then "
    "**Validate**.",
    "Stock is added to the destination location; putaway rules may route it (e.g. to Cold Storage)."])
h2("5.2 Deliveries (goods out)")
ol(["Deliveries are generated from confirmed sales orders.",
    "The system reserves stock — under **FEFO** it selects the soonest-to-expire lots.",
    "**Validate** the delivery to ship the goods and reduce stock."])
h2("5.3 Internal transfers")
p("Move stock between locations or warehouses — for example from the main store to **Cold "
  "Storage**. Use **Inventory → Operations → Transfers**, choose the source and destination "
  "locations, add the product and lot, and validate.")
h2("5.4 Reordering rules")
p("Set minimum/maximum levels on critical items (**Reordering Rules**). When stock falls "
  "below the minimum the system proposes a purchase (for *Buy* products) to top up to the "
  "maximum, preventing stock-outs of essential supplies.")

# ============================================================ 6. PROCUREMENT
h1("6. Procurement")
h2("6.1 The purchasing flow")
ol(["**Purchase → Orders → New** creates a Request for Quotation (RFQ).",
    "Select the supplier; add products and quantities. Prices come from the vendor price list.",
    "**Confirm Order** turns the RFQ into a Purchase Order and creates a **Receipt**.",
    "Receive the goods (entering lots and expiry).",
    "**Create Bill** generates the vendor bill; post it and register payment."])
h2("6.2 Vendor price lists")
p("On a product's **Purchase** tab, add one line per supplier with the price, currency, "
  "minimum quantity and lead time. Import suppliers can be priced in **USD**.")
h2("6.3 Multi-currency purchasing")
p("A purchase order can be issued in the supplier's currency (e.g. USD). The amount is "
  "converted to SDG using the exchange rate on the order/bill date, so the accounting "
  "value is always correct in the base currency.")
tip("Bill control", "Set **Bill Control = Received quantities** so you only pay for what "
    "actually arrived — important for medical goods.")

# ============================================================ 7. SALES
h1("7. Sales")
h2("7.1 The selling flow")
ol(["**Sales → Orders → New** creates a quotation.",
    "Select the customer; the customer's price list sets prices and currency.",
    "Add products and quantities and send or confirm the quotation.",
    "**Confirm** creates the Sales Order and a **Delivery**.",
    "Validate the delivery (FEFO selects the lots), then **Create Invoice** and post it."])
h2("7.2 Price lists and currency")
p("Each price list has a currency. Domestic sales use an **SDG** price list. The sales "
  "order's currency follows its price list, so assign the correct price list to each customer.")
warn("Currency comes from the price list", "If invoices appear in the wrong currency, check "
     "the price list assigned to the customer — the order currency follows the price list, "
     "not the contact's country.")

# ============================================================ 8. ACCOUNTING
h1("8. Accounting")
h2("8.1 What is included")
p("Community Odoo provides **Invoicing**; the bundled OCA / Odoo-Mates modules extend it into "
  "a full **Accounting** system.")
table(["Capability", "Provided by"],
      [["Customer invoices, vendor bills, payments, taxes", "Invoicing (core)"],
       ["Full Accounting menu, asset, budget, fiscal year, recurring", "om_account_accountant suite"],
       ["Financial reports (Balance Sheet, P&L, ledgers, tax, aged)", "accounting_pdf_reports"],
       ["Cash Book / Day Book / Bank Book", "om_account_daily_reports"],
       ["Bank reconciliation (interactive matching)", "account_reconcile_oca"],
       ["Customer follow-up / dunning", "om_account_followup"]])
h2("8.2 Customer invoices and vendor bills")
ul(["Customer invoices are normally created from sales orders and posted from the Accounting app.",
    "Vendor bills are created from purchase orders / receipts and posted before payment.",
    "Each posted document generates the matching journal entries automatically."])
h2("8.3 Payments and the money safe")
p("Register a payment from an invoice or bill and choose the journal — a **bank** account or "
  "a **cash safe**. Reconcile cash safes daily using the **Cash Book / Day Book** reports.")
h2("8.4 Bank reconciliation")
p("Use **Accounting → Bank** to match bank-statement lines against invoices and payments with "
  "the interactive reconciliation screen (account_reconcile_oca).")
h2("8.5 Reports")
ul(["**Balance Sheet** and **Profit & Loss** for financial position and performance.",
    "**General / Partner Ledger**, **Trial Balance**, **Aged Receivable / Payable**.",
    "**Tax Report** for filing; **Day/Cash/Bank Book** for daily cash control."])
h2("8.6 Fiscal year and follow-up")
ul(["Define the **Fiscal Year** and set **lock dates** after each period close.",
    "Configure **Follow-up levels** (e.g. 15 / 30 / 60 days) to chase overdue customers."])

# ============================================================ 9. MULTI-CURRENCY
h1("9. Multi-Currency Operations")
p("The system keeps accounts in **SDG** while letting you transact in **USD**.")
ul(["**Base currency:** SDG — all ledgers and reports are in SDG.",
    "**Reference currency:** USD — used for import purchases and quotations.",
    "**Rates:** stored as dated lines; the rate on a document's date is used for conversion.",
    "**Foreign journals:** a USD bank or cash journal holds balances in USD and is revalued "
    "to SDG at period close."])
table(["Document", "Currency source"],
      [["Purchase order", "Supplier's purchase currency / vendor price list"],
       ["Vendor bill", "Inherited from the purchase order"],
       ["Sales order", "Customer's price list"],
       ["Customer invoice", "Inherited from the sales order"]])

# ============================================================ 10. MEDICAL SPECIFICS
h1("10. Medical-Supply Specifics")
ul(["**Batch traceability** — every medicine is tracked by lot for recalls and audits.",
    "**Expiry control** — expiration dates are captured per lot and stock nearing expiry is flagged.",
    "**FEFO** — deliveries automatically issue the earliest-expiring stock first.",
    "**Cold chain** — temperature-sensitive items (e.g. insulin) are stored in a Cold Storage "
    "location, with putaway rules routing them there on receipt.",
    "**Quarantine / damaged** — separate locations isolate non-sellable stock.",
    "**Imports** — purchases in USD are valued in SDG at the current rate; landed costs "
    "(freight, customs) can be folded into unit cost."])

# ============================================================ 11. DEMO DATA
h1("11. Demo Data Reference")
p("The demonstration database **erpmedsupply** is pre-loaded with realistic data so every "
  "feature can be explored immediately.")
table(["Item", "Details"],
      [["Company", "Sudan MedSupply Co. (base currency SDG)"],
       ["Currencies", "SDG (base) + USD (reference), with 5 dated USD rates (600 → 700 SDG)"],
       ["Warehouses", "Khartoum Central (KRT), Port Sudan (PRT)"],
       ["Locations", "Cold Storage (2-8°C), Quarantine, Expired/Damaged"],
       ["Products", "10 medical items with lot & expiry tracking"],
       ["Customers", "Khartoum Teaching Hospital, Omdurman Family Clinic, Sudanese Red Crescent, Bahri Community Pharmacy"],
       ["Suppliers", "Nile Medical Supplies, Khartoum Pharma Imports, Gulf MedTrade (USD)"],
       ["Banks & safes", "2 bank journals (SDG/USD) + 2 cash safes (SDG/USD)"],
       ["Purchases", "3 purchase orders received (incl. one in USD); 1 vendor bill"],
       ["Sales", "2 delivered & invoiced orders (SDG) + 1 draft quotation"]])

# ============================================================ 12. ADMIN
h1("12. Administration & Maintenance")
h2("12.1 Users and access")
p("Create users under **Settings → Users**. Assign application access rights so each role "
  "sees only the menus it needs (e.g. sales staff vs accountants).")
h2("12.2 Backups")
p("Back up the database regularly. The deployment includes backup scripts; on the demo you can "
  "also back up from **Database Manager**. Keep off-site copies before upgrades.")
h2("12.3 Rebuilding the demo")
p("The demo database can be recreated from scratch using the project's seed script "
  "(**scripts/seed_medsupply.py**). See the project README and the *erp-medsupply-demo* "
  "runbook for the exact commands.")
warn("Production hardening", "Before real use: change all default passwords, disable the "
     "database manager (list_db = False), enable HTTPS, and restrict the database filter.")

# ============================================================ 13. GLOSSARY
h1("13. Glossary")
table(["Term", "Meaning"],
      [["SKU / Internal Reference", "Your unique product code."],
       ["Lot / Batch", "A group of units received together, tracked as one."],
       ["FEFO", "First Expiry First Out — issue soonest-to-expire stock first."],
       ["FIFO", "First In First Out — valuation method using oldest cost first."],
       ["Putaway rule", "Automatic routing of received goods to a specific location."],
       ["Journal", "A book of account entries (Sales, Purchase, Bank, Cash, Misc)."],
       ["RFQ", "Request for Quotation — a draft purchase order."],
       ["Reconciliation", "Matching bank-statement lines to invoices and payments."],
       ["Base currency", "The currency the accounts are kept in (SDG)."]])

# ----------------------------------------------------------------------------
# Inline bold parser
# ----------------------------------------------------------------------------
def runs(text):
    parts = []
    bold = False
    for seg in text.split("**"):
        if seg:
            parts.append((seg, bold))
        bold = not bold
    return parts or [(text, False)]

# ============================================================ DOCX RENDERER
def build_docx(path):
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    doc = Document()
    # base style
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)

    def set_heading_color(style_name, size, color):
        st = doc.styles[style_name]
        st.font.name = "Calibri"
        st.font.size = Pt(size)
        st.font.color.rgb = RGBColor.from_string(color)
        st.font.bold = True

    set_heading_color("Heading 1", 18, BRAND_DARK)
    set_heading_color("Heading 2", 14, BRAND)
    set_heading_color("Heading 3", 12, ACCENT)

    def shade(cell, color):
        tcpr = cell._tc.get_or_add_tcPr()
        sh = OxmlElement("w:shd")
        sh.set(qn("w:val"), "clear")
        sh.set(qn("w:fill"), color)
        tcpr.append(sh)

    def add_runs(paragraph, text, color=None, bold_all=False):
        for seg, b in runs(text):
            r = paragraph.add_run(seg)
            r.bold = b or bold_all
            if color:
                r.font.color.rgb = RGBColor.from_string(color)

    # ---- Cover ----
    band = doc.add_table(rows=1, cols=1)
    band.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = band.rows[0].cells[0]
    shade(cell, BRAND)
    cell.paragraphs[0].text = ""
    for _ in range(2):
        cell.add_paragraph("")
    pt = cell.add_paragraph()
    pt.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = pt.add_run(TITLE)
    r.bold = True; r.font.size = Pt(34); r.font.color.rgb = RGBColor.from_string("FFFFFF")
    ps = cell.add_paragraph()
    ps.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = ps.add_run(SUBTITLE)
    r.font.size = Pt(20); r.font.color.rgb = RGBColor.from_string("FFFFFF")
    for _ in range(2):
        cell.add_paragraph("")

    for txt, sz in [(ORG, 16), (PLATFORM, 12), ("", 6), (VERSION, 12), (DATE, 12)]:
        pp = doc.add_paragraph()
        pp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if txt:
            rr = pp.add_run(txt)
            rr.font.size = Pt(sz)
            if txt == ORG:
                rr.bold = True; rr.font.color.rgb = RGBColor.from_string(BRAND_DARK)
    doc.add_page_break()

    # ---- TOC ----
    htoc = doc.add_paragraph()
    rr = htoc.add_run("Table of Contents")
    rr.bold = True; rr.font.size = Pt(16); rr.font.color.rgb = RGBColor.from_string(BRAND_DARK)
    par = doc.add_paragraph()
    run = par.add_run()
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), r'TOC \o "1-3" \h \z \u')
    placeholder = OxmlElement("w:r")
    t = OxmlElement("w:t")
    t.text = "Right-click and choose 'Update Field' to build the table of contents."
    placeholder.append(t)
    fld.append(placeholder)
    par._p.append(fld)
    doc.add_page_break()

    # ---- Footer page numbers ----
    footer = doc.sections[0].footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = fp.add_run()
    for el, attrs in [("w:fldChar", {"w:fldCharType": "begin"}),
                      ("w:instrText", None), ("w:fldChar", {"w:fldCharType": "end"})]:
        e = OxmlElement(el)
        if el == "w:instrText":
            e.set(qn("xml:space"), "preserve"); e.text = "PAGE"
        else:
            for k, v in attrs.items():
                e.set(qn(k), v)
        run._r.append(e)

    # ---- Content ----
    def callout(title, text, fill, bar):
        tbl = doc.add_table(rows=1, cols=1)
        c = tbl.rows[0].cells[0]
        shade(c, fill)
        tp = c.paragraphs[0]
        add_runs(tp, title, color=bar, bold_all=True)
        bp = c.add_paragraph()
        add_runs(bp, text)
        doc.add_paragraph("")

    for block in C:
        kind = block[0]
        if kind == "h1":
            doc.add_page_break()
            doc.add_heading(block[1], level=1)
        elif kind == "h2":
            doc.add_heading(block[1], level=2)
        elif kind == "h3":
            doc.add_heading(block[1], level=3)
        elif kind == "p":
            par = doc.add_paragraph()
            add_runs(par, block[1])
        elif kind == "ul":
            for it in block[1]:
                par = doc.add_paragraph(style="List Bullet")
                add_runs(par, it)
        elif kind == "ol":
            for it in block[1]:
                par = doc.add_paragraph(style="List Number")
                add_runs(par, it)
        elif kind == "table":
            headers, rows = block[1], block[2]
            tbl = doc.add_table(rows=1, cols=len(headers))
            tbl.style = "Table Grid"
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            for i, htext in enumerate(headers):
                c = tbl.rows[0].cells[i]
                shade(c, BRAND)
                pr = c.paragraphs[0]
                add_runs(pr, htext, color="FFFFFF", bold_all=True)
            for ri, row in enumerate(rows):
                cells = tbl.add_row().cells
                for ci, val in enumerate(row):
                    if ri % 2 == 1:
                        shade(cells[ci], GREY)
                    add_runs(cells[ci].paragraphs[0], val)
            doc.add_paragraph("")
        elif kind == "tip":
            callout("TIP — " + block[1], block[2], LIGHT, ACCENT)
        elif kind == "warn":
            callout("IMPORTANT — " + block[1], block[2], "FBEAEA", "B00020")
        elif kind == "note":
            callout("NOTE — " + block[1], block[2], GREY, BRAND_DARK)

    doc.save(path)

# ============================================================ HTML RENDERER
def esc(t):
    out = []
    for seg, b in runs(t):
        s = _html.escape(seg)
        out.append("<strong>%s</strong>" % s if b else s)
    return "".join(out)

def slug(text):
    s = "".join(c.lower() if c.isalnum() else "-" for c in text)
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-")

def build_html(out_path):
    css = """
    @page { margin: 18mm 16mm 16mm 16mm; }
    body { font-family:'Helvetica Neue',Arial,sans-serif; color:#1a1a1a; font-size:11pt; line-height:1.5; margin:0; }
    h1 { color:#%(bd)s; font-size:21pt; border-bottom:3px solid #%(br)s; padding-bottom:6px;
         margin-top:0; page-break-before:always; }
    h2 { color:#%(br)s; font-size:15pt; margin-top:20px; }
    h3 { color:#%(ac)s; font-size:12.5pt; margin-top:14px; }
    p, li { font-size:11pt; }
    table { border-collapse:collapse; width:100%%; margin:12px 0; page-break-inside:avoid; }
    th { background:#%(br)s; color:#fff; text-align:left; padding:7px 9px; font-size:10.5pt; }
    td { border:1px solid #d6dde0; padding:6px 9px; vertical-align:top; font-size:10.5pt; }
    tr:nth-child(even) td { background:#%(gr)s; }
    .callout { border-radius:6px; padding:10px 14px; margin:12px 0; border-left:5px solid; page-break-inside:avoid; }
    .tip  { background:#%(lt)s; border-color:#%(ac)s; }
    .warn { background:#FBEAEA; border-color:#B00020; }
    .note { background:#%(gr)s; border-color:#%(bd)s; }
    .callout .t { font-weight:bold; display:block; margin-bottom:3px; }
    .tip .t { color:#%(ac)s; } .warn .t { color:#B00020; } .note .t { color:#%(bd)s; }
    /* cover */
    .cover { page-break-after:always; }
    .cover .band { background:#%(br)s; color:#fff; padding:150px 50px 80px; text-align:center; }
    .cover .band .t1 { font-size:42pt; font-weight:bold; }
    .cover .band .t2 { font-size:24pt; margin-top:10px; }
    .cover .meta { text-align:center; margin-top:80px; }
    .cover .meta .org { font-size:22pt; font-weight:bold; color:#%(bd)s; }
    .cover .meta .sub { font-size:13pt; margin-top:6px; color:#333; }
    .cover .meta .ver { font-size:13pt; margin-top:46px; color:#333; }
    /* toc */
    .toc { page-break-after:always; }
    .toc h2 { color:#%(bd)s; border-bottom:2px solid #%(br)s; padding-bottom:4px; }
    .toc ul { list-style:none; padding-left:0; }
    .toc li.l1 { font-weight:bold; color:#%(bd)s; margin-top:8px; font-size:11.5pt; }
    .toc li.l2 { padding-left:20px; font-weight:normal; color:#333; font-size:10.5pt; }
    .toc a { text-decoration:none; color:inherit; }
    """ % {"bd": BRAND_DARK, "br": BRAND, "ac": ACCENT, "gr": GREY, "lt": LIGHT}

    # table of contents from h1/h2
    toc_items = []
    for block in C:
        if block[0] in ("h1", "h2"):
            sid = slug(block[1])
            cls = "l1" if block[0] == "h1" else "l2"
            toc_items.append('<li class="%s"><a href="#%s">%s</a></li>' % (cls, sid, _html.escape(block[1])))

    parts = ['<!doctype html><html><head><meta charset="utf-8"><style>%s</style></head><body>' % css]
    # cover
    parts.append(
        '<div class="cover"><div class="band"><div class="t1">%s</div><div class="t2">%s</div></div>'
        '<div class="meta"><div class="org">%s</div><div class="sub">%s</div>'
        '<div class="ver">%s &middot; %s</div></div></div>'
        % (_html.escape(TITLE), _html.escape(SUBTITLE), _html.escape(ORG),
           _html.escape(PLATFORM), _html.escape(VERSION), _html.escape(DATE)))
    # toc
    parts.append('<div class="toc"><h2>Table of Contents</h2><ul>%s</ul></div>' % "".join(toc_items))
    # body
    for block in C:
        kind = block[0]
        if kind in ("h1", "h2", "h3"):
            parts.append('<%s id="%s">%s</%s>' % (kind, slug(block[1]), esc(block[1]), kind))
        elif kind == "p":
            parts.append("<p>%s</p>" % esc(block[1]))
        elif kind == "ul":
            parts.append("<ul>%s</ul>" % "".join("<li>%s</li>" % esc(i) for i in block[1]))
        elif kind == "ol":
            parts.append("<ol>%s</ol>" % "".join("<li>%s</li>" % esc(i) for i in block[1]))
        elif kind == "table":
            headers, rows = block[1], block[2]
            th = "".join("<th>%s</th>" % esc(h) for h in headers)
            trs = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % esc(c) for c in r) for r in rows)
            parts.append("<table><tr>%s</tr>%s</table>" % (th, trs))
        elif kind in ("tip", "warn", "note"):
            label = {"tip": "TIP", "warn": "IMPORTANT", "note": "NOTE"}[kind]
            parts.append('<div class="callout %s"><span class="t">%s — %s</span>%s</div>'
                         % (kind, label, esc(block[1]), esc(block[2])))
    parts.append("</body></html>")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("".join(parts))

if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    docx_path = os.path.join(OUT_DIR, "Sudan_MedSupply_ERP_User_Manual.docx")
    html_path = os.path.join(OUT_DIR, "_manual.html")
    build_docx(docx_path)
    build_html(html_path)
    print("DOCX :", docx_path)
    print("HTML :", html_path)
    print("BLOCKS:", len(C))
