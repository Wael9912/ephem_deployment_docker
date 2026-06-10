export const meta = {
  name: 'medsupply-manual-content',
  description: 'Draft + adversarially verify the bilingual (EN/AR) Medical-Supply ERP user manual, grounded in extracted ground-truth field/menu/role/demo data',
  phases: [
    { title: 'Draft', detail: 'one agent per chapter, grounded in ground-truth files, writes CONTENT/<key>.json' },
    { title: 'Verify', detail: 'adversarial fact-check vs ground truth + edit for clarity, overwrites the file' },
  ],
}

const GT = '/Users/waelabdalla/Documents/ephem-deploy/docs/manual/_ground_truth'
const CONTENT = '/Users/waelabdalla/Documents/ephem-deploy/docs/manual/_content'

const STYLE = `
You are writing the official **bilingual user manual** (English + Modern Standard Arabic) for the
**Medical-Supply ERP** of *Sudan MedSupply Co.* (Arabic: *شركة السودان للمستلزمات الطبية*) — a Khartoum,
Sudan company that imports, stores and distributes medical supplies and pharmaceuticals. The system is
**Odoo 18 Community** with OCA/Odoo-Mates accounting add-ons and the **Spiffy backend theme** (dark navbar,
a 9-dot app launcher, a vertical quick-action rail on the side, "Good Evening" greeting).

AUDIENCE: ordinary staff with **no accounting or management background**. Write so a newcomer understands.

VOICE & QUALITY RULES (follow strictly):
- Simple, warm, explanatory. The first time a business/accounting term appears (journal, reconciliation,
  receivable, FEFO, lot, putaway, pricelist, tax, fiscal), explain it in one plain-language sentence.
- Detailed, organized, and confidence-building. We are also SELLING the system: highlight what it does
  *for the user automatically* and call out every useful function/button so the breadth is obvious.
- Be concrete: use the **real demo records and numbers** from demo.json. NEVER invent numbers, names,
  field labels, menu paths, or buttons. If you are unsure, omit it.
- Menu navigation must be written as **App → Menu → Sub-menu** and must match menu_tree.json.
- When you describe a page, list **every field the user sees, across all tabs**, in a markdown-style
  table with two columns: the field label (exactly as in the form_*.json "label") and a plain explanation
  of what it means / what to enter. Group by tab using h3 sub-headings where a form has tabs (the tab
  order is the order pages appear in the form_*.json).
- Enumerate the page's **functions/buttons** (use the form_*.json "buttons", "smart_buttons" and
  "statusbar_states") and say what each does — this showcases capability.
- Provide clear **step-by-step** numbered instructions (ol) for each task.
- Insert screenshots with a fig block, referencing the EXACT file name from figures.json, with an accurate
  caption describing what is shown. Only reference files that exist in figures.json.
- Inline emphasis: **bold** for labels/buttons/menus, *italic* for record names. Tables for field lists
  and reference data. tip/warn/note callouts where helpful.
- Arabic (blocks_ar): natural, fluent MSA that MIRRORS the English structure 1:1 (same headings, tables,
  steps, figures, callouts). Keep technical/codes as-is (SDG, USD, SKU, FEFO, FIFO, RFQ, BIC) optionally
  with a short Arabic gloss. Translate Odoo UI labels to the Arabic the system shows where you know it.
- NEVER mention "ePHEM" anywhere. The product is the "Medical-Supply ERP".

OUTPUT FORMAT — write ONE JSON object to the file CONTENT/<key>.json (UTF-8), with keys:
  { "key": "<key>", "title_en": "...", "title_ar": "...", "blocks_en": [ <block>... ], "blocks_ar": [ <block>... ] }
A <block> is one of:
  {"t":"h2","text":"..."}            section heading
  {"t":"h3","text":"..."}            sub-heading (e.g. a tab name)
  {"t":"p","text":"..."}             paragraph (supports **bold** / *italic*)
  {"t":"ul","items":["...", ...]}    bullet list
  {"t":"ol","items":["...", ...]}    numbered steps
  {"t":"table","headers":["..."],"rows":[["...","..."], ...]}
  {"t":"tip","title":"...","text":"..."}     |  {"t":"warn",...}  |  {"t":"note",...}
  {"t":"fig","file":"po_usd.png","caption":"..."}
Do NOT use "h1" (the chapter title is rendered from title_en/title_ar). Make blocks_en and blocks_ar
parallel. Validate the JSON parses before writing (no trailing commas, properly escaped strings).
`

