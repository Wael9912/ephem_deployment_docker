# Deployment pins

Single source of truth for the **pinned versions** a production deployment of the
Sudan medical-supply ERP runs. Production clones each repo at its pinned **tag**
(a detached, reproducible checkout) — never a moving branch. Bump this file on
every release, then re-tag the repos to match.

| Repo | Pinned tag | Commit | Role |
|---|---|---|---|
| [`Wael9912/ephem_deployment_docker`](https://github.com/Wael9912/ephem_deployment_docker) | `nile-theme` branch | — | deployment (compose, configs, scripts, docs) |
| [`Wael9912/erpmedsupply-addons`](https://github.com/Wael9912/erpmedsupply-addons) | `v18.0.1.0.0` | `0a5b028` | the 14 ERP addons → `/mnt/extra-addons` |
| [`Wael9912/odoo-nile-theme`](https://github.com/Wael9912/odoo-nile-theme) | `v18.0.1.1.1` | `ffb4b55` | the `nile_*` theme stack → `/mnt/nile-theme` |

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
