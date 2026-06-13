export const meta = {
  name: 'nile-ui-audit',
  description: 'Audit the Nile Odoo backend theme for visual defects from real screenshots + code, design a comprehensive theme-config panel (clean-room), and emit one prioritized LOW-RISK implementation plan',
  phases: [
    { title: 'Audit', detail: 'fan-out: each agent owns a UI area, reads screenshots + SCSS, returns grounded findings' },
    { title: 'Design', detail: 'parallel design variants for the new theme-config panel' },
    { title: 'Synthesize', detail: 'merge findings + chosen design into one ordered low-risk plan' },
  ],
}

// args = { shotsDark, shotsAudit, code, darkLog }  (absolute paths)
const A = args || {}
const SHOTS_DARK = A.shotsDark || '/Users/waelabdalla/Documents/ephem-deploy/docs/theme-audit/qa/dark-sweep'
const SHOTS_AUDIT = A.shotsAudit || '/Users/waelabdalla/Documents/ephem-deploy/docs/theme-audit/qa/audit'
const CODE = A.code || '/Users/waelabdalla/Documents/odoo-nile-theme'
const DARK_LOG = A.darkLog || '/tmp/nile_dark_sweep.log'

const CONTEXT = `
You are auditing the **Nile** custom backend theme for Odoo 18 Community (a Sudan medical-supply ERP).
Ground truth lives in two places — you MUST look at BOTH for every claim:
  * Screenshots (use the Read tool on the .png files — it shows you the image):
    - Broad sweep, light+dark x EN+AR:  ${SHOTS_DARK}/{light,dark}/{en_US,ar_001}/*.png
      (inventory_overview, products_kanban, sale_orders_list, sale_order_form, invoices, settings, partners_kanban)
    - Targeted audit shots:  ${SHOTS_AUDIT}/*.png
      (theme_dialog, apps_menu, menu_section_open, user_menu_open, kanban_grouped_*,
       palette_base_* vs palette_blue_*  <- SAME screen at default 'teal' vs company palette switched to 'blue')
    - Automated dark-mode luminance findings: ${DARK_LOG}
  * Theme source code:  ${CODE}  (nile_core, nile_components, nile_shell, nile_config, nile_brand_*)

KEY ARCHITECTURE (so you don't rediscover it):
  * Design tokens are CSS custom props --nile-* defined in nile_core/static/src/scss/tokens.scss (light)
    and tokens.dark.scss (dark). SCSS palette source-of-truth + WCAG gate: nile_core/static/src/scss/contrast.scss.
  * Company palette + per-user prefs are injected at runtime as a <style> :root block
    (nile_config/models/res_users.py::_nile_runtime_css + views/webclient_templates.xml) — NO SCSS recompile.
  * The "re-point sheet" nile_config/static/src/scss/theme_runtime.scss re-declares a BOUNDED set of brand
    surfaces against var(--nile-color-brand-*): navbar (--nile-navbar-bg follows brand), .btn-primary,
    .btn-outline-primary, .btn-link, plain content links, .form-check-input:checked. ANY accent surface
    OUTSIDE this list keeps its COMPILED teal hex and will NOT follow a palette change — that is the prime
    suspect for "the color theme doesn't apply on the menu buttons". The palette_base vs palette_blue shots
    are the definitive test: anything still teal in the blue shot is an un-covered surface.
  * Theme configurator: nile_config/static/src/systray/theme_menu.{js,xml,scss} (paint-brush systray ->
    one Owl Dialog), theme_service.js (live preview + dark cookie sync).

HARD CONSTRAINTS for any fix you propose (the user said "without risky coding"):
  * LOW RISK only. Prefer SCSS/CSS token + re-point-sheet additions, Owl template/markup tweaks scoped to
    nile_*. Do NOT propose changes to Odoo core, broad !important wildcards, or anything touching JS that
    repositions popovers/dropdowns (a prior bug: a wildcard transition under prefers-reduced-motion sent ALL
    dropdowns to (0,0) — never propose wildcard transition/animation overrides).
  * Must NOT break: the WCAG AA contrast gate (contrast.scss + nile_core/tests/test_contrast.py), dark mode,
    or RTL/Arabic.
  * CLEAN-ROOM: never read or search for Spiffy theme source (spiffy_theme_backend) in any form, incl. git
    history. Design from first principles + Odoo-native patterns only.
`