// key, titles, scope, ground-truth files to read, suggested figures
const CHAPTERS = [
  {
    key: 'intro', title_en: '1. Introduction', title_ar: '1. مقدمة',
    gt: ['demo.json', 'figures.json'],
    scope: `Introduce the Medical-Supply ERP: what it is, the full operational chain it covers (configuration,
    inventory & warehousing, procurement, sales, accounting, multi-currency SDG base + USD reference). State it
    is built on Odoo 18 Community + open-source add-ons (no paid Enterprise licences). Add "Who this manual is for"
    (admins, procurement officers, sales staff, warehouse keepers, accountants, managers) and a "Key capabilities
    at a glance" table (Area | What you can do) covering Configuration, Inventory, Warehouse, Procurement, Sales,
    Accounting, Multi-currency, Medical specifics. Add a short "How to use this manual" note.`,
    figs: [],
  },
  {
    key: 'interface', title_en: '2. Getting Started & the Interface', title_ar: '2. البدء وواجهة النظام',
    gt: ['figures.json', 'menu_tree.json'],
    scope: `Teach the UI to a beginner. Cover: opening the URL (http://localhost:8069 for the local demo) and
    logging in (admin/admin on the demo — warn to change it). Then a TOUR of the Spiffy interface: the dark top
    navbar, the 9-dot **app launcher** (apps_home.png) and how to switch apps, the user/company menu and language
    switch, the vertical **quick-action rail** (favourite, search, full-screen, zoom, bookmark). Then explain the
    common screen types every app shares: **list view**, **form view**, **kanban/dashboard**, the **status bar**
    (draft → confirmed → done lifecycle, top-right), **smart buttons**, the **chatter** (messages/log on records),
    and the **search box with Filters / Group By**. Explain breadcrumbs and the New/Save/discard pattern. Use
    figures: login.png, apps_home.png, and point to sale_order.png (form anatomy), products_list.png (list),
    inventory_overview.png (kanban dashboard).`,
    figs: ['login.png', 'apps_home.png', 'sale_order.png', 'products_list.png', 'inventory_overview.png'],
  },
  {
    key: 'roles', title_en: '3. Roles & Permissions', title_ar: '3. الأدوار والصلاحيات',
    gt: ['roles.json', 'form_res_users.json', 'demo.json'],
    scope: `Explain in plain words what access rights are and why they matter (each person sees only what their job
    needs). Present the demo's six users (from roles.json users) in a table: Name | Login | Role | What they can do.
    Then a table of the standard application access groups (from roles.json categories: Sales, Purchase, Inventory,
    Accounting, Administration) with the levels each offers (e.g. Sales User vs Administrator; Accounting Invoicing
    vs Accountant vs Advisor) and what each level unlocks. Explain how to read/set a user's access on the user form's
    Access Rights tab. Step-by-step: create a user and assign a role. Figures: users_list.png, user_role.png.`,
    figs: ['users_list.png', 'user_role.png'],
  },
  {
    key: 'config_company', title_en: '4. Configuration — Company, Currencies, Taxes & Accounts',
    title_ar: '4. الإعدادات — الشركة والعملات والضرائب والحسابات',
    gt: ['demo.json', 'menu_tree.json', 'form_res_currency.json'],
    scope: `Plain-language setup, in order. (a) **Company**: Settings → Users & Companies → Companies; field table
    (name, address, city, country=Sudan, phone, email, tax id, currency). (b) **Currencies & exchange rates**: the
    base currency is SDG, USD is the reference; how to enable multi-currency; the USD record's **Rates** tab with the
    dated history (list the real rates from demo.json usd_rates: 2,400→4,500). Explain dated rates in plain words (each
    document is valued at the rate of its date; you just add a new line when the rate moves). (c) **Taxes**: the 15%
    sale and 15% purchase taxes (Sudan) from demo.json. (d) **Chart of accounts**: what it is in one sentence and
    where to find it. Figures: company.png, currencies_list.png, currency_usd.png, taxes_list.png, chart_of_accounts.png,
    settings_general.png.`,
    figs: ['company.png', 'currencies_list.png', 'currency_usd.png', 'taxes_list.png', 'chart_of_accounts.png', 'settings_general.png'],
  },
  {
    key: 'config_partners', title_en: '5. Configuration — Customers & Suppliers',
    title_ar: '5. الإعدادات — العملاء والموردون',
    gt: ['form_res_partner.json', 'demo.json', 'menu_tree.json'],
    scope: `Contacts = customers AND suppliers (one contact can be both; never duplicate). How to reach Contacts.
    Full field tables grouped by the contact form's tabs (use form_res_partner.json pages in order: Contacts &
    Addresses, Sales & Purchase, Payment Follow-up, Accounting) — explain the key fields a user actually sets
    (company vs individual, name, address, phone/email, then per tab: pricelist, payment terms, salesperson,
    purchase currency; receivable/payable accounts, bank accounts). Step-by-step: create a customer, create a foreign
    (USD) supplier. Reference the real demo partners (Khartoum Teaching Hospital; Gulf MedTrade FZE (USD), Dubai).
    Figures: contacts_list.png, contact_customer.png, contact_customer_salespurchase.png, contact_customer_accounting.png,
    contact_supplier.png.`,
    figs: ['contacts_list.png', 'contact_customer.png', 'contact_customer_salespurchase.png', 'contact_customer_accounting.png', 'contact_supplier.png'],
  },
  {
    key: 'config_banks', title_en: '6. Configuration — Banks, Cash Safes & Journals',
    title_ar: '6. الإعدادات — البنوك وخزائن النقد ودفاتر اليومية',
    gt: ['form_account_journal.json', 'demo.json', 'menu_tree.json'],
    scope: `Explain a **journal** in one plain sentence (a book where money/document movements are recorded). Explain
    the demo's clean journal set from demo.json (Customer Invoices, Vendor Bills, Bank of Khartoum (SDG), USD Bank
    Account, Main Cash Safe (SDG), USD Cash Safe). Make the key point: a **bank** = a Bank-type journal (+ a bank
    record with SWIFT/BIC); a **money safe / cash box** = a Cash-type journal (one per physical safe). Field table for
    the bank journal form (from form_account_journal.json key fields). Step-by-step: create a bank + bank journal, and
    create a cash safe. Figures: journals_list.png, journal_bank.png.`,
    figs: ['journals_list.png', 'journal_bank.png'],
  },
  {
    key: 'config_inventory', title_en: '7. Configuration — Warehouses, Locations, Units & Categories',
    title_ar: '7. الإعدادات — المستودعات والمواقع والوحدات والفئات',
    gt: ['form_stock_warehouse.json', 'form_stock_location.json', 'form_product_category.json', 'demo.json', 'menu_tree.json'],
    scope: `(a) **Warehouses**: the two real ones (Khartoum Central / KRT, Port Sudan / PRT); field table from
    form_stock_warehouse.json; receipt/delivery steps explained simply. (b) **Locations**: internal sub-locations
    (Cold Storage (2-8C), Quarantine, Expired / Damaged) and what each is for; explain a **putaway rule** (auto-routes
    a product to a location on receipt — e.g. insulin → Cold Storage). (c) **Units of Measure**: buy/stock/sell in
    different units (e.g. Box of 100 vs unit). (d) **Product categories**: the three categories and how they control
    costing (FIFO) and removal (FEFO); field table from form_product_category.json (costing method, valuation, removal
    strategy) with a plain note that the demo uses periodic valuation. Figures: warehouses.png, locations_list.png,
    uom_list.png, categories_list.png.`,
    figs: ['warehouses.png', 'locations_list.png', 'uom_list.png', 'categories_list.png'],
  },
  {
    key: 'products', title_en: '8. Products & Inventory Items', title_ar: '8. المنتجات وأصناف المخزون',
    gt: ['form_product_template.json', 'form_stock_lot.json', 'form_stock_warehouse_orderpoint.json', 'demo.json'],
    scope: `The product catalogue and how to register an item. Field tables grouped by the product form tabs (order
    from form_product_template.json: General Information, Sales, Purchase, Inventory, Accounting) — explain the fields
    a medical distributor sets (name, internal reference/SKU, barcode, product type=Goods, category, cost, sales price;
    Sales tab; Purchase tab incl. vendor pricelist; Inventory tab: Tracking=By Lots, Expiration Date on, routes,
    lead times; Accounting tab). Explain the smart buttons (On Hand, Forecasted, Reordering, etc. from smart_buttons).
    Then: **Lots/batches & expiry** (field table from form_stock_lot.json; how lots+expiry drive FEFO and recalls),
    **Reordering rules** (min/max — list the real ones from demo.json: Paracetamol 50/200, Insulin 20/80, Gloves
    30/120), and **checking stock on hand** (On Hand view / smart buttons). Use the real 10-product table from
    demo.json (ref, category, cost, price, tracking, on-hand). Figures: products_list.png, product_insulin.png,
    product_insulin_inventory.png, product_insulin_purchase.png, lots_list.png, lot_insulin.png, reordering_rules.png,
    onhand_quants.png.`,
    figs: ['products_list.png', 'product_insulin.png', 'product_insulin_inventory.png', 'product_insulin_purchase.png', 'lots_list.png', 'lot_insulin.png', 'reordering_rules.png', 'onhand_quants.png'],
  },
  {
    key: 'warehouse', title_en: '9. Warehouse Operations', title_ar: '9. عمليات المستودع',
    gt: ['form_stock_picking.json', 'demo.json', 'menu_tree.json'],
    scope: `The Inventory app overview (operation-type cards with counts). Then the three operations, each with a
    field/function explanation (from form_stock_picking.json buttons/statusbar) and step-by-step: **Receipts** (goods
    in from a PO; enter lot number + expiry, then Validate; putaway may route to Cold Storage), **Deliveries** (goods
    out from an SO; FEFO reserves soonest-to-expire lots; Validate to ship), **Internal transfers** (move stock between
    locations, e.g. to Cold Storage). Explain the picking status bar (Draft → Waiting → Ready → Done) and key buttons
    (Validate, Check Availability, Return, Print). Figures: inventory_overview.png, transfers_all.png, receipt_form.png,
    delivery_form.png, locations_list.png.`,
    figs: ['inventory_overview.png', 'transfers_all.png', 'receipt_form.png', 'delivery_form.png', 'locations_list.png'],
  },
  {
    key: 'procurement', title_en: '10. Procurement (Purchasing)', title_ar: '10. المشتريات',
    gt: ['form_purchase_order.json', 'demo.json'],
    scope: `The full purchasing flow (RFQ → Purchase Order → Receipt → Vendor Bill) with step-by-step. Field tables
    for the purchase order form grouped by its tabs (from form_purchase_order.json: Products, Invoices and Incoming
    Shipments, Other Information) and the header functions/status bar (RFQ, RFQ Sent, Purchase Order; buttons Confirm
    Order, Create Bill, Receipt, Send by Email, etc.). Explain vendor pricelists, multi-currency purchasing (USD), and
    Bill Control = received quantities. **Worked example** using the REAL demo order P00002 from Gulf MedTrade: 50
    Insulin @ $14 + 10 BP Monitors @ $42 → $1,288 total shown with the SDG equivalent (~5,796,000 SDG at 4,500). Mention
    the draft RFQ P00004. Figures: purchase_orders.png, po_usd.png, rfq_list.png, po_rfq.png.`,
    figs: ['purchase_orders.png', 'po_usd.png', 'rfq_list.png', 'po_rfq.png'],
  },
  {
    key: 'sales', title_en: '11. Sales', title_ar: '11. المبيعات',
    gt: ['form_sale_order.json', 'demo.json'],
    scope: `The selling flow (Quotation → Sales Order → Delivery → Customer Invoice) with step-by-step. Field tables
    for the sales order form grouped by tabs (from form_sale_order.json: Order Lines, Optional Products, Other Info)
    and the header functions/status bar (Quotation, Quotation Sent, Sales Order; buttons Confirm, Send by Email, Create
    Invoice; smart buttons Delivery/Invoice). Explain pricelists & currency (order currency follows the customer's
    pricelist; domestic = SDG). **Worked example** using REAL demo order S00001 to Khartoum Teaching Hospital: 50
    Paracetamol + 20 Gloves + 30 Syringes, priced in SDG, total 2,038,950 SDG (incl. 265,950 VAT at 15%), delivered under
    FEFO and invoiced as INV/2026/00001. Mention the draft quotation S00003 (Sudanese Red Crescent). Figures:
    sales_dashboard.png, quotations_list.png, sale_orders_list.png, sale_order.png, sale_quotation_draft.png.`,
    figs: ['sales_dashboard.png', 'quotations_list.png', 'sale_orders_list.png', 'sale_order.png', 'sale_quotation_draft.png'],
  },
  {
    key: 'accounting', title_en: '12. Accounting', title_ar: '12. المحاسبة',
    gt: ['form_account_move.json', 'form_account_payment.json', 'form_account_payment_register.json', 'form_account_journal.json', 'form_account_bank_statement.json', 'demo.json', 'menu_tree.json'],
    scope: `THE PRIORITY CHAPTER — write it long, gentle and complete for someone with no accounting background. Start
    by explaining in plain words: invoice vs bill, debit/credit need NOT be understood by the user because the system
    posts entries automatically, what "post" means, what a payment is, what reconciliation is. Cover, each with menu
    path + field/function tables + step-by-step:
    (1) **The Accounting dashboard** (cards per journal; Unpaid/Late counts; balances) — accounting_dashboard.png.
    (2) **Customer invoices**: list + the invoice form field tables grouped by tab (from form_account_move.json:
        Invoice Lines, Journal Items, Other Info), the status bar (Draft→Posted→Cancelled), buttons (Confirm/Post,
        Register Payment, Credit Note, Send). Use the REAL demo invoices from demo.json (INV/2026/00001 paid 2,038,950;
        the overdue ones 00003/00004 and current 00005). customer_invoices_list.png, customer_invoice.png,
        customer_invoice_overdue.png.
    (3) **Vendor bills**: same idea; real bills BILL/2026/05/0001 (SDG, 5,635,000) and 0002 (USD, 483). vendor_bills_list.png,
        vendor_bill_usd.png.
    (4) **Payments & money safes**: register a payment from an invoice/bill choosing a bank journal or a cash safe;
        the Register Payment wizard fields (from form_account_payment_register.json) and the payment form
        (form_account_payment.json). Real payments from demo.json. payments_list.png, payment_form.png.
    (5) **Bank reconciliation**: plain explanation (match what the bank statement says against the invoices/payments in
        the system); the real statement STMT/2026/06/KRT; the reconcile screen. bank_reconcile.png.
    (6) **Reports**: Balance Sheet, Profit & Loss, General/Partner Ledger, Trial Balance, Aged Receivable/Payable, Tax
        report, and the Cash/Day/Bank Book — say what each tells you in one line. report_balance_sheet.png,
        report_aged_receivable.png.
    (7) **Fiscal year & lock dates** and **customer follow-up / dunning** (chasing overdue invoices) — explain simply.
    Provide a table mapping capability → which add-on provides it (Invoicing core; om_account_accountant; accounting_pdf_reports;
    om_account_daily_reports; account_reconcile_oca; om_account_followup).`,
    figs: ['accounting_dashboard.png', 'customer_invoices_list.png', 'customer_invoice.png', 'customer_invoice_overdue.png', 'vendor_bills_list.png', 'vendor_bill_usd.png', 'payments_list.png', 'payment_form.png', 'bank_reconcile.png', 'report_balance_sheet.png', 'report_aged_receivable.png'],
  },
  {
    key: 'multicurrency', title_en: '13. Multi-Currency Operations', title_ar: '13. عمليات تعدّد العملات',
    gt: ['demo.json', 'form_res_currency.json'],
    scope: `How the system keeps the books in SDG while letting you transact in USD. Explain: base currency SDG (all
    reports in SDG), reference currency USD (imports & quotes), dated rates (the rate of a document's date is used —
    list the real 2,400→4,500 history), and that a foreign (USD) bank/cash journal holds USD and is revalued at period
    close. Table: Document | where its currency comes from (PO=supplier purchase currency/pricelist; bill=inherited;
    SO=customer pricelist; invoice=inherited). Reuse po_usd.png and vendor_bill_usd.png and currency_usd.png.`,
    figs: ['currency_usd.png', 'po_usd.png', 'vendor_bill_usd.png'],
  },
  {
    key: 'medical', title_en: '14. Medical-Supply Specifics', title_ar: '14. خصوصيات المستلزمات الطبية',
    gt: ['demo.json'],
    scope: `Why this ERP fits a medical distributor. Cover, each in plain words with the relevant real example:
    **batch/lot traceability** (recalls & audits), **expiry control** (per-lot expiration dates, near-expiry flagged),
    **FEFO** (earliest-expiring issued first), **cold chain** (insulin → Cold Storage via putaway), **quarantine /
    expired-damaged** locations, and **imports** (USD purchases valued in SDG; landed costs — freight/customs — can be
    added to unit cost). Figures: product_insulin_inventory.png, lot_insulin.png, locations_list.png.`,
    figs: ['product_insulin_inventory.png', 'lot_insulin.png', 'locations_list.png'],
  },
  {
    key: 'journeys', title_en: '15. Everyday Workflows by Role', title_ar: '15. مسارات العمل اليومية حسب الدور',
    gt: ['roles.json', 'demo.json', 'menu_tree.json'],
    scope: `End-to-end, step-by-step "a day in the life" journeys that tie the modules together, one per role. For each:
    a short intro, then a numbered ol of the exact clicks/menus. Use the real demo data.
    (1) **Procurement Officer (Amira)**: review reordering suggestions → create RFQ → confirm PO (incl. the USD import
        from Gulf MedTrade) → receive goods with lot+expiry → create vendor bill.
    (2) **Sales Representative (Khalid)**: create a quotation for a hospital → confirm the sales order → hand off the
        delivery → create & send the invoice.
    (3) **Warehouse Keeper (Sara)**: process receipts (enter lots/expiry, validate), run an internal transfer to Cold
        Storage, validate deliveries under FEFO, check on-hand stock.
    (4) **Accountant (Mohammed)**: post invoices/bills, register payments via bank or cash safe, reconcile the bank
        statement, run Aged Receivable and the Tax report, chase overdue invoices.
    (5) **General Manager (Layla)**: read the dashboards, review the sales/purchase pipeline, check stock and the
        financial reports. Reuse figures: po_usd.png, receipt_form.png, sale_order.png, delivery_form.png,
        payment_form.png, accounting_dashboard.png.`,
    figs: ['po_usd.png', 'receipt_form.png', 'sale_order.png', 'delivery_form.png', 'payment_form.png', 'accounting_dashboard.png'],
  },
  {
    key: 'demo_reference', title_en: '16. Demo Data Reference', title_ar: '16. مرجع البيانات التجريبية',
    gt: ['demo.json'],
    scope: `A precise reference of everything pre-loaded in the erpmedsupply demo, taken EXACTLY from demo.json. Tables
    for: company & currencies (+ the 5 dated USD rates 2,400→4,500), warehouses & internal locations, the 10 products
    (ref, category, cost, sales price, tracking, on-hand), customers, suppliers, journals (banks + cash safes), the
    six users/roles, purchase orders, sales orders, customer invoices (with totals/tax/due/payment status), vendor
    bills, payments, reordering rules, lots with expiry, and the bank statement. Numbers must match demo.json exactly.`,
    figs: [],
  },
  {
    key: 'admin', title_en: '17. Administration, Maintenance & Glossary', title_ar: '17. الإدارة والصيانة ومسرد المصطلحات',
    gt: ['demo.json', 'roles.json'],
    scope: `(a) **Users & access**: where to manage users, assign roles (link to ch.3). (b) **Backups**: back up the
    database regularly, keep off-site copies before upgrades. (c) **Rebuilding the demo**: the project seed scripts can
    recreate it (point to project docs; do not paste commands). (d) **Production hardening** (warn): change all default
    passwords, disable the database manager, enable HTTPS, restrict the database filter. (e) A **Glossary** table of
    plain-language definitions: SKU/Internal Reference, Lot/Batch, FEFO, FIFO, Putaway rule, Journal, RFQ,
    Reconciliation, Base currency, Pricelist, Receivable/Payable, Posting, Fiscal year. Figures: users_list.png,
    settings_general.png.`,
    figs: ['users_list.png', 'settings_general.png'],
  },
]

