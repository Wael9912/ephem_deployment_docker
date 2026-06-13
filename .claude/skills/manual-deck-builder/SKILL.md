---
name: manual-deck-builder
description: Build and maintain the customer-facing documents for this Odoo ERP — the bilingual (EN/AR) user manual (Word/PDF) and the 15-slide sales/live-demo deck (PDF). Use when asked to create, edit, restyle, re-flow, translate, or rebuild the manual or the deck, fix a layout/RTL defect, add an Arabic version, or change slide content/branding.
---

# Manual & deck development

Two customer-facing artifacts are generated from real demo data + real Odoo
screenshots. Both render with **WeasyPrint inside the `odoo` container** (the only
place the font + Pango stack lives) and embed the **Alexandria** Arabic font and all
images as base64, so the HTML/PDF is fully self-contained.

| Artifact | Source | Build | Output |
|---|---|---|---|
| **Deck** (sales / live demo) | `scripts/build_deck.py` | `bash scripts/build_deck_pdf.sh` | `docs/deck/Medical-Supply_ERP_Demo_Deck_{EN,AR}.{html,pdf}` (15 slides, 16:9) |
| **Manual** (user guide) | `scripts/build_manual.py` + `docs/manual/_content/*.json` | `bash scripts/build_manual_pdf.sh` | `docs/manual/Medical-Supply_ERP_User_Manual_{EN,AR}.{docx,pdf}` |

Companion: `docs/deck/PRESENTER_GUIDE.md` (the live-demo cheat-sheet — slide-by-slide
click paths + the number to say). Demo data & seeding are owned by the
**erp-medsupply-demo** skill; this skill owns the *documents*.

## Golden rules
- **Every figure and screenshot is real.** Numbers come from the running `erpmedsupply`
  demo (`docs/manual/_ground_truth/demo.json`); screenshots are real captures in
  `docs/manual/img/{en,ar}/` (identical filenames per language). After any reseed,
  re-verify the numbers on the slides/manual and re-capture screens.
- **Bilingual, always.** Build EN and AR. AR is full RTL with the Arabic screenshot set.
- **Render in the container, QA out of it.** The host has no Pango/poppler and can't
  import WeasyPrint. Rasterize the PDF *inside* the container and copy PNGs out to Read:
  ```bash
  docker compose cp docs/deck/Medical-Supply_ERP_Demo_Deck_EN.pdf odoo:/tmp/d.pdf
  docker compose exec -T odoo bash -lc 'pdftoppm -png -r 80 /tmp/d.pdf /tmp/d'
  docker compose cp odoo:/tmp/d-07.png /tmp/qa.png   # then Read /tmp/qa.png
  ```
- A container recreate **drops runtime pip/apt installs** → if you hit
  `No module named weasyprint` or missing `pdftoppm`, reinstall:
  ```bash
  docker compose exec -u root -T odoo bash -lc 'apt-get install -y -qq libpango-1.0-0 libpangocairo-1.0-0 libpangoft2-1.0-0 poppler-utils && pip install --break-system-packages -q weasyprint'
  ```

## The deck — `scripts/build_deck.py`
`python3 scripts/build_deck.py {en|ar}` writes one self-contained HTML; the `.sh`
builds both and renders both PDFs. The deck is **absolutely positioned on a 1280×720
canvas** (`@page size:1280px 720px`; each `.slide` is `position:relative;` with
`page-break-after:always`). Audience = an Excel-only manager; presenter-driven.

### 15-slide flow (keep it ≤15; cut, don't cram)
1. Cover → 2. The challenge (Excel cracks) → 3. **One connected system** (concept in
bullets + the real app launcher) → **4–10 capability slides** you can SHOW LIVE
(catalogue · expiry/cold-chain · auto-reorder · multi-currency · quote-to-cash ·
receivables/cash · roles+Arabic) → 11. Excel-vs-ERP table → 12. Cost & growth →
13. Switching (import/train/run) → 14. 4-week roadmap → 15. Next steps.
Problem → proof (live) → decision. Capability slides 4–10 each ground a **real number**
and carry a **▶ SHOW LIVE** band with the exact click-path.

### How it's structured (edit here)
- Copy is bilingual via `T(en, ar)` — every string passes through it. Numbers stay
  Western digits (consistent with the figures and screenshots).
- Layout helpers are RTL-aware via the global `RTL`/`DIR`/`ALIGN`: `pos(x,y,w,h)`
  anchors from the **right** edge when RTL (mirrors the whole canvas), text helpers
  add `direction/text-align`, `bullets`/`chips`/`shot`/`live_cue` flip margins & order.
- Capability slides use `cap(...)` (one screenshot) or `cap2(...)` (two). `shot()` is a
  browser-framed screenshot; `fit_w()` caps its height so the caption never collides
  with the cue band. `live_cue()` is the gold SHOW-LIVE band.
- Reusable line icons are inline SVG in `_ICON` — **never emoji** (no emoji font in the
  container).
- To rebrand: edit `DATE`, the cover/close text, and the footer brand string.