const FINDINGS_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['area', 'findings'],
  properties: {
    area: { type: 'string' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['title', 'severity', 'evidence', 'where', 'rootCause', 'proposedFix', 'risk'],
        properties: {
          title: { type: 'string', description: 'one-line defect summary' },
          severity: { type: 'string', enum: ['high', 'medium', 'low'] },
          evidence: { type: 'string', description: 'screenshot filename(s) that show it + what to look at' },
          where: { type: 'string', description: 'file:line in the theme code (or "core, no nile rule yet")' },
          rootCause: { type: 'string' },
          proposedFix: { type: 'string', description: 'concrete LOW-RISK fix (target file + what to change)' },
          risk: { type: 'string', enum: ['low', 'medium', 'high'] },
        },
      },
    },
  },
}

const DESIGN_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['variant', 'summary', 'layout', 'controls', 'languageSwitcher', 'googleFonts', 'colorPicker', 'serverChanges', 'risks'],
  properties: {
    variant: { type: 'string' },
    summary: { type: 'string' },
    layout: { type: 'string', description: 'dialog structure: sections/tabs/preview pane, size, ascii sketch ok' },
    controls: { type: 'array', items: { type: 'string' }, description: 'every control + its widget + scope (company/user)' },
    languageSwitcher: { type: 'string', description: 'how language becomes reachable from the top menu; exact mechanism' },
    googleFonts: { type: 'string', description: 'how a Google font is chosen/loaded + the on-prem/offline privacy caveat + fallback' },
    colorPicker: { type: 'string', description: 'the upgraded custom-color UX (no raw native box); LGPL, no risky deps' },
    serverChanges: { type: 'array', items: { type: 'string' }, description: 'new model fields / session_info keys / templates' },
    risks: { type: 'array', items: { type: 'string' } },
  },
}

const PLAN_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['summary', 'steps', 'cantDoLowRisk'],
  properties: {
    summary: { type: 'string' },
    steps: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['order', 'group', 'title', 'files', 'change', 'risk', 'verify'],
        properties: {
          order: { type: 'number' },
          group: { type: 'string', enum: ['bugfix', 'palette-follow', 'polish', 'config-panel'] },
          title: { type: 'string' },
          files: { type: 'array', items: { type: 'string' } },
          change: { type: 'string', description: 'precise edit to make' },
          risk: { type: 'string', enum: ['low', 'medium', 'high'] },
          verify: { type: 'string', description: 'how to confirm it visually' },
        },
      },
    },
    cantDoLowRisk: { type: 'array', items: { type: 'string' }, description: 'anything that cannot be done at low risk + why' },
  },
}