const STATUS_SCHEMA = {
  type: 'object',
  required: ['key', 'wrote_file', 'n_blocks_en', 'n_blocks_ar'],
  properties: {
    key: { type: 'string' },
    wrote_file: { type: 'boolean' },
    n_blocks_en: { type: 'integer' },
    n_blocks_ar: { type: 'integer' },
    figures_used: { type: 'array', items: { type: 'string' } },
    issues: { type: 'array', items: { type: 'string' } },
  },
}

function gtList(ch) {
  return ch.gt.map(f => `${GT}/${f}`).join('\n  - ')
}

function draftPrompt(ch) {
  return `${STYLE}

================ YOUR CHAPTER ================
key: ${ch.key}
title_en: ${ch.title_en}
title_ar: ${ch.title_ar}

SCOPE:
${ch.scope}

Suggested figures (only use those present in figures.json): ${ch.figs.join(', ') || '(none)'}

STEP 1 — READ these authoritative ground-truth files (they override your assumptions; do not invent):
  - ${gtList(ch)}
  - ${GT}/figures.json   (the only screenshots that exist)
Use Read or 'cat' via Bash. For long form_*.json files, focus on each field's "label", "type", "help",
"page" and on the "buttons"/"smart_buttons"/"statusbar_states" arrays.

STEP 2 — WRITE the chapter as a single valid JSON object to: ${CONTENT}/${ch.key}.json
Keys: key, title_en, title_ar, blocks_en, blocks_ar (see OUTPUT FORMAT). Comprehensive and accurate.
Make blocks_ar a faithful Arabic mirror of blocks_en (same headings/tables/steps/figures).

STEP 3 — Return the status object (key, wrote_file=true, n_blocks_en, n_blocks_ar, figures_used, issues).`
}

