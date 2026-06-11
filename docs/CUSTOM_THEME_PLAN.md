# Custom Backend Theme Master Plan — Replacing Spiffy (OPL-1) with an In-House LGPL-3 Theme

**Status:** Phase 0 complete (2026-06-12) | **Date:** 2026-06-11 | **Targets:** Odoo 18.0 Community | **Products:** Sudan Medical-Supply ERP demo (`erpmedsupply`, Arabic-first EN/AR), CMP, ePHEM

> **Phase 0 decisions (ratified 2026-06-12, spike evidence in [theme-audit/phase0-spike/](theme-audit/phase0-spike/README.md)):**
> shell base = OCA `web_responsive` (one 2-line xpath patch for Odoo 18.0-20260324, candidate upstream PR);
> default chatter position = **bottom** (per-user switchable via `web_chatter_position`);
> naming `nile_` ratified. Scaffold repo: `~/Documents/odoo-nile-theme` (branch `18.0`).
> Plan-§6 correction from the spike: Odoo 18 RTL bundles carry a `.rtl.` filename suffix, not a `/rtl/` URL path — QA assertions must match either.

---

## 1. Vision

One small, legally clean, in-house design system that skins every product we ship — demo-grade polished, RTL-flawless, brandable per product in ~50 lines of SCSS, and free of the three Spiffy problems: OPL-1 lock-in (cannot fork/modify), `auth='public'` data-mutating endpoints, and UI inflexibility. We do **not** rebuild Spiffy. We rebuild the ~20% of Spiffy our users actually see (shell branding, app launcher, polished forms/lists/kanban, login page, RTL) on top of core Odoo 18 + a curated LGPL-3 open-source base, and we deliberately drop the other 80% (multi-tab, PWA/Firebase, 19 palettes, 4-variant widget styles, to-do notes) that adds maintenance burden without demo or customer value.

The existing `medsupply_ui_refresh` overlay (design tokens `--msr-*`, card forms, kanban headers/lanes, list polish) is the proof the CSS-first approach works; its code is ours (LGPL-3, clean) and gets absorbed wholesale into the new component layer. The existing `ui_kanban_first` addon (kanban as default first view) stays a separate generic addon.

### 1.1 Naming proposal

| Option | Prefix | Rationale | Concern |
|---|---|---|---|
| **Nile** (recommended) | `nile_` | Short, memorable, regionally meaningful across Sudan ERP and African public-health deployments, product-neutral, zero trademark noise in the Odoo app ecosystem | None significant |
| Acacia | `acacia_` | Regional, calm brand image | Longer prefix; collides conceptually with several design tools named Acacia |
| DS (Design System) | `ds_` | Maximally generic | Too anonymous for an app-store-publishable LGPL suite; `ds_` is a common prefix collision risk |

**Recommendation: `nile_`** — addons `nile_core`, `nile_components`, `nile_shell`, `nile_config`, `nile_brand_medsupply`, `nile_brand_cmp`, `nile_brand_ephem`. CSS token prefix `--nile-*` (mechanical rename of `--msr-*`). Repo: `odoo-nile-theme`, branch `18.0`, manifest versions `18.0.x.y.z`, license LGPL-3 on every addon, author set explicitly.

---

## 2. Strategy decision: full-custom vs OCA-composition vs hybrid

**Panel positions:**

- **Odoo frontend architect:** Full-custom shell (navbar, app drawer, responsive behavior) is the highest-churn JS surface across Odoo minor releases — exactly what OCA `web_responsive` (LGPL-3, **Production/Stable**, ported same-quarter every release since v11) already maintains for us. Rebuilding it is vanity engineering. Conversely, pure OCA composition gives no design identity: tokens, typography, card forms, kanban polish, login pages are *ours* and must be custom.
- **Security engineer:** Anything we adopt must be auditable and removable. OCA governance (many maintainers, public review) beats single-vendor MuK for the *base* dependency; MuK is fine for leaf modules we could drop or rewrite in a day. Hard rule: **no `depends` on AGPL-3 modules from our LGPL addons** (license contamination + network-clause obligations on ePHEM public-health instances). AGPL modules may not even be installed standalone without sign-off.
- **Product designer:** The manual/deck already teach users a "9-dot launcher + searchable app grid" mental model. `web_responsive`'s fullscreen searchable drawer matches that model with minimal re-documentation; MuK's sidebar (`muk_web_appsbar`) would change the documented chrome more.
- **RTL/i18n specialist:** `web_responsive` is RTL-tested upstream by a large Arabic-market user base; a custom shell means we own every RTL flip bug ourselves.
- **PM/QA:** Full-custom parity was estimated at 4–6 weeks for *one* developer just to reach parity — before QA, docs re-capture, and three products. Hybrid cuts Phase 1 to ~2 weeks including doc re-capture.

**Decision (unanimous): HYBRID.**

