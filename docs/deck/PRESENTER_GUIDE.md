# Presenter Guide — Medical-Supply ERP Live Demo

A one-page companion to **`Medical-Supply_ERP_Demo_Deck.pdf`**. The deck carries the
story; this tells you exactly what to open in the system at each **▶ SHOW LIVE** cue,
and the number to say out loud. Keep the PDF on screen, switch to the live system on the
cues, then come back.

## Before the meeting (pre-flight)
- Start the stack and confirm the app is up: open **http://localhost:8069**
- Database: **erpmedsupply**  ·  Login: **admin / admin**  (demo only — change for real use)
- Have these tabs/records pre-opened so you don't fumble: **Sales ▸ S00001**, **Accounting ▸ Dashboard**, **Purchase ▸ P00002**, **Inventory ▸ Lots/Serial Numbers**.
- Optional: a second user logged in as Arabic (e.g. **layla / demo1234** with language Arabic) for the bilingual moment.

## Demo data cheat-sheet (all real, seeded)
| Thing | Where | The number / fact to say |
|---|---|---|
| Product catalogue | Inventory ▸ Products | 10 items, 3 categories; Insulin on-hand **50** |
| Insulin lot + cold chain | Inventory ▸ Lots ▸ **LOT-GULF-01** | Expiry **09 Jun 2027**, lives in **Cold Storage (2–8°C)** |
| Reordering rules | Inventory ▸ Operations ▸ Reordering Rules | Insulin **20/80**, Paracetamol **50/200**, Gloves **30/120** |
| USD purchase | Purchase ▸ **P00002** (Gulf MedTrade) | **$1,288.00** ⇄ **5,796,000 SDG** |
| FX history | Accounting ▸ Configuration ▸ Currencies ▸ USD | 1 USD = **2,400 → 4,500 SDG** (dated) |
| Sale → invoice | Sales ▸ **S00001** → its invoice | Order **2,038,950 SDG**, invoice **INV/2026/00001 = PAID** |
| Cash position | Accounting ▸ Dashboard | **3 unpaid (3,966,350 SDG)**, **2 late**, bank **3,924,950 SDG** |
| Roles | Settings ▸ Users ▸ **Layla (General Manager)** ▸ Access Rights | 6 users; warehouse keeper ≠ accountant access |

## Slide-by-slide live cues
- **Slide 5 — A working system:** open the **9-dot app launcher** (top-left). "These are the real apps, one login."
- **Slide 7 — Catalogue:** *Inventory ▸ Products*, search **Insulin**, open the card. Point at **On Hand**, cost, price, 15% tax.
- **Slide 8 — Expiry & cold chain:** *Inventory ▸ Lots/Serial Numbers*, open **LOT-GULF-01**. Show the **expiry date** and that it sits in **Cold Storage (2–8°C)**. "Find every unit of a bad batch in seconds."
- **Slide 9 — Re-ordering:** *Inventory ▸ Operations ▸ Reordering Rules*. Point at On-Hand vs **Min/Max** and the **To-Order** column. "Insulin is set to reorder at 20."
- **Slide 10 — Warehouses:** *Inventory ▸ Configuration ▸ Warehouses* then **Locations**. Show **Cold Storage / Quarantine / Expired**.
- **Slide 11 — Multi-currency:** *Purchase ▸ P00002*. Show the **$1,288 total** and the **5,796,000 SDG** equivalent right beneath it.
- **Slide 12 — Quote to cash:** *Sales ▸ S00001*, then click through to its **invoice**. Show the green **PAID** banner. "Same order, becomes the invoice — nothing re-typed."
- **Slide 13 — Cash position:** *Accounting ▸ Dashboard*. Point at **Unpaid / Late** and the live **bank balance**. Optional: print **Aged Receivable**.
- **Slide 14 — Roles:** *Settings ▸ Users ▸ Layla ▸ Access Rights*. "Each person sees only their part; every change is logged."
- **Slide 15 — Arabic:** switch your user language to **Arabic** and reload (or flip to the pre-logged Arabic session). Show the same screen **right-to-left**.

## If asked (quick answers)
- **"How much?"** → No per-user licence fees. Built on Odoo 18 **Community** + open-source (OCA). You pay for setup, training and support — not seats. You own your data.
- **"Can it grow?"** → Switch on Manufacturing, POS, HR, Barcode, e-Commerce later; custom modules built to fit. Nothing to rip out.
- **"Moving off Excel?"** → Import products/customers/opening stock straight from your sheets; run parallel; go live when ready.
- **"Training?"** → A 17-chapter bilingual (AR/EN) manual with 53 real screenshots already exists; role-based; hands-on rollout.
- **"Where does it run? Is it safe?"** → Your server or cloud; any browser; encrypted login; role-based access; automated daily backups.

## Tips
- Let *them* click when they lean in — buyers who touch it, buy it.
- Always say a real number ("3,966,350 pounds unpaid") — concreteness sells.
- If the live system hiccups, the deck screenshot is the same data — keep talking, recover quietly.

---
*Rebuild the deck after any data change:* `bash scripts/build_deck_pdf.sh`