### Deck gotchas (each cost real iterations — do not relearn them)
- **`display:inline-flex` renders as a full-width block flex in WeasyPrint** → it blows
  pill/chip rows to one-per-line and collapses the SHOW-LIVE icon chip into a tall
  sliver. Use `display:inline-block` for chips (inline-block dot, `vertical-align:middle`);
  for the cue chip use a fixed-size `display:flex` item (`flex:none;width;height`), and
  draw the play glyph **filled** (`<path … fill="#fff"/>`) — a stroke-only icon at
  `stroke-width:0` is invisible.
- **Tables: use a real `<table dir="rtl|ltr">`, NOT flexbox.** WeasyPrint mis-mirrors
  flex rows under a `direction:rtl` page (header and body diverge, the start-column
  overflows the right edge). A `<table>` with the `dir` attribute mirrors columns
  natively in both languages. Position the table with a `pos()` wrapper.
- **RTL position mirroring**: `pos()` swaps `left`→`right`; that cleanly mirrors every
  absolutely-positioned element. But WeasyPrint mishandles an explicit `left:` (or
  `text-align`) on some elements inside an rtl page — prefer `pos()` (right-anchored)
  and flex `justify-content` over raw `text-align` for positioned content.
- **A positioned `display:flex` element mis-renders under an rtl page** (vanishes or
  shifts off-screen): the cover brand mark, the roadmap number circles and the close-slide
  step rows all disappeared in AR until rebuilt **without** positioned flex. Fixes:
  position the row, then lay its children with `display:inline-block;vertical-align:middle`
  (mark, steps), or center a lone glyph with `text-align:center;line-height:<h>px` instead
  of flex (number circles).
- **The full-width cue/callout bands are NOT exempt** (this was the old advice — it was
  wrong). A right-anchored positioned `display:flex` band pushes its **leading** flex child
  clean off the right edge of the slide under rtl: the `live_cue` SHOW-LIVE band dumped its
  play-chip + `اعرض مباشرةً` label past the right edge, and the teal `note_band` callout
  pushed its leading tag icon off-screen (less obvious — it's just an icon). The body text
  still landed correctly, which is what made it look like a half-broken band. Fix: build
  these bands with **inline-block flow, not flex** — `chip`/`icon` + `label` + `body` all
  `display:inline-block;vertical-align:middle` inside a band carrying `txtdir()` +
  `line-height:<band-h>px;white-space:nowrap;overflow:hidden`. `line-height` does the
  vertical centering (the cover/roadmap pattern); `txtdir` right-aligns so the chip/icon
  leads from the right in AR and the left in EN. Only the roadmap's bottom band survives as
  flex because it's `justify-content:center` with no leading child.
- **Flex icon-centering breaks under inherited `direction:rtl`** → icons drift to a box
  corner. Add `direction:ltr` to every icon-only box (it contains no RTL text, so this is
  safe) so `align-items/justify-content:center` behaves like the working EN path. `icon()`
  also carries `vertical-align:middle` for line-height/inline-block centering.
- **Screenshots are tall** (all 2960×1880 ≈ 1.57:1). `fit_w(name, w_max, h_max)` shrinks
  width so the framed shot + caption stay above the cue band (`y=612`); single shots cap
  at 393px image height, dual at 309px.
- The footer page number must be `direction:ltr` or RTL bidi flips "6 / 15" to "15 / 6".

## The manual — `scripts/build_manual.py`
Content lives in `docs/manual/_content/<chapter>.json` (`{title_en,title_ar,blocks_en,
blocks_ar}`), drafted+verified by the `scripts/wf_manual_content.js` Workflow against the
ground-truth dumps. `build_manual.py` assembles them in `CHAPTER_ORDER`, renders DOCX
(python-docx) and HTML; the `.sh` renders both PDFs. AR is RTL + Alexandria; **never
wkhtmltopdf for Arabic**. Manuals must not mention "ePHEM".

## Capturing/refreshing screenshots
Owned by the demo skill (`scripts/capture_screens.py {en|ar}`,
`docker compose restart odoo` before each capture so the worker picks up the lang).
**⚠️ STALE — the live UI is now the Nile theme (Spiffy retired/deleted 2026-06-13), but the
committed screenshots + this script + both decks STILL show the dead Spiffy UI.** Re-capture is
the deferred Phase-1 doc task: `capture_screens.py` must be updated for `web_responsive` chrome
first — the Spiffy app-launcher opener `a.appDrawerToggle` no longer exists; web_responsive uses
`button.o_grid_apps_menu__button` (verify against the live DB). The switchover also requires an
`intro`/`interface` chapter rewrite (de-Spiffy terminology + document the new **Theme Settings**
dialog = `nile_config`, now a tabbed panel (Brand / Typography / Display) with palette presets, an
inline **HSV color picker**, a company **Google-Fonts link**, per-user font/size/density/**dark
mode**/chatter, plus a **systray globe language switcher** — capture in light;
mention dark exists). Both languages produce the **same filenames** — that's what lets the
deck/manual switch the image set by language with one flag. After a reseed, record IDs shift →
update the `ID` dict in `capture_screens.py` before recapturing.

## Rebuild checklist
```bash
bash scripts/build_deck_pdf.sh      # EN + AR deck
bash scripts/build_manual_pdf.sh    # EN + AR manual
# QA: rasterize a few pages in the container and Read the PNGs (see Golden rules)
```