1. **Adopt (LGPL-3 only):** OCA `web_responsive` as the shell base (app drawer, search, sticky headers, mobile, hotkeys, docked document viewer); OCA `web_chatter_position` (per-user chatter side/bottom); OCA `web_notify` and `web_remember_tree_column_width` as optional QoL; MuK `muk_web_dialog` only if dialog-expand proves needed (leaf, LGPL, replaceable).
2. **Build (in-house, clean-room, LGPL-3):** token core, component skin (absorbing `medsupply_ui_refresh`), shell branding (logo/tab-title/favicon/login), configurator with runtime palette switching, dark-mode toggle reusing core `web.assets_web_dark`, brand packs.
3. **Drop:** everything in the parity matrix marked DROP — decisively, with the option to add back later as small LGPL leaf addons if a customer pays for it.
4. **Explicitly NOT adopted:** `muk_web_theme` as base (don't stack two shell reshapers; single-vendor base risk), all AGPL-3 modules (`web_dark_mode`, `web_dialog_size`, `web_company_color`, `web_favicon`, `web_refresher`, `web_save_discard_button`) — each has a trivial LGPL build-equivalent.

---

## 3. Addon architecture

### 3.1 Layer diagram

```
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 4 — Brand packs (per product, ~50 lines SCSS + images)     │
│  nile_brand_medsupply │ nile_brand_cmp │ nile_brand_ephem        │
│  palette map, logo, login imagery, favicon, tab-title default    │
│  (SCSS prepended BEFORE nile_core so !default tokens lose)       │
├──────────────────────────────────────────────────────────────────┤
│ LAYER 3 — Shell & configurator                                   │
│  nile_shell : navbar logo/branding, login template, favicon,     │
│               tab title; depends web_responsive (OCA, LGPL-3)    │
│  nile_config: res.config.settings + res.users prefs; runtime     │
│               palette injection; dark/density/chatter toggles    │
├──────────────────────────────────────────────────────────────────┤
│ LAYER 2 — Component skin                                         │
│  nile_components : card forms, list polish, kanban headers/      │
│  lanes, statusbar, control panel, dialogs, RTL fixes             │
│  (absorbs medsupply_ui_refresh 00–40 SCSS, renamed --nile-*)     │
├──────────────────────────────────────────────────────────────────┤
│ LAYER 1 — Design tokens                                          │
│  nile_core : SCSS !default vars in web._assets_primary_variables │
│  + :root CSS custom properties (--nile-*) + self-hosted fonts    │
│  + *.variables.dark.scss + density/motion tokens. NO CSS rules,  │
│  NO JS, NO models.                                               │
├──────────────────────────────────────────────────────────────────┤
│ ADOPTED OSS (LGPL-3): web_responsive, web_chatter_position,      │
│  (opt.) web_notify, web_remember_tree_column_width,              │
│  (opt.) muk_web_dialog                                           │
├──────────────────────────────────────────────────────────────────┤
│ Odoo 18 Community core: Ctrl+K command palette, dark SCSS bundle │
│  (web.assets_web_dark), rtlcss RTL pipeline, company switcher    │
└──────────────────────────────────────────────────────────────────┘
Sibling (independent): ui_kanban_first (kanban default first view)
```

### 3.2 Addon responsibilities

| Addon | Depends | Contents | Models | JS |
|---|---|---|---|---|
| `nile_core` | `web` | tokens, fonts (WOFF2 self-hosted), dark variables, density/motion tokens | none | none |
| `nile_components` | `nile_core` | all component SCSS, one opinionated style per widget (tabs, checkboxes, separators, modals) | none | none |
| `nile_shell` | `nile_components`, `web_responsive` | navbar logo, login page template, favicon, tab title; ≤3 `t-inherit` xpaths, ≤2 `patch()` files (one per core component, individually deletable) | `res.company` fields: `nile_menubar_logo`, `nile_favicon`, `nile_tab_name`, `nile_login_background` | minimal |
| `nile_config` | `nile_shell` | settings page + user prefs + runtime palette | `res.company` palette fields; `res.users`: `nile_dark_mode`, `nile_density`, (chatter pref via `web_chatter_position`) | small |
| `nile_brand_*` | `nile_core` (+product apps for defaults) | prepended SCSS token overrides, images, data XML defaults | none | none |

**Where design tokens live:** exclusively in `nile_core` — SCSS `!default` assignments in `web._assets_primary_variables` for compile-time identity (Bootstrap-derived values, radii, type scale), mirrored as `:root { --nile-* }` custom properties in `web.assets_backend` for everything runtime-switchable. Components consume **only** `var(--nile-*)` or `$nile-*`; styling raw hexes in Layer 2+ fails code review.

### 3.3 Configurator design (anti-scope-creep by construction)

Two axes, deliberately small:

1. **Product identity (compile time, no UI):** the brand pack. Choosing a different look per product = installing a different brand pack. Never user-editable.
2. **Tenant/user preferences (runtime, no recompile):**
   - **Runtime palette switching:** `res.company` stores primary/accent/navbar hexes (defaulted by brand pack data XML). A QWeb inheritance on `web.layout` renders `<style>:root{--nile-primary: …}</style>` from `env.company`. Switching company or saving settings = instant restyle, **zero SCSS recompilation, zero ir.attachment generation, zero web_editor coupling**. (We accept the documented limitation: runtime vars cannot re-derive Bootstrap SCSS math; brand packs handle that at compile time. This is the safer of the three known mechanisms — the `web_company_color` attachment pattern and the MuK `web_editor.assets` rewrite are both more version-fragile and have documented uninstall/recompile outage modes.)
   - **User prefs:** dark mode (sets core `color_scheme` cookie + reload to `web.assets_web_dark` — the dark SCSS already ships in Community; we build only the user-menu toggle, ~1 file), density (`<html data-nile-density="compact">` driving CSS-var overrides), chatter position (delegated to `web_chatter_position`).
   - **Hard cap:** the settings page exposes ≤ 8 controls, ever. Curated presets (≤6 palettes) instead of Spiffy's 19+19+freeform. Anything more requires a new plan, not a new field.

### 3.4 Per-product brand packs

| Pack | Palette | Fonts | Login | Notes |
|---|---|---|---|---|
| `nile_brand_medsupply` | current `--msr-*` palette carried over 1:1 (demo continuity — screenshots change chrome, not color story) | Alexandria (AR+EN) | company name + warehouse imagery | first shipped, Phase 1 |
| `nile_brand_cmp` | CMP palette | same family | CMP branding | CMP is theme-agnostic today — lowest-risk rollout |
| `nile_brand_ephem` | ePHEM/EOC palette (seeded from `eoc_theme_backend` brand vars, which is our clean LGPL code) | same family | ePHEM branding | replaces and retires `eoc_theme_backend`; stub addons `ephem_theme_backend`/`ephem_theme_push` (no `__manifest__.py`, dead code) deleted in Phase 0 |

---

## 4. Design-system spec essentials

- **Token taxonomy:** `--nile-{color|space|radius|type|elevation|motion|density}-*`. Color split into `color-brand-{primary,accent}`, `color-surface-{0..3}`, `color-text-{primary,secondary,muted,inverse}`, `color-state-{success,warning,danger,info}` with light + dark values (dark via `*.variables.dark.scss` in `web.dark_mode_variables` from day one, even though the toggle ships Phase 3 — retrofitting dark into a tokenless system is 10× the cost).
- **Typography EN/AR:** **one family for both scripts — Alexandria** (SIL OFL, variable, 400/500/700 WOFF2, self-hosted in `nile_core/static/fonts/` — never CDN; ePHEM runs in low-connectivity health settings). It is already the deck/manual brand font, giving print/screen consistency. Fallback stack `"Segoe UI", Tahoma, "Noto Sans Arabic", sans-serif`, `font-display: swap`. Scale: 13px base (Odoo native), steps 11/13/15/18/24. Arabic adjustments scoped via `:lang(ar)`: `line-height` 1.7 (vs 1.5 EN), never letter-spacing on Arabic text. If Alexandria proves weak in dense tables during Phase 1 QA, the pre-approved alternate is IBM Plex Sans Arabic — same OFL/self-host rules.
- **Color & dark posture:** brand palettes must pass an SCSS compile-time contrast assertion (≥4.5:1 text-on-surface, WCAG 2.1 AA). Dark mode = core dark bundle + our dark token values; posture is "supported, off by default, demo'd in light".
- **Density:** comfortable default (~48px list rows), compact opt-in (~40px) via `data-nile-density` + token overrides, persisted on `res.users`. Touch targets stay ≥44px in comfortable.
- **Motion:** transitions 150–200ms ease-out, opacity/transform only, no layout-thrashing animations; global `prefers-reduced-motion: reduce` rule in `nile_core` collapsing durations to 1ms.
- **CSS discipline:** logical properties only (`margin-inline-start`, `inset-inline-end`, `text-align: start`) — enforced by stylelint in CI; the rare intentional physical CSS uses the bang form `/*!rtl:ignore*/` (plain comments are stripped by SCSS/minification before rtlcss runs). Classnames prefixed `nile_`; no IDs, no tag selectors, no SCSS wildcards in manifests.

---

## 5. Migration & rollout per product

**Coexistence rule:** Spiffy and Nile are never active in the same DB. Development happens on a **copy** of `erpmedsupply`; the live demo DB keeps Spiffy untouched until Phase 1 exit. `nile_*` must not reference any spiffy/`biz-` selector, so install order can't create coupling.

**ERP demo (first):**
1. Copy `erpmedsupply` → `erpmedsupply_nile`; install `nile_core/components/shell/brand_medsupply` + `web_responsive` + `web_chatter_position` + `ui_kanban_first`.
2. **Absorb `medsupply_ui_refresh`:** its five SCSS files (our LGPL code) move into `nile_components` with `--msr-*`→`--nile-*` rename; `kanban_group_by.xml` (default group_by on kanban boards) moves into `nile_brand_medsupply`. The old addon is then deprecated — never installed alongside `nile_components` (duplicate rules).
3. Switchover (one maintenance window): uninstall `medsupply_ui_refresh`, then `spiffy_theme_backend`; install Nile stack; **regenerate assets** (RTL bundles); run uninstall-residue check (spiffy models, menus, `ir.ui.menu` columns) and the public-endpoint scan (§7).
4. Docs blast radius (budgeted, not hoped away): update `capture_screens.py` (navbar wait selector + app-launcher opener for `web_responsive` chrome), re-capture all EN+AR screenshots, re-edit manual `intro.json` + `interface.json` (remove "Spiffy" terminology — describe *our* chrome), rebuild manual + both decks via existing pipelines, update `erp-medsupply-demo` and `manual-deck-builder` SKILL.md install/verify steps.
5. Delete the `spiffy_theme_backend` directory (171 MB) from the addons tree once no DB references it. (Per the prod-readiness review, also remember it sits in git history — that scrub is tracked there.)

**CMP (second):** theme-agnostic today (zero spiffy references). Install Nile stack + `nile_brand_cmp` on a CMP staging DB, run the brand QA matrix, ship. Smallest rollout.

**ePHEM (third):** delete stub addons; replace `eoc_theme_backend` (its 3-line brand vars seed `nile_brand_ephem`); validate against the eoc dashboards and per-country modules; this is also where the prod-readiness "public eoc endpoints" concern gets the same endpoint-scan treatment.

---

## 6. QA strategy

- **Visual regression:** extend the existing Playwright `capture_screens.py` pipeline into a baseline-diff harness (Playwright screenshot + pixelmatch, ~2% threshold). Screens: login, app launcher, SO list, SO form (chatter both positions), product kanban, inventory list, settings. **Matrix per run: {EN-LTR, AR-RTL} × {light, dark*} × {comfortable, compact*} × {brand pack}** (*from the phase where the feature ships). Baselines refreshed only via reviewed PR.
- **RTL matrix:** AR runs assert (a) the served bundle URL contains `/rtl/` AND content is actually flipped (the classic missing-`rtlcss`-binary failure serves unflipped CSS at an `/rtl/` URL — rtlcss is baked into dev/CI/prod images and "regenerate assets" is a deploy-runbook step), (b) drawer, chatter, breadcrumbs, kanban lanes mirror correctly, (c) Alexandria renders for `:lang(ar)`.
- **Tour tests:** one `HttpCase.start_tour` per brand pack — login → launcher → open list → open form → save — run in EN and AR. Hoot unit tests (`web.assets_unit_tests`) for `nile_config` JS (palette injection, dark toggle, density attribute).
- **CI per push:** stylelint (logical-properties rule) + pylint-odoo; install matrix `-i nile_…,brand_X --stop-after-init` for all three brands (catches bundle-compile failures — the classic theme outage mode); tours EN+AR; **uninstall test for every addon** (themes are notorious for bricking on uninstall); screenshot artifacts.
- **Demo-day gate:** no theme changes merged within 48h of a scheduled customer demo; demo runs from a tagged release, never from `18.0` HEAD.

## 7. Security wins

- Uninstalling Spiffy removes **~30 `auth='public'`/`auth='none'` data-mutating JSON endpoints** (`/color/pallet/`, `/update-user-fav-apps`, `/active/dark/mode`, `/theme_color/parameter_check` Firebase registration, font upload routes, etc.) — directly closing a blocker in the prod-readiness review.
- **Verification, not assumption:** a `scripts/check_public_endpoints.py` smoke hits the full inventoried Spiffy route list post-uninstall expecting 404, plus enumerates remaining `auth='public'` routes DB-wide (also covers the eoc endpoints concern). Run in CI and in the deploy runbook.
- **New-code policy:** Nile ships **zero custom HTTP controllers** in Phases 0–2 (settings via standard ORM/`res.config.settings`; user prefs via `res.users` writes covered by core access rules). Any future controller requires `auth='user'` + security review sign-off. No Firebase keys, no service workers, no file-upload routes.
- Removes 171 MB of unauditable third-party JS (bundled Firebase SDK, jQuery UI) from the attack surface.

## 8. Team & process — clean-room rules

- **Tainted vs clean roles.** Anyone who has read Spiffy source (the engineer who produced the inventory) is *tainted*: they may write specs, the parity matrix, tests, and acceptance criteria, and may review *behavior* — they may **not** author any `nile_*` SCSS/JS/XML. The implementer(s) work from screenshots, this plan, and the parity matrix only; the `spiffy_theme_backend` directory is removed from the implementer's checkout (enforced via a worktree excluding it).
- **Never copy:** no Spiffy SCSS/JS/XML/image/icon may be opened, copied, or visually pixel-cloned (no proprietary artwork reproduction). Recreating *functionality and a similar general look* from screenshots is lawful (idea/expression dichotomy); copying *material* violates OPL-1.
- **Review gates (every PR):** (1) automated grep for `spiffy|biz-|bizople` in code and assets — any hit blocks merge; (2) license header + manifest `license: LGPL-3` check; (3) AGPL-dependency check on `depends`; (4) tainted reviewer confirms no structural resemblance beyond function; (5) the standing per-component "core touchpoint inventory" file is updated for every new `t-inherit`/`patch()`.
- **Bus factor:** every Nile addon gets a README with architecture notes; the tainted engineer pair-reviews all shell JS so ≥2 people understand each layer; docs pipeline knowledge already lives in the two SKILL.md files — keep them current as part of phase exit criteria.

## 9. Phased roadmap

| Phase | Scope | Effort (person-days) | Exit criteria |
|---|---|---|---|
| **0 — Foundations** | Repo `odoo-nile-theme` scaffold + CI skeleton; clean-room protocol signed; AGPL policy doc; delete `ephem_theme_backend`/`ephem_theme_push` stubs; spike: `web_responsive` + `web_chatter_position` on a copy of `erpmedsupply` in EN+AR (validates shell choice & RTL before we build on it); rtlcss confirmed in all images | **4 pd** | Spike DB screenshots approved by designer in both languages; CI runs install+lint on empty addons; naming `nile_` ratified |
| **1 — Spiffy-free ERP demo** | `nile_core` (tokens, fonts, dark variables file), `nile_components` (absorb medsupply_ui_refresh, one opinionated style per widget, login page), `nile_shell` (logo/favicon/tab-title/login on `web_responsive`), `nile_brand_medsupply`; switchover on demo DB; endpoint scan; full EN+AR re-capture; manual `intro`/`interface` rewrite; both decks rebuilt; SKILL.md updates | **10 pd** (6 build, 4 docs/QA) | **`erpmedsupply` runs with Spiffy and `medsupply_ui_refresh` uninstalled and looks demo-grade, not broken**, in EN and AR; visual-regression baselines recorded; all inventoried Spiffy public endpoints return 404; manual + decks rebuilt and proofed; Spiffy dir removable |
| **2 — Configurator + multi-product** | `nile_config` (runtime palette via `:root` injection, ≤6 presets, density modes, ≤8 controls hard cap), `nile_brand_cmp` + CMP rollout, `nile_brand_ephem` + ePHEM staging rollout, retire `eoc_theme_backend` | **9 pd** | Palette switch is instant (no recompile) and company-scoped; CMP + ePHEM staging pass tour/visual matrix; uninstall tests green for all addons |
| **3 — Dark mode + a11y polish** | Dark toggle in user menu (core `web.assets_web_dark` + `color_scheme` cookie), dark token pass on all components, contrast audit (4.5:1 assertions), focus-visible pass, reduced-motion rule, compact density QA | **7 pd** | Dark × RTL × both densities pass the visual matrix on all three brands; WCAG AA contrast assertions in CI |
| **4 — Hardening & distribution** | Hoot unit tests, tour matrix EN/AR per brand in CI, uninstall-test automation, git-submodule consumption wiring for the three deployments, version tagging, core-touchpoint inventory finalized, 19.0-readiness notes, maintainer README per addon | **6 pd** | All deployments consume pinned submodule tags; CI fully green incl. uninstall + RTL bundle check; a second engineer has merged a change to every layer |

**Total: ~36 person-days.** Phase 1 is the only hard-deadline-sensitive phase; phases 2–4 can interleave with product work.

---

# Appendix A — Spiffy Feature Parity Matrix

| # | Spiffy feature | Spiffy behavior | Decision | Replacement notes | Effort | Phase |
|---|---|---|---|---|---|---|
| 1 | Color palettes (19) | Predefined schemes via SCSS+JS injection | BUILD (reduced) | ≤6 curated presets in `nile_config`, runtime `:root` CSS-var injection; 19 is choice-overload, not value | S | 2 |
| 2 | Custom color override | User picks hex for primary/secondary/dark | BUILD | Company-level palette fields (brand-pack defaults) in `nile_config`; per-user freeform dropped deliberately | S | 2 |
| 3 | Drawer color palettes (19) + custom drawer colors | Separate drawer color scheme | DROP | One coherent palette per brand; separate drawer theming is incoherent design | — | — |
| 4 | Dark mode | Toggle + dark SCSS | CORE-ALREADY + BUILD | Community ships full `web.assets_web_dark` bundle; build only the user-menu toggle setting `color_scheme` cookie (avoid AGPL `web_dark_mode`); our dark token values in `nile_core` | S | 3 |
| 5 | Menu position (horizontal/vertical/mini ×2) | 4 layout modes | DROP + ADOPT-OCA(web_responsive) | One opinionated layout: standard navbar + fullscreen drawer. Four layouts = 4× QA matrix for zero demo value | — | 1 |
| 6 | App drawer (grid, search, favorites drag-drop) | OWL slide-out app grid | ADOPT-OCA(web_responsive) | LGPL-3, Production/Stable; fullscreen searchable drawer matches the manual's "9-dot launcher" mental model. Favorites drag-drop dropped (search is faster) | S (integrate) | 1 |
| 7 | Favorite apps (`favorite.apps`) | Pinned apps in drawer | DROP | Drawer auto-focus search + Ctrl+K palette cover it; was backed by an auth=public route | — | — |
| 8 | App grouping (`spiffy.app.group`) | Organize top menus into icon groups | DROP | Menu sequence + drawer search suffice at our app count; revisit only if an app-heavy customer asks | — | — |
| 9 | Menu icons (image/FA class on ir.ui.menu) | Custom icons per menu | DROP | Core app icons shown by web_responsive; per-submenu icons are clutter in data-dense backends | — | — |
| 10 | Global app search | Search modal over apps | CORE-ALREADY | Ctrl+K command palette (core since v15) + drawer search | — | 1 |
| 11 | Global record search (`global.search.bizople`) | Configurable cross-model record search | DROP (backlog) | Ctrl+K covers menus/users/channels; a record-namespace palette extension is a small future LGPL build if demanded | — | — |
| 12 | Bookmarks sidebar (`bookmark.link`) | Right panel of saved links | DROP | Browser bookmarks + core favorite filters + Ctrl+K cover it; was 4 auth=public CRUD routes; never featured in demos | — | — |
| 13 | Multi-tab system (`biz.multi.tab`) | Open forms in tab bar | DROP | Browser tabs do this natively; OWL-fragile across upgrades; auth=public CRUD routes | — | — |
| 14 | Split tree-form view | List left + form right, resize/scroll-sync | DROP | L-effort, most upgrade-fragile Spiffy component; core list→form breadcrumb flow is the documented UX; not in manual/deck | — | — |
| 15 | Document viewer modal | PDF/image preview modal | ADOPT-OCA(web_responsive) | web_responsive docks the document viewer beside chatter with maximize toggle | — | 1 |
| 16 | To-Do/Notes (`todo.list`, 7 palettes) | Personal notes panel | DROP | Odoo Activities/Notes apps exist; auth=public CRUD routes; zero demo value | — | — |
| 17 | Chatter position (right/bottom) | Per-user chatter layout | ADOPT-OCA(web_chatter_position) | LGPL-3, per-user side/bottom preference, full-width sheet | S | 2 |
| 18 | Form input styles (3 variants) | Borderless/bottom/bordered | BUILD (one style) | Single opinionated card-form input style in `nile_components` (extends current `10_form.scss`); variants dropped | S | 1 |
| 19 | List density (comfortable/compact) | Row-spacing toggle | BUILD | `data-nile-density` attribute + density tokens, persisted on res.users; comfortable default, compact opt-in | S | 2 |
| 20 | List sticky header | Pinned header on scroll | ADOPT-OCA(web_responsive) | Ships sticky list headers/footers + sticky form statusbar | — | 1 |
| 21 | Tab styles (4) | Tab widget variants | BUILD (one) | One token-styled tab design in `nile_components`; variants dropped | S | 1 |
| 22 | Checkbox styles (4) | Checkbox variants | BUILD (one) | One accessible token-styled checkbox; variants dropped | S | 1 |
| 23 | Radio styles (4) | Radio variants | BUILD (one) | Same | S | 1 |
| 24 | Popup/modal styles (4) | Dialog variants | BUILD (one) | One token-styled modal in `nile_components`; optional `muk_web_dialog` (LGPL) later for expand button | S | 1 |
| 25 | Separator styles (4) | Form divider variants | BUILD (one) | One separator style | S | 1 |
| 26 | Theme corners (rounded/standard/square) | Global border-radius switch | BUILD (token, fixed) | `--nile-radius-*` tokens set per brand pack; not user-switchable | S | 1 |
| 27 | Menu shapes (rounded/circle/square) | Menu button shapes | DROP | Cosmetic churn; one designed shape via tokens | — | — |
| 28 | Loader styles (10 spinners) | Spinner animation variants | DROP | Core spinner, restyled via tokens if desired; 10 spinners is pure bloat | — | — |
| 29 | Font size (S/M/L) | Global font scaling | DROP | Browser zoom + density modes cover it; global font scaling breaks dense layouts unpredictably | — | — |
| 30 | Google Fonts library (max 5/user, `google.font.family`) | Per-user web fonts from CDN | DROP | Self-hosted brand fonts only (offline-safe for ePHEM, no CDN/privacy leak); per-user fonts destroy brand consistency; had auth='none' add/delete routes | — | — |
| 31 | Login page styles (4 presets) | Template variants + bg image/color | BUILD (one branded) | One designed login template in `nile_shell`, imagery/colors from brand pack + company fields | S | 1 |
| 32 | Browser tab title | Company `tab_name` field | BUILD | `nile_tab_name` on res.company, default per brand pack | S | 1 |
| 33 | Favicon | Company favicon binary | BUILD | Trivial company field + layout inherit (avoid AGPL `web_favicon`) | S | 1 |
| 34 | Menubar logo (+icon variant) | Company logo in navbar | BUILD | `nile_menubar_logo` + small navbar `t-inherit` in `nile_shell` | S | 1 |
| 35 | PWA (manifest, service worker, install) | Installable app + offline cache | DROP (backlog) | No product requirement; large attack/maintenance surface (public service-worker + manifest routes). Revisit as separate addon only with a funded mobile requirement | — | — |
| 36 | PWA shortcuts (`pwa.shortcuts`) | Home-screen quick actions | DROP | Falls with PWA | — | — |
| 37 | PWA offline page | Cache-miss fallback | DROP | Falls with PWA | — | — |
| 38 | Firebase push (`mail.firebase`, server keys) | Device token registration | DROP | Out of scope; was partially commented-out even in Spiffy; removes auth='none' registration route + stored Firebase server keys (security win) | — | — |
| 39 | Push notification routing (`push.notification.menu`) | Model-event push rules | DROP | Falls with Firebase; `web_notify` (LGPL) covers in-app server toasts if needed | — | — |
| 40 | Auto-save prevention | Company flag forcing manual save | DROP | Odoo 18 save/discard UX is acceptable and demo'd as-is; AGPL `web_save_discard_button` exists if a customer insists (standalone install, never a dep) | — | — |
| 41 | Filter row visibility toggle | Show/hide list filter row | DROP | Core search panel/facets suffice; niche toggle | — | — |
| 42 | Tree-view attachments badge | File count in lists | DROP | Niche; chatter shows attachments on the record | — | — |
| 43 | List rendering polish (row height, checkboxes) | Renderer patches + SCSS | BUILD | Pure-CSS list polish already exists in `20_list.scss` → `nile_components`; bigger checkboxes come with web_responsive | S | 1 |
| 44 | Form statusbar styling | Header button styling | BUILD | Token-based statusbar/button styling in `nile_components` (sticky behavior from web_responsive) | S | 1 |
| 45 | Kanban styling | Card/header styling | BUILD | Carry over `30_kanban.scss` (headers/lanes) into `nile_components`; `ui_kanban_first` stays separate | S | 1 |
| 46 | Responsive/mobile design | Breakpoints, hamburger, touch | ADOPT-OCA(web_responsive) | Its core competency; maintained upstream | — | 1 |
| 47 | RTL support | flip JS + responsive SCSS | CORE-ALREADY + BUILD discipline | Core rtlcss `/rtl/` bundles do the flipping; we contribute logical-properties discipline + carried-over `40_rtl.scss` fixes + AR font scoping | M | 1 |
| 48 | Multi-language switcher | Lang routes in user menu | CORE-ALREADY | Core user preferences/lang switching; Spiffy's auth=public lang routes die with it | — | 1 |
| 49 | Report export w/ color preservation (PDF/xlsx routes) | Custom export controllers | DROP | Core PDF/xlsx export is sufficient; Spiffy's custom export/session-flag routes were part of the risky controller surface | — | — |
| 50 | Theme prefs persistence (`backend.config`) | Per-user ORM config | BUILD (simplified) | Few fields on res.users/res.company via `nile_config`; no separate config model, no public routes | S | 2 |
| 51 | Global vs user-level theming | Admin-wide vs per-user scope | BUILD (simplified) | Two fixed scopes by design: company = palette/branding, user = dark/density/chatter only. No scope-switch machinery | S | 2 |
| 52 | View refresh button (pager) | Reload view data | DROP | Niche; AGPL `web_refresher` exists if ever requested (standalone only) | — | — |
| 53 | Company switcher styling | Restyled multi-company menu | CORE-ALREADY | Core switcher; inherits token styling for free | — | 1 |
| 54 | Page title/breadcrumb patch | Dynamic tab titles | CORE-ALREADY | Core handles document titles; `nile_tab_name` covers the brand prefix | — | 1 |
| 55 | Icon pack loader | Async FA pack load | DROP | Core FontAwesome suffices | — | — |
| 56 | App drawer / vertical-menu background images | Uploadable bg imagery | DROP | Visual gimmick; hurts contrast/a11y; brand identity comes from tokens + login imagery | — | — |
| 57 | Sticky/pinned sidebar state | Per-user pin state | DROP | No persistent sidebar in our shell (drawer model) | — | — |
| 58 | Custom jQuery UI bundle | Legacy interactions | DROP | Dead weight; nothing of ours needs jQuery UI | — | — |

---

# Appendix B — Risk Register

# Risk Register

| # | Risk | Likelihood | Impact | Mitigation | Owner (role) |
|---|---|---|---|---|---|
| 1 | **License contamination** — Spiffy (OPL-1) expression leaking into Nile code (copied SCSS/JS/XML/assets), or an LGPL addon gaining an AGPL `depends` | Medium | Critical (legal exposure; forced relicense/rewrite; OPL-1 explicitly forbids copying material) | Clean-room split (tainted spec-writers vs clean implementers); spiffy dir excluded from implementer checkouts; CI grep gate for `spiffy|biz-|bizople`; CI AGPL-dependency check; never reuse Spiffy images/artwork; delete Spiffy from tree post-Phase 1 (git-history scrub tracked in prod-readiness plan) | Security engineer (gates) + PM (protocol) |
| 2 | **Odoo minor-upgrade breakage** — `t-inherit` xpaths and `patch()`es on navbar/web client break on 18.0 point releases or saas updates | High | Medium (UI breakage until patched) | JS-minimalism ladder (registries > t-inherit+hasclass > patch); ≤2 patch files, one per core component; core-touchpoint inventory file recording template hash per xpath; Hoot + tour CI on every Odoo image bump; pin Odoo image per deployment | Odoo frontend architect |
| 3 | **RTL regressions** — unflipped bundles (missing rtlcss binary), stripped `/*rtl:ignore*/` comments, physical CSS sneaking in | Medium | High (Arabic-first flagship demo looks broken to the primary audience) | rtlcss baked into all dev/CI/prod images; CI asserts `/rtl/` bundle content actually flipped; stylelint logical-properties rule; bang-form `/*!rtl:ignore*/` only; AR-RTL leg mandatory in visual-regression matrix; "regenerate assets" in deploy runbook | RTL/i18n specialist |
| 4 | **Demo-day regressions** — theme change lands right before a customer demo and breaks a screen or the deck/manual drifts from live UI | Medium | High (lost sale/credibility) | 48h merge freeze before demos; demos run tagged releases only; visual-regression baselines on the exact demo flows; manual/deck re-capture is an explicit Phase 1 exit criterion, not an afterthought; switchover on a copy DB first | QA lead + PM |
| 5 | **Configurator scope creep** — recreating Spiffy's 30+ options "because users had them" | High | Medium (maintenance explosion, QA matrix blow-up) | Hard cap: ≤8 controls, ≤6 palette presets, written into the plan; parity matrix DROP decisions are pre-litigated — re-adding any DROPped feature requires a new mini-plan with funding; designer owns "one opinionated style per widget" rule | Product designer + PM |
| 6 | **Single-maintainer bus factor** — one engineer holds all theme + docs-pipeline knowledge | Medium | High (project stalls; deployments unpatchable) | Per-addon READMEs; tainted engineer pair-reviews all shell JS; Phase 4 exit requires a second engineer to have merged changes in every layer; SKILL.md docs kept current as phase exit criteria; small total code surface by design (DROP-heavy strategy) | PM |
| 7 | **OCA module abandonment** — `web_responsive`/`web_chatter_position` not ported to 19.0 in time, or quality drops | Low–Medium | Medium (shell gap at next major upgrade) | Chose Production/Stable LGPL modules with multi-year port history and OCA (multi-maintainer) governance over single-vendor; LGPL license preserves fork-and-maintain right (unlike Spiffy); our layers depend on web_responsive only in `nile_shell` (thin); fallback documented: MuK appsbar or in-house minimal drawer (~5 pd) | Odoo frontend architect |
| 8 | **Theme uninstall/asset-pipeline bricking** — bad uninstall or bundle-compile failure leaves DB without working assets (known failure mode of theme addons) | Medium | High (downtime on demo/prod DBs) | Per-addon uninstall tests in CI; install matrix with `--stop-after-init` per brand; runtime palette via `:root` injection (no `web_editor.assets` rewriting, no generated-attachment SCSS); switchover rehearsed on DB copy with rollback snapshot | QA lead |
| 9 | **Docs re-capture underestimated** — bilingual manual (8 sections) + 2×15-slide decks lag the new UI, shipping screenshots of a dead theme | Medium | Medium (inconsistent customer-facing artifacts) | 4 pd explicitly budgeted inside Phase 1; capture pipeline updated before switchover; deck/manual rebuild is a Phase 1 exit criterion; existing manual-deck-builder skill encodes the rebuild procedure | PM + QA lead |
| 10 | **Dark-mode debt** — shipping Phase 1 without dark token values, making Phase 3 a rewrite | Medium | Medium | `nile_core` ships `*.variables.dark.scss` and dark token values from day one (Phase 1), even though the toggle arrives Phase 3 | Product designer |

---

*Companion document: [theme-audit/SPIFFY_AUDIT.md](theme-audit/SPIFFY_AUDIT.md) — full Spiffy inventory, dependency map, and the no-Spiffy uninstall experiment evidence.*