function verifyPrompt(draft, ch) {
  return `You are a meticulous fact-checker and plain-language editor for the Medical-Supply ERP manual.
Chapter file to verify and FIX IN PLACE: ${CONTENT}/${ch.key}.json

STEP 1 — Read the chapter file AND these ground-truth files:
  - ${gtList(ch)}
  - ${GT}/figures.json

STEP 2 — Adversarially VERIFY every factual claim and correct anything wrong:
  - Field labels must exist (match a "label" in the relevant form_*.json). Fix or remove invented fields.
  - Menu paths must match menu_tree.json (App → Menu → Sub-menu).
  - Button / status names must match the form_*.json "buttons"/"smart_buttons"/"statusbar_states".
  - Every numeric figure, record name, total, rate, quantity, due date and payment status must match demo.json EXACTLY.
  - Every {"t":"fig","file":...} must name a file that exists in figures.json; the caption must match what that
    figure actually shows. Remove figs whose file is absent.
  - You may run 'docker compose exec -T db psql -U odoo -d erpmedsupply -c "..."' from
    /Users/waelabdalla/Documents/ephem-deploy to double-check a number if unsure.

STEP 3 — EDIT for the audience: ensure it is simple and explanatory for someone with NO accounting/management
  background, well organized, detailed, and that it showcases the system's functions. Ensure blocks_ar mirrors
  blocks_en exactly (same structure, correct fluent Arabic, correct Arabic UI terms, no "ePHEM" anywhere).

STEP 4 — OVERWRITE ${CONTENT}/${ch.key}.json with the corrected, valid JSON (same shape). Then return the status
  object (key, wrote_file=true, n_blocks_en, n_blocks_ar, figures_used, issues=[list of concrete corrections you made]).`
}

phase('Draft')
const results = await pipeline(
  CHAPTERS,
  (ch) => agent(draftPrompt(ch), { label: `draft:${ch.key}`, phase: 'Draft', schema: STATUS_SCHEMA }),
  (draftStatus, ch) => agent(verifyPrompt(draftStatus, ch), { label: `verify:${ch.key}`, phase: 'Verify', schema: STATUS_SCHEMA }),
)

const ok = results.filter(Boolean)
log(`chapters processed: ${ok.length}/${CHAPTERS.length}`)
return {
  total: CHAPTERS.length,
  done: ok.map(r => r.key),
  issues: ok.flatMap(r => (r.issues || []).map(i => `${r.key}: ${i}`)),
  block_counts: ok.map(r => ({ key: r.key, en: r.n_blocks_en, ar: r.n_blocks_ar })),
}