const AUDIT_AREAS = [
  {
    key: 'navbar-menus-palette',
    prompt: `${CONTEXT}\n\nYOUR AREA: Navbar, systray, app menu + section dropdowns + user menu, and PALETTE-FOLLOW.
This is the most important area. Read apps_menu.png, menu_section_open.png, user_menu_open.png, theme_dialog.png,
and EVERY palette_base_* vs palette_blue_* pair. Enumerate exhaustively every surface/element that stays teal in
the *_blue shots (i.e. does NOT follow the company palette) — menu item active/hover highlights, breadcrumb,
dropdown active items, statusbar, switches/toggles, notebook active-tab underline, progress bars, links in
special contexts, badges/tags, settings page accents, etc. For each, give the core class and a low-risk
re-point-sheet (theme_runtime.scss) or token addition that makes it follow --nile-color-brand-primary/accent.
Also flag navbar/systray spacing, alignment, and "cheap" chrome. Inspect tokens.scss, theme_runtime.scss,
nile_shell/static/src/scss/60_navbar.scss, nile_config systray scss.`,
  },
  {
    key: 'kanban',
    prompt: `${CONTEXT}\n\nYOUR AREA: Kanban (grouped + ungrouped dashboards). The user reports "in kanban the column
value is attached to the corner" — find it: look at kanban_grouped_*.png, products_kanban, partners_kanban,
inventory_overview (light AND dark). The column header count/aggregate value (sum, e.g. monetary total, or the
record count) is glued to a corner with no padding/alignment. Pin the exact element + rule in
nile_components/static/src/scss/30_kanban.scss and core. Propose a low-risk spacing/alignment fix. Also audit
general kanban polish: lane tint, header strip, card elevation/borders, folded columns, badge styling, RTL.`,
  },
  {
    key: 'forms-lists-density',
    prompt: `${CONTEXT}\n\nYOUR AREA: Form views, list views, the Settings page, alignment/spacing/density. Read
sale_order_form, sale_orders_list, invoices, settings (light+dark, EN+AR). Hunt the "looks cheap" issues:
misaligned labels/fields, inconsistent gutters, cramped or sloppy spacing, weak table headers, statusbar look,
button bar alignment, chatter. Map each to nile_components 10_form.scss / 20_list.scss and tokens. Low-risk fixes.`,
  },
  {
    key: 'controls-typography-elevation',
    prompt: `${CONTEXT}\n\nYOUR AREA: The overall "cheap" feel — buttons, inputs, badges/tags/chips, typography
scale, radius, borders, elevation/shadows, focus rings. Across ALL shots. Identify where the design tokens are
too flat/inconsistent vs a polished SaaS backend, and propose token-level (tokens.scss) refinements that raise
perceived quality WITHOUT changing brand hues or breaking the WCAG gate. Inspect tokens.scss, contrast.scss,
50_widgets.scss, 70_a11y.scss.`,
  },
  {
    key: 'dialogs-theme-panel-rtl',
    prompt: `${CONTEXT}\n\nYOUR AREA: Dialogs/popovers, the Theme Settings dialog's CURRENT styling, and RTL/Arabic
correctness. Read theme_dialog.png and the ar_001 shots. Critique the current theme dialog's look (cramped,
plain, the raw native color box). List RTL defects (mirroring, alignment, the .rtl. bundle). Map to
nile_config systray scss + 90_rtl.scss. Low-risk fixes. (The full panel REDESIGN is the Design phase — here just
catalog current defects.)`,
  },
  {
    key: 'dark-mode',
    prompt: `${CONTEXT}\n\nYOUR AREA: Dark mode. Read every dark/* shot and the automated luminance findings in
${DARK_LOG}. Flag any surface still light, low-contrast text, white seams, or elements that lost their accent.
Map to nile_components/static/src/scss/dark.scss and tokens.dark.scss. Low-risk fixes only.`,
  },
]

