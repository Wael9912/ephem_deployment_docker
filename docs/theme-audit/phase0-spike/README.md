# Phase 0 Spike — Shell Candidate Comparison (Nile theme program)

**Date:** 2026-06-12 · **DB:** `erpmedsupply_nile` (throwaway copy of `erpmedsupply`) · **Odoo:** 18.0-20260324 Community

Side-by-side UI samples for the [CUSTOM_THEME_PLAN.md](../../CUSTOM_THEME_PLAN.md) Phase 0 exit decision:
which chrome do we build the `nile_*` layers on?

| Variant | What it is | Addons active |
|---|---|---|
| `spiffy` | Current demo baseline (to be replaced) | spiffy_theme_backend + medsupply_ui_refresh |
| `core` | Plain Odoo 18 Community, no theme | (none — both uninstalled) |
| `responsive` | **Plan's recommendation** — OCA shell base | web_responsive + web_chatter_position (LGPL-3) |
| `responsive-chatter-bottom` | Same, chatter below the form sheet | per-user pref of web_chatter_position |

Screens per variant/lang: `login`, `apps_home` (app launcher open), `inventory_overview`,
`products_kanban`, `sale_orders_list`, `sale_order_form`, `settings_general`.

> Note: `core` and `responsive` show **unstyled stock purple** — Phase 1's `nile_core`/`nile_components`
> (tokens, Alexandria font, card forms, kanban polish, brand palette) layer on top of whichever
> shell is chosen. Judge the **chrome** (navbar, launcher, drawer, chatter, RTL), not the colors.

## App launcher

| | EN | AR |
|---|---|---|
| Spiffy | ![](img/spiffy/en/apps_home.png) | ![](img/spiffy/ar/apps_home.png) |
| Core | ![](img/core/en/apps_home.png) | ![](img/core/ar/apps_home.png) |
| web_responsive | ![](img/responsive/en/apps_home.png) | ![](img/responsive/ar/apps_home.png) |

## Sales order form (chatter)

| | EN | AR |
|---|---|---|
| Spiffy | ![](img/spiffy/en/sale_order_form.png) | ![](img/spiffy/ar/sale_order_form.png) |
| Core | ![](img/core/en/sale_order_form.png) | ![](img/core/ar/sale_order_form.png) |
| web_responsive (chatter sided) | ![](img/responsive/en/sale_order_form.png) | ![](img/responsive/ar/sale_order_form.png) |
| web_responsive (chatter bottom) | ![](img/responsive-chatter-bottom/en/sale_order_form.png) | — |

## Sales orders kanban

| | EN | AR |
|---|---|---|
| Spiffy | ![](img/spiffy/en/sale_orders_list.png) | ![](img/spiffy/ar/sale_orders_list.png) |
| Core | ![](img/core/en/sale_orders_list.png) | ![](img/core/ar/sale_orders_list.png) |
| web_responsive | ![](img/responsive/en/sale_orders_list.png) | ![](img/responsive/ar/sale_orders_list.png) |

## Products kanban

| | EN | AR |
|---|---|---|
| Spiffy | ![](img/spiffy/en/products_kanban.png) | ![](img/spiffy/ar/products_kanban.png) |
| Core | ![](img/core/en/products_kanban.png) | ![](img/core/ar/products_kanban.png) |
| web_responsive | ![](img/responsive/en/products_kanban.png) | ![](img/responsive/ar/products_kanban.png) |

## Inventory overview

| | EN | AR |
|---|---|---|
| Spiffy | ![](img/spiffy/en/inventory_overview.png) | ![](img/spiffy/ar/inventory_overview.png) |
| Core | ![](img/core/en/inventory_overview.png) | ![](img/core/ar/inventory_overview.png) |
| web_responsive | ![](img/responsive/en/inventory_overview.png) | ![](img/responsive/ar/inventory_overview.png) |

## Settings

| | EN | AR |
|---|---|---|
| Spiffy | ![](img/spiffy/en/settings_general.png) | ![](img/spiffy/ar/settings_general.png) |
| Core | ![](img/core/en/settings_general.png) | ![](img/core/ar/settings_general.png) |
| web_responsive | ![](img/responsive/en/settings_general.png) | ![](img/responsive/ar/settings_general.png) |

## Login

| | EN | AR |
|---|---|---|
| Spiffy | ![](img/spiffy/en/login.png) | ![](img/spiffy/ar/login.png) |
| Core | ![](img/core/en/login.png) | ![](img/core/ar/login.png) |
| web_responsive | ![](img/responsive/en/login.png) | ![](img/responsive/ar/login.png) |

## Spike findings

1. **RTL bundles verified**: AR sessions serve `web.assets_web.rtl.min.css` and the layout is
   actually mirrored on all three variants (navbar, kanban lanes, chatter side, breadcrumbs).
   Note: Odoo 18 marks RTL bundles with a `.rtl.` filename suffix, **not** a `/rtl/` URL path —
   the QA assertion in the plan (§6) should match either.
2. **rtlcss present** in the `ephem-cmp:dev` image (v4.3.0 at `/usr/local/bin/rtlcss`).
3. **One upstream incompatibility found and patched** (plan risk #2 materialized, cheap to fix):
   OCA `web_responsive` 18.0.1.0.6 xpaths `//t[@t-if='this.ui.isSmall']` in
   `web.NavBar.AppsMenu`, but Odoo 18.0-20260324 core renamed it to `env.isSmall` → OWL crash,
   blank web client. Patched locally in
   `custom-addons/web_responsive/static/src/components/apps_menu/apps_menu.xml` (2 lines,
   commented). Worth an upstream OCA issue/PR; must be re-checked on every Odoo image bump.
4. **Spiffy config is destroyed by uninstall**: reinstalling spiffy on the spike DB came back with
   factory defaults (teal vertical sidebar), not the demo's configured horizontal layout — its
   `backend.config` rows are dropped on uninstall. Confirms the plan's "rehearse switchover on a
   copy + rollback snapshot" rule: there is no cheap "reinstall spiffy" rollback on the live demo DB.
5. **Registry-cache gotcha for capture runs**: flipping the admin language via SQL is not seen by a
   running server (user-context ormcache) — restart Odoo (or flip via ORM) before capturing.
6. `web_chatter_position` works as advertised (auto/sided/bottom per user pref, full-width sheet
   when bottom).

## Reproduce

```bash
# capture: variant ∈ {spiffy|core|responsive}, lang ∈ {en|ar}
python3 scripts/spike_capture.py responsive ar
# admin lang must match; flip with:
#   UPDATE res_partner SET lang='ar_001' WHERE id=(SELECT partner_id FROM res_users WHERE login='admin');
# then: docker compose restart odoo
```
