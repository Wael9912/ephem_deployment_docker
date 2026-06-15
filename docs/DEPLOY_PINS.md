# Deployment pins

Single source of truth for the **pinned versions** a production deployment of the
Sudan medical-supply ERP runs. Production clones each repo at its pinned **tag**
(a detached, reproducible checkout) — never a moving branch. Bump this file on
every release, then re-tag the repos to match.

| Repo | Pinned tag | Commit | Role |
|---|---|---|---|
| [`Wael9912/ephem_deployment_docker`](https://github.com/Wael9912/ephem_deployment_docker) | `erp-deployed` branch | — | deployment (compose, configs, scripts, docs) |
| [`Wael9912/erpmedsupply-addons`](https://github.com/Wael9912/erpmedsupply-addons) | `v18.0.1.0.0` | `0a5b028` | the 14 ERP addons → `/mnt/extra-addons` |
| [`Wael9912/odoo-nile-theme`](https://github.com/Wael9912/odoo-nile-theme) | `v18.0.2.5.1` | `310a2c2` | the `nile_*` theme stack (1 theme module `nile_theme` + brand packs) → `/mnt/nile-theme` |

> **Deployment branch (2026-06-15):** the go-to branch for a fresh server is now
> **`erp-deployed`** (was `nile-theme`). It carries the latest theme work plus the
> customer-provisioning tooling (`scripts/new-tenant.sh`) and the beginner/onboarding/
> hosting guides under `docs/`. Clone it on the server:
> `git clone -b erp-deployed https://github.com/Wael9912/ephem_deployment_docker.git ephem-deploy`.
> See `docs/First_Server_Setup_Hetzner.pdf` for the full first-time walkthrough.

## odoo-nile-theme `v18.0.2.5.1` (2026-06-15) — tag `310a2c2`

**Hotfix for `v18.0.2.5.0`.** That release put the GraphRenderer patch in
`chart_rtl.js`, which statically imports `@web/views/graph/graph_renderer` — a
module in a **lazy** sub-bundle that only loads with the graph view. That import
made the *whole* `chart_rtl.js` module lazy, so on every non-graph page (incl. the
Accounting dashboard and Inventory Overview) it never executed → the dashboard RTL
fix that shipped in `v18.0.2.4.0` silently stopped applying and the new inventory
patch never ran (live-confirmed: `@nile_theme/webclient/chart_rtl` was absent from
the loader on the dashboard page). Fix = move the GraphRenderer patch to its own
`graph_view_rtl.js` (still lazy, which is correct — it's only needed when a graph
renders); `chart_rtl.js` now imports only eager modules so the dashboard +
inventory patches load on every backend page again. **Verified live on
`erpmedsupply` (Arabic) reading the DEPLOYED bundle:** dashboard 5 charts +
inventory 6 bars + graph view all `rtl:true` / `x.reverse` / y-axis right; 0 JS
errors. **Deploy:** `-u nile_theme`, then **restart** Odoo (same as 2.5.0).

## odoo-nile-theme `v18.0.2.5.0` (2026-06-15) — tag `5341fee`

> ⚠️ Superseded by `v18.0.2.5.1` — do not pin 2.5.0 (the graph-view patch's lazy
> import deferred the eager dashboard/inventory patches; see the hotfix above).

Finishes the Arabic-RTL chart pass started in `v18.0.2.4.0` (which fixed only the
Accounting dashboard graphs) and fixes a contact-card paint defect. Assets/JS +
SCSS only — **no schema change, no new strings** → deploy is plain `-u nile_theme`
(no `--i18n-overwrite`), **then restart** Odoo. No business data touched.

- **Reporting graph view now mirrors in Arabic.** Sales/Purchase/Invoices
  Analysis (and any `graph` view) render through core's `GraphRenderer`, a
  *different* component from the dashboard field — it built Chart.js `options`
  with no direction awareness, so categories/time ran left→right and the value
  axis sat on the left. `GraphRenderer.prepareOptions` is now wrapped to stamp
  `rtl` + `scales.x.reverse` + `scales.y.position:"right"` under RTL (one wrap
  covers bar/line/pie). Drill-down `onClick` is unaffected (Chart.js hit-tests by
  data index, which `reverse` preserves).
- **Inventory Overview bar widgets now mirror in Arabic.** The operation-type
  cards use stock's `PickingTypeDashboardGraphField`, which subclasses the
  dashboard field but **overrides `getBarChartConfig`** — so it shadowed the
  parent patch and stayed LTR. Now patched too, **via the field registry** (not
  `import "@stock/..."`) so the generic theme stays installable on DBs without
  Inventory; a hard stock import would brick the whole backend bundle there.
- **Contact card top stroke no longer hidden by the avatar.** Full-bleed contact
  avatars (`.o_kanban_aside_full`) had square corners that sat proud of the
  card's rounded border, clipping the top/bottom "stroke" on the picture's side
  (only on cards *with* an avatar — hence "sometimes"). The avatar's leading
  (start) corners now round to the card radius + clip (logical props → correct in
  LTR and RTL).
- Mechanics: `static/src/webclient/dashboard_graph_rtl.js` renamed to
  `chart_rtl.js`; the RTL helper (`nileFlipChartForRtl`) is generalized and reused
  by all three chart patches. The dashboard graphs are unchanged (the helper still
  reverses their x-axis; the new y-axis-right is a no-op on their hidden axes).
- **Deploy:** `-u nile_theme`, then **restart** Odoo.
- Verified live on `erpmedsupply` (Arabic): graph view → `rtl:true, x.reverse,
  y on right`, dates newest-left/oldest-right; all 6 Inventory Overview bars
  mirror; contact avatars round on the leading edge. Pivot + KPI numbers already
  correct in core (numeric cells are `rtl:ignore` LTR by design).

## odoo-nile-theme `v18.0.2.4.0` (2026-06-15) — tag `71c7d1c`

Two user-reported fixes + one new configurator knob. Adds **one stored column**
(`res.company.nile_kanban_gap`) → a real schema change, plus a new `ar.po`
string, so deploy is `-u nile_theme,nile_brand_medsupply --i18n-overwrite`,
**then restart** Odoo. No business data is touched (existing companies get the
field default `separated`).

- **Arabic dashboard graphs now flip RTL.** The Accounting dashboard journal
  cards render their bar/line graphs through core's `web` `dashboard_graph` field
  (`JournalDashboardGraphField`), which builds Chart.js configs with **no
  direction awareness** — so in Arabic the axis labels translated but the chart
  never mirrored (bars/time ran left→right, tooltip stayed LTR). New
  `static/src/webclient/dashboard_graph_rtl.js` patches the two config getters to
  stamp `options.rtl` + `scales.x.reverse` when `localization.direction === "rtl"`
  (pure no-op in LTR). The generic Graph **reporting** view shares the same core
  gap — not patched here (out of scope; available on request).
- **Grouped kanban cards now read as separate rounded tiles.** Core stacks
  records with `margin: 0 0 -1px` (adjacent 1px borders collapse) and never
  rounds them, so cards looked like one attached block and the Corner knob never
  reached them. Grouped records now bind `border-radius` to the corner knob and
  use a real gutter; ungrouped dashboard tiles round all four corners (was
  top-only).
- **New "Kanban Cards" spacing knob** on the configurator Style tab + Companies
  → Nile Theme form: `nile_kanban_gap` = Attached (restores the flush core
  stack) / Separated (default — gutter + rounded) / Spaced (wider gutter). Wired
  through `res.company` → `ir_http` session → `data-nile-kanban-gap` attr →
  `theme_runtime.scss`, mirroring the `accent_strip` knob.
- **Deploy:** `-u nile_theme,nile_brand_medsupply --i18n-overwrite`, then
  **restart** Odoo.

## odoo-nile-theme `v18.0.2.3.0` (2026-06-15) — tag `1b3f498`

Two user-reported fixes + a no-code branding affordance. Adds a transient model
(`res.config.settings` inherit) and a view but **no new DB column** → effectively
an asset+view recompile; plain `-u nile_theme` (no `--i18n-overwrite` — no new
strings), **then restart** so the registry picks up the new transient model.

- **Logo no longer clipped.** The navbar/primary "Sudan MedSupply" wordmarks were
  live SVG `<text>` in Alexandria; an SVG used as `<img>` can't load the page
  webfont, so the wider fallback overflowed `viewBox="0 0 452 96"` and clipped the
  trailing "y". Both `nile_brand_medsupply` SVGs are now **outlined paths**
  (Alexandria 700 via fontTools) with a recomputed viewBox — identical on every
  client. (Sibling `nile_brand_cmp`/`nile_brand_ephem` lockups still use `<text>`:
  same latent bug, not deployed.)
- **Kanban count readable on dark palettes.** The column count chip rode
  `--nile-color-text-inverse`, which Bootstrap's `.text-900{color:#212529!important}`
  (in BOTH bundles) overrode → near-black on a dark brand chip (e.g. the **Slate**
  palette), unreadable. Now `--nile-color-on-brand` (white in light AND dark)
  `+ !important`, won back by selector specificity. The light progress bar (the
  "column indicator") is untouched.
- **Admin no-code logo upload.** The company branding fields (navbar logo /
  favicon / tab name) are now on **Settings → General Settings → "Nile Theme"**
  (`res.config.settings` related fields), so an admin swaps the navbar logo with
  no code. An uploaded `nile_menubar_logo` already takes precedence over the brand
  SVG; `object-fit: contain` renders any aspect ratio uncropped. (The same fields
  still live on the Companies form's "Nile Theme" tab.)
- **Deploy:** `-u nile_theme,nile_brand_medsupply`, then **restart** Odoo.
- Verified live on `erpmedsupply` (Slate palette): logo full + uncropped, count
  white on slate, the General Settings "Nile Theme" block renders.

## odoo-nile-theme `v18.0.2.2.0` (2026-06-14) — tag `239ad45`

**Production UX/QA pass** (6-expert adversarial review over live light/dark/RTL
screenshots; 30 verified findings). No schema change → **asset-only recompile**,
BUT `--i18n-overwrite` is still required (the `ar.po` was re-attributed from the
retired `nile_config` module to `nile_theme`).

- **Deploy:** `-u nile_theme,nile_brand_medsupply --i18n-overwrite`, then **restart**
  the Odoo server. ALSO clear any stale per-company `nile_menubar_logo` Binary so
  the rod-of-Asclepius SVG shows (the old `+`-cross raster was shadowing it):
  `env['res.company'].browse(cid).nile_menubar_logo = False` (commit).
- **Dark mode:** every Owl dialog / popover rendered as a white island — Bootstrap
  declares `--modal-bg`/`--popover-bg` ON `.modal`/`.popover` (compiled light),
  shadowing the `:root` dark overrides. Now set on the element + content/input/
  close-glyph recolor + deeper scrim. (the "config tab unreadable in dark" report)
- **Corner knob** now reaches the whole control family (`.btn-secondary`, inputs,
  dropdowns were frozen at 0px compiled literals) via `--nile-control-radius` with
  RTL-safe btn-group seam handling.
- **Configurator polish:** equal-width segmented controls (no more text-ragged
  "cheap" look), real tab `:hover`, active tab via `--nile-color-link` (readable in
  dark), Google-Fonts inputs forced `dir=ltr`.
- **Kanban accent-strip** now visible in dark (new `--nile-color-accent-strip`
  token, lightened in the dark bundle).
- Removed `web_responsive`'s stray `AppMenuTheme` systray (unbranded water-drop +
  caret). Dropped the obsolete `+`-cross raster logo lockups (SVGs are canonical).
- Verified live on `erpmedsupply`: EN+AR critical-flow tours PASS (ltr/rtl,
  Alexandria); corner-knob probe 6/1/8px; dark dialog + LTR font input by screenshot.

## odoo-nile-theme `v18.0.2.1.0` (2026-06-14) — tag `377680c`

**Quiet-Elevation depth system + 6 customization knobs + rod-of-Asclepius logo.**
Adds schema (new `res.company`/`res.users` Selection fields) → **not asset-only**.

- **Deploy:** `-u nile_theme,nile_brand_medsupply --i18n-overwrite`, then
  **restart** the Odoo server. The `--i18n-overwrite` is REQUIRED to import the
  new Arabic strings on an existing DB (plain `-u` skips them). The restart is
  REQUIRED so the new `ir.http.session_info` keys (corner/card/accent/input/
  sticky + `navbar_logo_url`) and the per-process UI-translation cache reload.
  A brand-pack migration (`nile_brand_medsupply/migrations/18.0.1.1.0/`) repoints
  the favicon ICP `.png → .svg` (its record shipped under `noupdate="1"`, so `-u`
  alone won't move it).
- **New:** elevation/depth tokens (light + dark, dark = 1px ring + inner
  highlight), shared `--nile-card-*` recipe, kanban D1 (dark column/header
  corners) + D2 (accent strip 3px→2px inset) fixes, recessed light inputs; a
  **Style** tab (corner-style / card-style / kanban accent-strip — company) +
  Input-Style / Sticky-List-Header / deepened density (per-user); rod-of-
  Asclepius SVG navbar/primary logos + pill favicon, served via
  `nile.navbar_logo_url` (no manual upload needed; a per-company
  `nile_menubar_logo` Binary still overrides).
- **RTL:** the HSV color picker is now physical end-to-end (position +
  centering), so it cannot mirror in Arabic.
- Verified on `erpmedsupply_nile`: assets compiled, WCAG gate `0 failed`, light +
  dark + EN + AR screenshots, adversarial review (8 low/nit findings fixed).

## odoo-nile-theme `v18.0.2.0.0` (2026-06-14) — tag `8d09cf5`

**Single-module consolidation + RTL color-picker fix.** Structural change, so the
deploy is **not** asset-only.

- The four theme modules (`nile_core` → `nile_components` → `nile_shell` →
  `nile_config`) were folded into one addon **`nile_theme`** (history preserved
  via `git mv`; asset-injection order preserved as one flattened list). Brand
  packs (`nile_brand_*`) now `depend` on `nile_theme` and prepend before
  `nile_theme/static/src/scss/primary_variables.scss`. **Install is now 2 modules
  for the ERP: `nile_theme,nile_brand_medsupply`.**
- Fixed: the HSV color picker (Brand custom color + App-Menu Background) was
  **mirrored in Arabic/RTL** — `rtlcss` flipped its `linear-gradient(to right…)`
  to `to left` in the RTL bundle while the click math stayed physical-left, so a
  pick on the left applied the color from the right. The two gradients now carry
  `/*rtl:ignore*/`. Verified in the real compiled `.rtl` backend bundle.
- **Deploy note (clean break — chosen strategy):** on an existing DB, update the
  module list, **uninstall** `nile_core,nile_components,nile_shell,nile_config`,
  then install `nile_theme` (`-i nile_theme,nile_brand_medsupply`). Company/user
  theme prefs (palette/font/density/dark) reset to defaults and are re-picked in
  the Theme dialog. Fresh installs just install the two modules. Verified: clean
  install of `nile_theme,nile_brand_ephem` on an empty DB — 28 modules loaded,
  WCAG gate `0 failed`.

## odoo-nile-theme `v18.0.1.2.1` (2026-06-14)

Asset-only bug-fix over `v18.0.1.2.0` (no schema change → deploy recreate just
recompiles assets). The top-menu (navbar) **bottom border/stroke** now follows
the company palette — it was core's compiled `$o-navbar-border-bottom` (a fixed
darkened teal) and stayed teal under every other palette. Tied to the
darkened-brand token; dark mode unaffected (retinted to `--nile-color-border`).

## odoo-nile-theme `v18.0.1.2.0` (2026-06-14)

Feature release (only `nile_config` changed → only it gets `-u` on deploy; a new
`res.company` column is added, so the upgrade is **not** asset-only).

- **App-launcher (9-dots) background is now palette-following + customizable.**
  New `res.company.nile_appmenu_bg` (hex). The drawer was web_responsive's
  compiled brand (ignoring the runtime palette); it now follows the Nile palette
  by default and admins can override the base hue from the Theme dialog
  (Brand tab → "App Menu Background": Follow palette / Custom).
- Fixed the Google-Fonts help text never rendering in Arabic (inline `<b>`
  + wording drift made it miss its `.po` msgid).
- Deploy note: the recreate must run `-u nile_config` (new DB column), not just
  an asset recompile. Verified live (EN+AR, light+dark) via
  `scripts/qa_test_appmenu_bg.py` (9/9, incl. dark-mode regression).

## odoo-nile-theme `v18.0.1.1.1` (2026-06-14)

Bug-fix pass over `v18.0.1.1.0` (no schema change beyond the existing fields;
asset-only recompile on deploy). All five user-reported, root-caused:

- Language switch flips LTR↔RTL on the **first** reload (session context
  refreshed before reload).
- Navbar menu-section toggles (submenus) follow the company palette (base
  `--NavBar-entry-backgroundColor` tied to the runtime navbar bg).
- Discuss app is dark (sidebar/header/thread/channel rows retied to dark tokens).
- Black kanban counters + grayscale `.text-*` utilities readable in dark.
- Custom-Font (Google-Fonts) upload moved Brand → Typography tab.

## odoo-nile-theme `v18.0.1.1.0` (2026-06-13)

- Phase 3 real dark skin + WCAG contrast gate + a11y focus pass.
- UI refinement: palette-follow extended (statusbar / settings rail / view
  switcher / notebook follow the company color), grouped-kanban count chip fix,
  stronger elevation + focus ring.
- Comprehensive theme panel: tabbed dialog, inline HSV color picker, company
  Google-Fonts link, systray globe language switcher.
- Hoot JS unit-test scaffold + CI lane.
- Ship only 5 of the 7 modules for the ERP: `nile_core`, `nile_shell`,
  `nile_components`, `nile_config`, `nile_brand_medsupply`.

## erpmedsupply-addons `v18.0.1.0.0`

- The 14 addons the ERP installs (11 OCA/OdooMates accounting + `web_responsive`
  + `web_chatter_position` + `ui_kanban_first`). Dependency closure verified
  against core Odoo + the 14 + `nile_*`.

## Bumping a pin

1. Land + tag the change in the addon/theme repo (`vMAJOR.MINOR.PATCH`).
2. Update the table above (tag + commit) and the matching row in
   [`PRODUCTION_HARDENING_RUNBOOK.md`](PRODUCTION_HARDENING_RUNBOOK.md) §5.
3. On the server: `git fetch --tags && git checkout <new tag>` in each clone,
   then `docker compose up -d` (recreate to pick up new assets).