const DESIGN_VARIANTS = [
  {
    key: 'sectioned-preview',
    prompt: `${CONTEXT}\n\nDESIGN TASK (variant A: "sectioned dialog with a live preview pane").
Design a COMPREHENSIVE, user-friendly Theme Settings panel to replace the current cramped 7-control dialog
(the plan's old "<=8 controls" cap is LIFTED — the user wants it rich, like a polished theme configurator, but
Odoo-native and CLEAN-ROOM). It opens from the paint-brush in the top systray. Must cover, at minimum:
  * Company palette: the 6 presets as good-looking swatches + a CUSTOM color with a PROPER picker (see below).
  * Per-user: interface font (incl. a GOOGLE FONT chosen/loaded by the user), font size, density, dark mode,
    chatter position.
  * LANGUAGE: make switching the UI language reachable straight from the TOP MENU (design the exact mechanism —
    e.g. a language item in this dialog and/or a small language entry in the systray/user menu; specify how it
    writes res.users.lang + reloads).
  * GOOGLE FONTS: how the user picks a Google font (curated list + free-text name?), how it's loaded
    (inject Google Fonts <link> / @font-face) and set as --nile-font-stack, with an explicit ON-PREM / OFFLINE
    PRIVACY caveat and a safe fallback when the CDN is unreachable.
  * COLOR PICKER: replace the raw <input type=color> "normal box" with a refined UX (styled swatch + hex input +
    recent/suggested colors and/or a small Owl HSV picker). Must stay LGPL with NO risky new deps, and warn when
    a custom color fails WCAG AA against white button/navbar text.
Keep the existing low-risk plumbing (runtime :root injection, live preview, dark cookie pre-set on save).
Give a concrete, implementable spec (template structure with an ASCII sketch, exact controls, new res.users/
res.company fields, session_info keys, asset wiring) — fill the schema fully.`,
  },
  {
    key: 'tabbed-compact',
    prompt: `${CONTEXT}\n\nDESIGN TASK (variant B: "tabbed/grouped, compact-but-complete").
Same requirements and constraints as variant A (comprehensive, clean-room, language-switcher-in-top-menu,
Google-font loading with on-prem caveat, refined color picker replacing the native box, LGPL/no risky deps,
keep runtime :root injection + live preview + WCAG warn). But take a DIFFERENT structural approach: group the
controls into tabs/segments (e.g. "Brand", "Typography", "Display", "Language") inside the dialog, optimizing
for fast access and a clean compact look rather than a side preview pane. Give a concrete implementable spec
with an ASCII sketch and fill the schema fully.`,
  },
]

phase('Audit')
const auditThunks = AUDIT_AREAS.map(a => () => agent(a.prompt, { schema: FINDINGS_SCHEMA, phase: 'Audit', label: `audit:${a.key}` }))
const designThunks = DESIGN_VARIANTS.map(d => () => agent(d.prompt, { schema: DESIGN_SCHEMA, phase: 'Design', label: `design:${d.key}` }))

const results = await parallel([...auditThunks, ...designThunks])
const auditResults = results.slice(0, AUDIT_AREAS.length).filter(Boolean)
const designResults = results.slice(AUDIT_AREAS.length).filter(Boolean)
const findings = auditResults.flatMap(r => (r.findings || []).map(f => ({ ...f, area: r.area })))
log(`Audit: ${findings.length} findings across ${auditResults.length} areas; ${designResults.length} design variants`)

phase('Synthesize')
const plan = await agent(
  `${CONTEXT}\n\nSYNTHESIZE. You are given (1) all audit findings and (2) two design variants for the new theme
panel. Produce ONE ordered, de-duplicated, LOW-RISK implementation plan.
  * Pick the stronger design (or merge the best of both) for the config-panel steps; justify briefly in summary.
  * Order: group 'bugfix' first (the kanban-corner + any high-severity), then 'palette-follow' (expand the
    re-point sheet so the company color actually applies everywhere), then 'polish' (token/spacing/elevation),
    then 'config-panel' (the redesign).
  * Every step must be LOW risk and name exact files. Drop or down-scope anything that can't be done low-risk and
    list it under cantDoLowRisk.
  * Each step needs a concrete 'change' and a visual 'verify'.
Be precise and implementable — this plan will be executed directly.

=== AUDIT FINDINGS (JSON) ===
${JSON.stringify(findings, null, 1)}

=== DESIGN VARIANTS (JSON) ===
${JSON.stringify(designResults, null, 1)}
`,
  { schema: PLAN_SCHEMA, phase: 'Synthesize', label: 'synthesize-plan' }
)

return { findingsCount: findings.length, findings, designs: designResults, plan }
