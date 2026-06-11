# Spiffy Theme Audit — What We Lose Without It (and What Replaces It)

**Date:** 2026-06-11 · **Branch:** custom-theme · **Odoo:** 18.0 Community · **DB evidence:** disposable copy `erpmedsupply_ns`

## 0. Live uninstall experiment (ground truth)

Spiffy was uninstalled on a throwaway copy of the demo DB (`scripts/duplicate-db.sh erpmedsupply erpmedsupply_ns`,
then `button_immediate_uninstall()` from odoo shell). Results:

- **Uninstall cascade:** only `medsupply_ui_refresh` was removed alongside `spiffy_theme_backend` —
  no business/data addon depends on Spiffy. Uninstalling is SAFE for data.
- **What the UI reverts to** (screenshots in `docs/theme-audit/no-spiffy/`):
  default purple Odoo 18 navbar + standard apps menu (no grid home — `/odoo` lands on Discuss),
  Odoo branding back everywhere (tab title, login), stock flat forms (our card styling gone with the
  cascade), chatter back to stock position, no bookmarks sidebar, no Spiffy global search modal,
  no configurator (palettes/fonts/density/menu layouts), stock list/kanban styling.
- **What KEPT working:** all business flows, all data, kanban-first defaults (`ui_kanban_first` is
  spiffy-independent), RTL/Arabic rendering, command palette (Ctrl+K), core view switchers.
- Recreate the experiment: duplicate DB → relax `dbfilter` in odoo.conf → uninstall in shell →
  capture → restore conf → drop DB + filestore copy.

| Screen | With Spiffy + our overlay | Without Spiffy |
|---|---|---|
| Home | black navbar, app grid home | purple navbar, Discuss inbox |
| Sale order form | card sheet, visible inputs (our overlay) | stock flat form, side chatter |
| Inventory overview | accent-strip tiles | stock plain cards |
| Lists | tinted headers, hover, no gridlines | stock spreadsheet look |

## 1. Spiffy feature inventory (from code, clean-room behavioral notes)

# Spiffy Backend Theme (v1.15, OPL-1) — Exhaustive Feature Inventory

## 1. __manifest__.py
- **Version**: 1.15
- **License**: OPL-1
- **Dependencies**: web, base_setup, portal, resource
- **Author**: Bizople Solutions Pvt. Ltd.

### Data Files Loaded:
- `security/ir.model.access.csv` — 12 model access rules (base.group_user, base.group_public)
- `data/backend_config_data.xml` — Default light theme colors (#0097a7, #ffffff)
- `data/global_level_config.xml` — Global-level theme configuration
- `data/spiffy_default_images.xml` — Demo images for app drawer, menu backgrounds

### Views:
- `views/manifest.xml` — Main menu/app structure
- `views/pwa_offline.xml` — Progressive Web App offline fallback
- `views/backend_configurator_view.xml` — User-facing theme configurator form
- `views/backend_configurator_template.xml` — Configurator UI template (HTML/Qweb)
- `views/res_users_view.xml` — User preference extensions
- `views/res_config_setting.xml` — Company-level settings form
- `views/res_company_view.xml` — Company branding/PWA/Firebase fields
- `views/login_page_style.xml` — Login form template inheritance
- `views/templates_inherit.xml` — Webclient template patches
- `views/to_do_list_template.xml` — User notes/to-do UI
- `views/global_search_view.xml` — Global search configuration
- `views/spiffy_app_group_view.xml` — App grouping/organization
- `views/google_font_family_views.xml` — Custom font management
- `views/ir_module_view.xml` — Module extension
- `views/pwa_shortcuts_view.xml` — PWA app shortcuts config
- `views/menuitems.xml` — Menu customization
- `views/push_notification_menu_view.xml` — Push notification routing

### Assets (Backend):
- **40 SCSS files** covering all view types, form styles, input rendering, menu layouts, responsive design
- **12 XML/Qweb templates** for component rendering (menus, bookmarks, search, modals, dialogs)
- **25 JS modules** for interactivity (menu patching, form controllers, view renderers, color handling, PWA)
- **Custom jQuery UI** bundle for legacy interactions
- **PWA-specific assets** (service worker, manifest handler)

---

## 2. Models (Data Layer)

### Core Configuration Model: `backend.config`
**Table: `backend_config` — Per-user or global theme settings**

| Field Name | Type | What It Controls |
|---|---|---|
| `use_custom_colors` | Boolean | Enable custom color palette override |
| `color_pallet` | Selection (1-19) | Primary color scheme (19 predefined palettes) |
| `light_primary_bg_color` | Char (hex) | Light theme primary background color |
| `light_primary_text_color` | Char (hex) | Light theme primary text color |
| `light_bg_image` | Binary | App drawer background image (light mode) |
| `apply_light_bg_img` | Boolean | Toggle background image display |
| `dark_primary_bg_color` | Char (hex) | Dark mode primary background |
| `dark_primary_text_color` | Char (hex) | Dark mode primary text |
| `dark_secondry_bg_color` | Char (hex) | Dark mode secondary background |
| `dark_secondry_text_color` | Char (hex) | Dark mode secondary text |
| `dark_body_bg_color` | Char (hex) | Dark mode body background |
| `dark_body_text_color` | Char (hex) | Dark mode body text |
| `use_custom_drawer_color` | Boolean | Enable drawer color customization |
| `drawer_color_pallet` | Selection (1-19) | Drawer-specific color scheme |
| `appdrawer_custom_bg_color` | Char (hex) | Custom app drawer background |
| `appdrawer_custom_text_color` | Char (hex) | Custom app drawer text |
| `header_vertical_mini_text_color` | Char (hex) | Vertical mini menu header text |
| `header_vertical_mini_bg_color` | Char (hex) | Vertical mini menu header background |
| `menu_shape_bg_color` | Char (hex) | Enterprise menu background color |
| `menu_shape_bg_color_opacity` | Float | Menu background opacity (0-1) |
| `top_menu_position` | Selection | Menu layout: horizontal, vertical, vertical_mini, vertical_mini_2 |
| `theme_style` | Selection | UI corner style: rounded, standard, square |
| `apply_menu_shape_style` | Boolean | Apply shape style to menu buttons |
| `shape_style` | Selection | Menu button shape: rounded, circle, square |
| `separator` | Selection (1-4) | Field separator style in forms |
| `tab` | Selection (1-4) | Tab widget style |
| `checkbox` | Selection (1-4) | Checkbox input style |
| `radio` | Selection (1-4) | Radio button style |
| `popup` | Selection (1-4) | Modal/dialog popup style |
| `loader_style` | Selection (1-10) | Loading spinner animation style |
| `font_size` | Selection | Font scale: small, medium, large |
| `list_view_density` | Selection | List row spacing: comfortable, compact |
| `list_view_sticky_header` | Boolean | Pin list header while scrolling |
| `input_style` | Selection | Form input appearance: borderless, bottom_border, bordered |
| `chatter_position` | Selection | Chat panel layout: chatter_right, chatter_bottom |
| `tree_form_split_view` | Boolean | Enable split tree-form view panel |
| `show_filter_row` | Boolean | Display/hide list view filter row |
| `attachment_in_tree_view` | Boolean | Show attachments in tree view |
| `vertical_mini_bg_image_one/two/three/four` | Binary | 4 preset vertical menu backgrounds |
| `menu_bg_image` | Binary | Vertical menu header background image |
| `top_menu_bg_vertical_mini_2` | Selection | Vertical mini menu background preset |
| `top_menu_custom_bg_vertical_mini_2` | Binary | Custom vertical menu background upload |
| `google_font_family` | Char | Google Fonts family name string |
| `google_font_links_ids` | One2many | Related google.font.family records |

### Company-Level Settings: `res.company` (extended)
**Additional fields on company records:**

| Field | Type | Purpose |
|---|---|---|
| `backend_theme_level` | Selection | Theme scope: user_level (per-user) or global_level (admin-wide) |
| `tab_name` | Char | Browser tab title (default: "Spiffy") |
| `login_page_style` | Selection (1-4) | Login form design preset |
| `login_page_background_img` | Binary | Login screen background image |
| `login_page_background_color` | Char (hex) | Login background color |
| `login_page_text_color` | Char (hex) | Login text color |
| `show_bg_image` | Boolean | Display login background image |
| `spiffy_favicon` | Binary | Browser tab favicon |
| `backend_menubar_logo` | Binary | Logo displayed in top menu bar |
| `backend_menubar_logo_icon` | Binary | Icon variant of menubar logo |
| `enable_pwa` | Boolean | Enable Progressive Web App mode |
| `app_name_pwa` | Char | PWA full application name |
| `short_name_pwa` | Char | PWA short name (for home screen) |
| `description_pwa` | Char | PWA app description |
| `image_192_pwa` | Binary | PWA icon 192x192px |
| `image_512_pwa` | Binary | PWA icon 512x512px |
| `start_url_pwa` | Char | PWA app entry URL (default: /odoo) |
| `background_color_pwa` | Char (hex) | PWA splash screen background |
| `theme_color_pwa` | Char (hex) | PWA theme color (Android status bar) |
| `pwa_shortcuts_ids` | Many2many | PWA quick-action shortcuts |
| `spiffy_toobar_color` | Char (hex) | Android toolbar color |
| `prevent_auto_save` | Boolean | Force manual save only (disable auto-save) |
| `prevent_auto_save_warning` | Char (translated) | Message shown when auto-save disabled |
| `firebase_server_key` | Char | Firebase Cloud Messaging server key |
| `firebase_key_file` | Binary | Firebase service account JSON file |

### User Extensions: `res.users` (extended)

| Field | Type | Purpose |
|---|---|---|
| `backend_theme_config` | Many2one → backend.config | User's personal theme configuration |
| `dark_mode` | Boolean | Dark mode toggle (user preference) |
| `vertical_sidebar_pinned` | Boolean | Sidebar collapse state (pinned = expanded) |
| `app_ids` | One2many → favorite.apps | User's pinned favorite apps |
| `bookmark_ids` | One2many → bookmark.link | User's saved quick-link bookmarks |
| `bookmark_panel` | Boolean | Show/hide right-side bookmark panel |
| `multi_tab_ids` | One2many → biz.multi.tab | Open multi-tab browser tabs |
| `enable_todo_list` | Boolean | Enable to-do/notes feature |
| `todo_list_ids` | One2many → todo.list | User's to-do list items |
| `mail_firebase_tokens` | One2many → mail.firebase | Firebase push notification device tokens |
| `table_color` | Boolean | (Unused legacy field) |
| `tool_color_id` | Char | (Unused legacy field) |

**Auto-creation**: New users automatically get a default `backend.config` record with primary colors (#0097a7, #ffffff).

### Supporting Models:

| Model | Fields | Purpose |
|---|---|---|
| `favorite.apps` | name, app_id, app_xmlid, app_actionid, user_id | Pinned shortcuts in app drawer |
| `bookmark.link` | name, title, url, user_id | Custom bookmarks sidebar |
| `biz.multi.tab` | name, url, actionId, menuId, menu_xmlid, user_id | Open form tabs (multi-tab feature) |
| `todo.list` | name, description, note_color_pallet, user_id, sequence, timestamps | User notes/to-do items with 7 color palettes |
| `global.search.bizople` | name, global_model_id, global_field_ids (M2M) | Configurable global search indexes per model |
| `pwa.shortcuts` | name, short_name, url, description, image_192_shortcut | PWA home screen quick actions |
| `google.font.family` | name, url, config_id, is_selected, user_id | Custom Google Fonts library per user |
| `ir.ui.menu` (extended) | icon_img, use_icon, icon_class_name, spiffy_app_group_id | Menu icons (image or FontAwesome class) |
| `spiffy.app.group` | name, group_menu_icon, group_menu_list_ids, use_group_icon, group_icon_class_name, sequence | App grouping/organization in drawer |
| `mail.firebase` | user_id, os, token (unique constraint) | Push notification device registration |
| `push.notification.menu` | model_name, menu_id, action_id | Push notification routing rules |

---

## 3. JavaScript Components & OWL Patches

### Main Components (static/src/js/)

| File | OWL Component / Patch | User-Visible Feature | Code Lines | Complexity |
|---|---|---|---|---|
| `menu.js` | NavBar patch + app drawer controller | Sidebar menu, app drawer with search, favorites drag-drop | 400+ | M |
| `apps_menu.js` | App drawer grid layout, search filtering | Apps grid, app grouping, search modal | 300+ | M |
| `color_pallet.js` | Color management utility | Dynamic color theme application (19 palettes, custom colors) | 200+ | S |
| `user_menu.js` | UserMenu patch | Dark mode toggle, language switcher, user avatar | 150+ | S |
| `SwitchCompanyMenu.js` | Company switcher component | Multi-company selector in navbar | 100+ | S |
| `form_view_renderer.js` | FormRenderer patch | Sticky statusbar, input styling (borderless/bordered/bottom-border) | 100+ | S |
| `form_controller.js` | FormController patch | Auto-save prevention, split-view form reload trigger | 50+ | S |
| `list_view_renderer.js` | ListRenderer patch | List density (compact/comfortable), filter row visibility, sticky headers | 150+ | M |
| `pager.js` | Pager patch | View refresh button, chatter position toggle, split-view button, filter-row toggle | 100+ | S |
| `kanban_modal.js` | Kanban modal customization | Kanban card styling (tab styles, separators) | 100+ | S |
| `menu_service.js` | Menu data service extension | Menu icon data retrieval, app group sorting | 100+ | S |
| `SpiffyPageTitle.js` | Page title/breadcrumb patch | Dynamic page title from component metadata | 50+ | S |
| `iconpack_load.js` | Icon pack loader | Font Awesome icon pack async loading | 50+ | S |
| `pwebapp.js` | PWA initialization module | Service worker registration, offline handling, manifest.json loading | 150+ | M |
| `service_worker.js` | Service worker script (Qweb template) | Cache management, offline page serving, asset caching | 200+ (template) | M |
| `flip_min.js` | RTL/LTR direction toggle | Right-to-left layout for Arabic/Hebrew | 50+ | S |

### Split View System (static/src/js/split_view/)

| File | Purpose | Code Lines | Complexity |
|---|---|---|---|
| `split_view_form.xml` | OWL template: split panel form view | 93 | S |
| `split_view_form.js` | OWL component: main split-form container | 304 | M |
| `split_view_controller.js` | View controller: tree-list on left, form on right | 69 | M |
| `split_view_container.js` | Layout container managing resize, scroll sync | 135 | M |
| `split_view_components.js` | Utility components (tree selector, splitter handle) | 45 | S |

**Feature**: Tree-form split view shows hierarchical data (left) and detail form (right) in one view. Configurable via `tree_form_split_view` toggle.

### Widget Components (static/src/js/widgets/)

| File | Widget | Purpose | Complexity |
|---|---|---|---|
| `spiffyDocumentViewer.js` + `.xml` + `.scss` | Document/file viewer modal | Display PDFs, images, documents in modal (integrates ir.attachment) | M |

### Total JS Code: ~4,000+ lines OWL/ES6 modules with patches to core Odoo web components.

---

## 4. Controllers (HTTP Routes & Auth)

**File: `controllers/main.py` — 1,438 lines**

### Public Routes (auth='public') — SECURITY FLAG ⚠️

| Route | Method | Purpose | Security Note |
|---|---|---|---|
| `/color/pallet/` | JSON (POST) | Save user theme settings to backend.config | **SECURITY**: auth='public' — should require auth='user' |
| `/color/pallet/data/` | HTTP (GET) | Render theme config form template | auth='public' |
| `/get/model/record` | JSON (GET) | Fetch current user's backend.config with theme values | auth='public' |
| `/get-favorite-apps` | JSON (GET) | List user's pinned apps | auth='public' |
| `/get/active/menu` | JSON (GET) | Top-level menus for app drawer | auth='public' |
| `/get/appsearch/data` | JSON (GET) | Global app search by name | auth='public' |
| `/get/tab/title/` | JSON (GET) | Company tab title | auth='public' |
| `/get/active/lang` | JSON (GET) | Available languages | auth='public' |
| `/change/active/lang` | JSON (POST) | Switch user language | auth='public' |
| `/update-user-fav-apps` | JSON (POST) | Add favorite app | auth='public' |
| `/remove-user-fav-apps` | JSON (POST) | Remove favorite app | auth='public' |
| `/active/dark/mode` | JSON (POST) | Toggle dark mode on user | auth='public' |
| `/get/dark/mode/data` | JSON (GET) | Fetch dark mode setting | auth='public' |
| `/update/bookmark/panel/show` | JSON (POST) | Toggle bookmark sidebar visibility | auth='public' |
| `/sidebar/behavior/update` | JSON (POST) | Pin/unpin sidebar | auth='public' |
| `/get/bookmark/link` | JSON (GET) | List user bookmarks | auth='public' |
| `/add/bookmark/link` | JSON (POST) | Create bookmark | auth='public' |
| `/update/bookmark/link` | JSON (POST) | Modify bookmark | auth='public' |
| `/remove/bookmark/link` | JSON (POST) | Delete bookmark | auth='public' |
| `/update/chatter/position` | JSON (POST/GET) | Set chatter right/bottom position | auth='public' |
| `/get/mutli/tab` | JSON (GET) | List open multi-tabs | auth='public' |
| `/add/mutli/tab` | JSON (POST) | Open new tab | auth='public' |
| `/remove/multi/tab` | JSON (POST) | Close tab | auth='public' |
| `/update/tab/details` | JSON (POST) | Rename/relink tab | auth='public' |
| `/get/attachment/data` | JSON (GET) | Fetch attachments for records | auth='public' |
| `/get/irmenu/icondata` | JSON (GET) | Menu icon data + spiffy_app_group structure | auth='public' |
| `/show/user/todo/list/` | HTTP (GET) | Render to-do list template | auth='public' |
| `/create/todo` | JSON (POST) | Create/update to-do item with color palette | auth='public' |
| `/delete/todo` | JSON (POST) | Delete to-do | auth='public' |

### User-Level Routes (auth='user')

| Route | Purpose |
|---|---|
| `/get/records/global/search` | Fetch configured global search indexes (respects user permissions) |
| `/update/split/view` | Toggle tree-form split view |
| `/update/filter/row` | Toggle list filter row |
| `/filter/relational/field/list` | Search related model values for filters |
| `/filter/relational/field/data` | Get related record data by IDs |
| `/selection/filter/list` | Get selection field options |

### Protected Routes (auth='none' or 'user')

| Route | Auth | Purpose |
|---|---|---|
| `/text_color/label_color` | 'none' | Report export with optional PDF color preservation |
| `/attach/get_data` | 'user' | Download attachment with MIME type |
| `/app/attachment/upload` | 'public' (with CSRF) | Upload attachment via mail |
| `/theme_color/parameter_check` | 'none' | Pre-login theme color check + Firebase device registration |
| `/add/google/font` | 'none' | Add custom Google Font (max 5 per user) |
| `/delete/google/font` | 'none' | Remove custom font |
| `/update_single_font_selection` | 'user' | Mark font as active |
| `/report/pdf/<reportname>/` | 'user' | PDF report generation with color preservation |
| `/service_worker.js` | 'public' | Service worker script (PWA) |
| `/pwa/enabled` | 'public' | Check PWA enabled status |
| `/pwa/offline` | 'public' | Offline fallback page |
| `/spiffy_theme_backend/<company_id>/manifest.json` | 'public' | PWA manifest (app name, icons, shortcuts) |
| `/web/dataset/call_kw` | 'user' | Override dataset call for Odoo RPC |

### Report Handling
- Custom report export routes with base64 encoding for PDF/Excel
- Color preservation (`request.session.bg_color` flag)
- Pivot export, grouped export, tree export (xlsx)

---

## 5. Views & Templates

### Login Page (views/login_page_style.xml)
Inherits Odoo web login template with:
- 4 login style presets (login_style_1-4)
- Custom background image & color
- Custom text color
- Company favicon display

### Configuration UI (views/backend_configurator_view.xml + backend_configurator_template.xml)
**Form-based theme customizer** with tabs:
- **Colors**: 19 light + 19 drawer palettes, custom color overrides
- **Images**: App drawer bg, vertical menu backgrounds (4 presets)
- **Styles**: Theme corners (rounded/standard/square), menu shapes, input styles
- **UI Elements**: Tab style, checkbox style, radio style, popup style, separator style, loader style
- **Layout**: Menu position (horizontal/vertical/vertical_mini), chatter position (right/bottom)
- **Fonts**: Google Fonts selector (max 5), font size (small/medium/large)
- **Lists**: Row density (comfortable/compact), sticky headers
- **Advanced**: Tree-form split view, filter row visibility, attachment in tree

**User-facing Web Form** at `/color/pallet/data/` uses `spiffy_theme_backend.template_backend_config_data` template with:
- Live color picker widgets
- Image upload dropzones
- Style preview cards
- Quick preset buttons
- Save/Apply button (POST to `/color/pallet/`)

### Web Customization (views/templates_inherit.xml)
Core Odoo web template inheritance:
- Navbar customization (logo, menu button style)
- Sidebar styling
- Modal/dialog styling
- View control panel patches

### PWA Templates
- `pwa_offline.xml` — Offline page when service worker cache missed
- `service_worker.js` (Qweb) — Dynamic service worker registration script

### To-Do/Notes (views/to_do_list_template.xml + models/to_do_list.py)
User note interface with 7 color palettes (pallet_1-7), ordered by recent date.

### Menu Customization (views/spiffy_app_group_view.xml)
Define app groups to organize top-level menus:
- Group name
- Group icon (image or FontAwesome class)
- Assigned top-level menus (One2many ir.ui.menu)
- Sequence ordering

---

## 6. SCSS Modules (Styling Layers)

**43 SCSS files totaling ~5,000+ lines** covering:

### View-Specific Styles
| File | What It Styles | Configurable Via |
|---|---|---|
| `list_view.scss` | List rows, columns, row height | input_style, list_view_density |
| `form_view.scss` | Form layout, fieldset, group spacing | input_style, theme_style |
| `form_chatter.scss` | Chat sidebar, message bubbles | chatter_position |
| `kanban_view.scss` | Kanban cards, card height | theme_style |
| `graph_view.scss` | Chart styling | color_pallet |
| `pivot_view.scss` | Pivot table styling | color_pallet |
| `calendear_view.scss` | Calendar grid, event styling | color_pallet |
| `activity_view.scss` | Activity timeline | color_pallet |
| `tree_form_split_view.scss` | Split panel layout, resize handle | (hardcoded) |

### Input/Control Styles
| File | What It Styles | Options |
|---|---|---|
| `checkbox_styles.scss` | Checkbox appearance | checkbox: style_1-4 |
| `radio_styles.scss` | Radio button appearance | radio: style_1-4 |
| `separator_styles.scss` | Form field separator line | separator: style_1-4 |
| `tab_styles.scss` | Tab widget appearance | tab: style_1-4 |
| `popup_styles.scss` | Modal/dialog appearance | popup: style_1-4 |

### Layout Styles
| File | What It Styles | Options |
|---|---|---|
| `top_menu_horizontal.scss` | Horizontal menu bar layout | top_menu_position: horizontal |
| `top_menu_vertical.scss` | Vertical sidebar menu | top_menu_position: vertical |
| `top_menu_vertical_mini.scss` | Compact vertical menu | top_menu_position: vertical_mini |
| `menu_shape_styles.scss` | Menu button shapes | shape_style: rounded/circle/square |
| `appdrawer.scss` | App drawer panel | color_pallet, use_custom_drawer_color |
| `side_menu.scss` | Sidebar styling | top_menu_position |
| `burger_menu.scss` | Mobile hamburger menu | (responsive) |

### Global Styles
| File | Purpose |
|---|---|
| `custom_varibles.scss` | SCSS variables for colors, spacing, fonts (imports color_pallet.js-generated CSS) |
| `common_view.scss` | Common element styling (buttons, links, badges) |
| `responsive.scss` | Mobile breakpoints, touch-friendly spacing |
| `notification.scss` | Toast notifications |
| `modal.scss` | Modal/dialog base styling |
| `search_modal.scss` | Global search modal styling |
| `chat_window.scss` | Chat box styling |
| `discuss_style.scss` | Discuss/messaging UI |
| `controlpannel.scss` | Control panel (action buttons) |
| `loader.scss` | Spinner animations (10 styles via loader_style) |
| `font_icons.scss` | FontAwesome icon imports |
| `datetime_pickers.scss` | Date/time picker styling |
| `search_panel.scss` | Search filter panel |
| `setting_page.scss` | Settings form styling |
| `website_menu.scss` | Website portal menu styling |
| `multi_tab.scss` | Multi-tab browser UI |
| `to_do_list.scss` | Note/to-do item cards |
| `list_view_row_filters.scss` | Inline row filter buttons |
| `dashboards.scss` | Dashboard grid layouts |

### Responsive Design
- Mobile-first approach with tablet/desktop breakpoints
- Touch-friendly spacing for mobile funnel view
- Hamburger menu for narrow screens

---

## 7. Security & Access Control

### Model Access (security/ir.model.access.csv)

| Model | Group | Read | Write | Create | Delete | Notes |
|---|---|---|---|---|---|---|
| favorite.apps | group_user | ✓ | ✗ | ✗ | ✗ | Read-only (managed by /update-user-fav-apps) |
| bookmark.link | group_user | ✓ | ✗ | ✗ | ✗ | Read-only (managed by /add/bookmark/link) |
| backend.config | group_user | ✓ | ✓ | ✓ | ✗ | Users can modify own config, not delete |
| pwa.shortcuts | group_user | ✓ | ✓ | ✓ | ✓ | Full admin control |
| pwa.shortcuts | group_public | ✓ | ✗ | ✗ | ✗ | Public read-only (for PWA manifests) |
| biz.multi.tab | group_user | ✓ | ✗ | ✗ | ✗ | Read-only (managed by /add/mutli/tab) |
| todo.list | group_user | ✓ | ✓ | ✓ | ✓ | Full user control |
| mail.firebase | group_user | ✓ | ✓ | ✓ | ✓ | Push notification device tokens |
| push.notification.menu | group_user | ✓ | ✓ | ✓ | ✓ | Admin-configured notification routing |
| global.search.bizople | group_user | ✓ | ✓ | ✓ | ✓ | Global search index configuration |
| spiffy.app.group | group_user | ✓ | ✓ | ✓ | ✓ | App drawer organization |
| google.font.family | group_user | ✓ | ✓ | ✓ | ✓ | User-specific Google Fonts |

### Security Concerns

⚠️ **HIGH**: Multiple routes with `auth='public'` that modify user data:
- `/color/pallet/` — Saves theme config without auth
- `/update-user-fav-apps` — Adds favorite apps (auth='public')
- `/active/dark/mode` — Toggles dark mode (auth='public')
- `/theme_color/parameter_check` — Checks theme & registers Firebase token (auth='none')

**Mitigation**: Routes use `request.env.user` to target current session; relies on Odoo's session management. However, `auth='public'` should be `auth='user'` for data-modifying operations.

**SQL Constraint** (mail.firebase):
```sql
UNIQUE(token, os, user_id)
CHECK (token IS NOT NULL)
```

---

## 8. Data Files & Defaults

### backend_config_data.xml
Single default record (id: backend_config_data):
- light_primary_bg_color: #0097a7 (teal)
- light_primary_text_color: #ffffff (white)
- (Commented: default Google Font 'Rubik')

### global_level_config.xml
(Content not detailed in manifest — likely sets system-wide defaults)

### spiffy_default_images.xml
Demo images:
- app-drawer-bg-image.png
- top-menu-v2-bg1/2/3/4.jpg
- header_vertical_mini.svg

---

## 9. Feature Complexity & Reimplement Summary

### Master Feature Table

| Feature | What It Does | Tech Stack | User-Visible Impact | Reimplement Complexity |
|---|---|---|---|---|
| **Theme Color Palettes (19)** | Predefined color schemes for UI | SCSS variables + JS color_pallet.js | Instant theme switch | S |
| **Custom Color Override** | User picks exact hex colors for primary/secondary/dark | JS color picker + backend.config ORM | Live color picker UI | S |
| **Dark Mode** | Toggle dark/light theme | SCSS dark theme + dark_mode boolean + color_pallet.js | Toggle button in user menu | S |
| **Menu Position** | Horizontal/vertical/mini layout | 3 separate SCSS files + menu.js patch | Menu position selector | M |
| **App Drawer** | Slide-out app grid with search & favorites | OWL component (menu.js) + appdrawer.scss | Left sidebar grid interface | M |
| **App Grouping** | Organize top-level menus into groups | spiffy.app.group model + menu.js | App drawer groups with icons | M |
| **Menu Icons** | Display icon (image or FontAwesome class) | ir.ui.menu icon_img/icon_class_name fields | Icon next to menu label | S |
| **Global App Search** | Full-text search across models | global.search.bizople model + apps_menu.js modal | Search modal in app drawer | M |
| **Bookmarks Sidebar** | Quick links panel | bookmark.link model + right sidebar OWL component | Right panel with links | S |
| **Multi-Tab System** | Open multiple forms in tabs | biz.multi.tab model + multi_tab.scss + menu.js | Tab bar under top menu | M |
| **Split Tree-Form View** | Hierarchical list (left) + detail form (right) | split_view/* OWL components + tree_form_split_view.scss | Side-by-side view layout | L |
| **Document Viewer** | Modal file preview (PDF, images) | spiffyDocumentViewer OWL component | Attachment preview modal | M |
| **To-Do/Notes** | User note-taking feature | todo.list model + to_do_list_template.xml | Notes panel in sidebar | S |
| **Chatter Position** | Right sidebar vs. bottom chat panel | form_chatter.scss + form patch | Toggle chatter layout | S |
| **Form Input Styles** | Borderless/bottom-border/full-bordered inputs | 3 SCSS variants + form_view_renderer.js | Form appearance change | S |
| **List Density** | Comfortable/compact row spacing | list_view.scss + list_view_renderer.js patch | Row height toggle | S |
| **List Sticky Header** | Pin header while scrolling | list_view.scss (position: sticky) + patch | Sticky column header | S |
| **Tab Styles (4)** | Different tab widget appearances | tab_styles.scss (4 variants) | Tab appearance selector | S |
| **Checkbox Styles (4)** | Different checkbox designs | checkbox_styles.scss (4 variants) | Checkbox appearance selector | S |
| **Radio Styles (4)** | Different radio button designs | radio_styles.scss (4 variants) | Radio appearance selector | S |
| **Popup Styles (4)** | Modal/dialog visual variants | popup_styles.scss (4 variants) | Modal appearance selector | S |
| **Separator Styles (4)** | Form field divider line variants | separator_styles.scss (4 variants) | Field separator appearance | S |
| **Theme Corners** | Rounded/standard/square UI elements | theme_style SCSS variables | Border-radius toggle | S |
| **Menu Shapes** | Rounded/circle/square menu buttons | shape_style + menu_shape_styles.scss | Menu button corner style | S |
| **Loader Styles (10)** | Different spinner animations | loader.scss (10 CSS animations) | Loading animation variant | S |
| **Font Size** | Small/medium/large text scaling | font_size in custom_varibles.scss | Global font scale | S |
| **Google Fonts** | Custom font library (max 5 per user) | google.font.family model + font_family.xml template | Font dropdown selector | S |
| **Login Page Styling** | 4 login form templates | login_page_style.xml (4 presets) + loginpage.scss | Login screen appearance | S |
| **Login Background Image** | Custom login bg image & color | res.company login_page_background_img field | Login background picker | S |
| **Browser Tab Title** | Custom browser tab name | res.company tab_name field + /get/tab/title/ | HTML <title> tag | S |
| **Favicon** | Custom browser tab icon | res.company spiffy_favicon field | Favicon.ico in navbar | S |
| **Menubar Logo** | Company logo in top menu | res.company backend_menubar_logo field | Logo display in navbar | S |
| **PWA Support** | Progressive Web App mode (installable) | pwa/* controllers + service_worker.js + manifest.json | Install button + offline mode | L |
| **PWA App Shortcuts** | Home screen quick actions | pwa.shortcuts model + manifest.json | Quick action shortcuts | S |
| **PWA Offline Page** | Fallback when offline | service_worker.js (cache) + pwa_offline.xml | Offline.html page | M |
| **Firebase Push Notifications** | Android push notification tokens | mail.firebase model + theme_color/parameter_check route | Device registration | M |
| **Push Notification Routing** | Trigger push on model events | push.notification.menu model | Background notifications | M |
| **Auto-Save Prevention** | Disable auto-save, require manual save | prevent_auto_save (company field) + form patch | Save button mandatory | S |
| **Filter Row Visibility** | Show/hide list filter bar | show_filter_row + list patch | Filter row toggle | S |
| **Tree View Attachments** | Show file count in tree view | attachment_in_tree_view + tree renderer patch | Attachment badge | S |
| **List Rendering** | Custom list row height, checkbox, density | list_view_renderer.js patch + list_view*.scss | List appearance | M |
| **Form Statusbar** | Custom button styling in form header | form_statusbar.xml template | Action buttons appearance | S |
| **Responsive Design** | Mobile-optimized layout | responsive.scss + mobile funnel view | Mobile view collapse | M |
| **RTL Support** | Right-to-left text direction (Arabic/Hebrew) | flip_min.js + responsive.scss | Layout flipping | M |
| **Multi-Language** | Translation support in templates | Odoo's _t() + lang switch route | Language selector | S |
| **Report Export** | PDF/Excel export with color preservation | text_color/label_color route + custom ExportXlsxWriter | Colored report output | M |
| **User Preferences Persistence** | Save all theme settings per user | backend.config model + session storage | Settings retained on login | S |
| **Global vs. User-Level Theming** | Admin theme or per-user theme | backend_theme_level selection (global/user_level) | Theme scope toggle | M |

---

## Summary: What Spiffy Does vs. How It Does It

### Core Philosophy
**Customizable Odoo backend UI** with 30+ configuration options, split across:
1. **Company-level** (branding, PWA, login page)
2. **User-level** (personal theme, colors, preferences)
3. **Admin-level** (menu organization, global search, app groups)

### Key Innovation Areas
- **19 + 19 color palettes** + unlimited custom color override (SCSS variables + JS color injection)
- **4 layout presets** (horizontal/3 vertical menus) with multiple style variants
- **Split tree-form view** (OWL components with resize, scroll-sync)
- **App drawer organization** (grouping, search, favorites drag-drop)
- **PWA first-class support** (manifest, offline, shortcuts, push notifications via Firebase)
- **Theme persistence** (backend.config ORM model per user)
- **Responsive design** with mobile funnel view
- **RTL ready** (Arabic/Hebrew language support)

### Reimplement Effort (Clean-Room)
- **Quick wins (S = small)**: Individual style options, toggles, 1-2 line changes (40+ features)
- **Medium complexity (M = medium)**: Component patches, modal UI, search system (12 features)
- **High effort (L = large)**: Split view system, PWA infrastructure (2 features)

**Total estimated effort to rebuild parity**: ~4-6 weeks for experienced Odoo developer (assuming working ES6/OWL/SCSS knowledge).

---

## Missing/Unused Code
- Firebase integration partially commented out in res_config_setting.py
- Some legacy fields marked as "unused" in res_users.py (table_color, tool_color_id)
- Auth TOTP (2FA) integration present but not core to theme

## Not Covered in Spiffy
- Database migration tools
- Audit logging for configuration changes
- A/B testing or analytics
- Theme marketplace/distribution
- Accessibility (WCAG) compliance testing documented

---

**License**: OPL-1 (Odoo Proprietary License v1) — Code cannot be modified or redistributed without author consent.

## 2. Coupling map & in-house theme addons assessment

## 1. SPIFFY THEME DEPENDENCY MAP

### Direct Dependencies on spiffy_theme_backend

| Dependent Addon | Manifest Path | Dependency Context | Impact |
|---|---|---|---|
| **medsupply_ui_refresh** | `/custom-addons/medsupply_ui_refresh/__manifest__.py` | `'spiffy_theme_backend'` in depends list | **CRITICAL**: Uninstalling spiffy cascades this addon. UI refresh overlay (SCSS only) depends on asset-load ordering. |

**No other custom addons depend on spiffy_theme_backend in their `depends` field.**

---

## 2. IN-HOUSE THEME ADDON ASSESSMENTS

### eoc_theme_backend
- **Path**: `/custom-addons/eoc_theme_backend/`
- **Files**: 4 (manifest, init, 1 SCSS, 1 XML)
- **Size**: 12K
- **Manifest**: License LGPL-3, author blank, no spiffy dependency
- **Scope**: Minimal custom brand colors overlay
- **Contents**:
  - `__manifest__.py`: 12 lines, no code
  - `views/assets.xml`: Inherits `web_editor.13_0_color_system_support_primary_variables_scss`, appends `/eoc_theme_backend/static/src/scss/theme_style.scss`
  - `static/src/scss/theme_style.scss`: 3 lines, sets `$o-community-color: #56fc03` (neon green) + brand vars
- **Verdict**: ✅ **ORIGINAL, NO LICENSE CONTAMINATION**
  - Pure SCSS variable declarations, zero code reuse
  - Minimal footprint, zero XPath manipulation
  - Could serve as seed for custom theme (this pattern is clean and portable)

### ephem_theme_backend
- **Path**: `/custom-addons/ephem_theme_backend/`
- **Files**: Only `__pycache__`, `controllers/`, `models/` subdirs (no __manifest__.py)
- **Size**: 40K
- **Status**: **STUB ADDON (incomplete, non-functional)**
  - Has directories but no `__manifest__.py` → will not install
  - Would not be active even if project installs all addons
- **Verdict**: ⚠️ **DEAD CODE, SHOULD BE REMOVED**

### ephem_theme_push
- **Path**: `/custom-addons/ephem_theme_push/`
- **Files**: Only `__pycache__`, `models/` subdir (no __manifest__.py)
- **Size**: 20K
- **Status**: **STUB ADDON (incomplete, non-functional)**
  - No `__manifest__.py` → inert
- **Verdict**: ⚠️ **DEAD CODE, SHOULD BE REMOVED**

---

## 3. THIRD-PARTY DEBRANDING ADDONS (no spiffy dependency)

All 5 debranding addons are **OCA/community-origin**, unrelated to spiffy, and do NOT depend on it.

| Addon | License | Author | Depends On | Purpose | Size | Assessment |
|---|---|---|---|---|---|---|
| **mail_debrand** | AGPL-3 | Tecnativa, OCA | `mail` | Remove Odoo branding from sent email templates | 184K | ✅ OCA stable, no theme link |
| **portal_odoo_debranding** | LGPL-3 | TAKOBI, OCA | `portal` | Remove branding from portal templates | 68K | ✅ OCA stable, no theme link |
| **website_odoo_debranding** | LGPL-3 | Tecnativa, OCA | `website` | Remove branding from website | 76K | ✅ OCA stable, no theme link |
| **wk_debrand_odoo** | Proprietary (Webkul) | Webkul Software | `web`, `mail`, `portal` | Backend debranding (JS + XML) | 280K | ✅ Third-party, paid module, no theme link |
| **disable_odoo_online** | AGPL-3 | Therp BV, OCA | `mail` | Remove odoo.com bindings | 112K | ✅ OCA stable, no theme link |

**None of these depend on spiffy or theme at all.** Their scope is branding removal only (mail, portal, website, UI chrome), orthogonal to backend theme choice.

---

## 4. MEDSUPPLY_UI_REFRESH (spiffy-dependent overlay)

- **Path**: `/custom-addons/medsupply_ui_refresh/`
- **Files**: 6 (manifest, init, 1 XML, 5 SCSS)
- **Size**: 32K
- **Manifest**: License LGPL-3, author "Sudan MedSupply Co."
- **Depends**: `['web', 'spiffy_theme_backend', 'sale_management', 'purchase', 'stock']`
- **Scope**: Pure CSS overlay — no Python code, no XPath manipulation
- **Contents**:
  - `__manifest__.py`: Comments carefully note "Plain appends only — no ('after', ...) tuples targeting spiffy/core files"
  - Assets all appended (no custom ordering), rely on dependency-based load sequencing
  - `views/kanban_group_by.xml`: Clean view inheritance (3 records, set `default_group_by` on kanban boards)
  - `static/src/scss/`:
    - `00_variables.scss`: Custom CSS custom-properties (`--msr-*`), additive only, never override spiffy's `--biz-theme-primary-color`
    - `10_form.scss`, `20_list.scss`, `30_kanban.scss`, `40_rtl.scss`: Card styling, form tweaks, RTL corrections — zero spiffy selectors, pure Odoo base selectors
- **Verdict**: ✅ **ORIGINAL, CLEAN OVERLAY**
  - No code copied from spiffy
  - Well-documented design-token pattern (additive, non-destructive)
  - **Cannot be uninstalled without uninstalling spiffy** (hard dependency)

---

## 5. CMP PROJECT (no spiffy references)

- **Path**: `/Projects/cmp/cmp/`
- **Manifest**: Depends on `['cmp_core', 'eoc_base', 'mail', 'mass_mailing', 'event', 'calendar', 'contacts', 'auth_signup', 'portal']`
- **Theme addon presence**: **NONE**
- **Spiffy references**: **ZERO** (grep found no spiffy strings anywhere in CMP)
- **Assets**: Only custom `web.assets_backend` with JS/SCSS (deployment_matrix, entity_map) — no theme-specific code
- **Verdict**: ✅ **CMP is theme-agnostic**
  - Does NOT depend on spiffy_theme_backend
  - Renders fine under any backend theme (spiffy, eoc_theme_backend, or vanilla Odoo)
  - No documentation or screenshots tied to spiffy look

---

## 6. DOCS & SCRIPTS SPIFFY BLAST RADIUS

### User Manual & Deck (docs/manual/, docs/deck/)
**CRITICAL**: Both artifacts embed **Spiffy-specific UI terminology and screenshots**, all bilingual.

#### Manual `/docs/manual/_content/*.json` sections hardcoding spiffy:
1. **intro.json**: `"The screens use the **Spiffy backend theme**, which gives the system its modern look: a dark navigation bar across the top, a 9-dot grid icon that opens the app launcher, a vertical quick-action rail down the side of the screen, and a friendly greeting..."`
2. **interface.json** (section 2.2): `"A tour of the screen (the Spiffy interface)"`
   - Describes Spiffy's **dark top navbar**, **9-dot app launcher**, **vertical quick-action rail** (not present in vanilla Odoo)
   - References "Spiffy" by name 4+ times
3. **images** in `docs/manual/img/{en,ar}/`:
   - `apps_home.png`: Screenshot of Spiffy's app launcher with grid icons and side rail
   - All other screenshots assume Spiffy's dark navbar, vertical rail UI chrome
   - Arabic version (`img/ar/`) has RTL-mirrored layouts (require Spiffy + RTL rendering)

#### Deck `/docs/deck/Medical-Supply_ERP_Demo_Deck_{EN,AR}.{html,pdf}`:
- **15 slides total**, ~7+ slides heavily screenshot-dependent:
  - Capability slides (4–10) each show "SHOW LIVE" bands with real Spiffy UI captures
  - Home/launcher slides (slides 3, some of 4) assume Spiffy's app grid and dark navbar
  - All images rendered inside container with Spiffy active (checked in `capture_screens.py`)
- **Arabic deck** requires RTL screenshots + bilingual text (cannot reuse English deck images)

### Build Scripts & Skill docs

#### `/scripts/build_deck.py` & `/scripts/build_manual.py`
- **No hardcoded spiffy names**, but both assume **Spiffy is the running theme** when extracting demo data
- Comments note: "every screenshot is a real capture of the themed Odoo UI"

#### `/scripts/capture_screens.py`
- **Explicitly assumes Spiffy is active**:
  ```python
  """The Spiffy backend theme is active, so these reflect the real, themed UI."""
  """Open the Spiffy full-screen app launcher for the home shot."""
  page.wait_for_selector(".o_main_navbar", timeout=30000)
  ```
- Waits for Spiffy's `.o_main_navbar` (class unique to Spiffy's navbar implementation)
- **If theme swaps, capture must re-run** to get the new navbar/rail visuals

#### `.claude/skills/erp-medsupply-demo/SKILL.md`
- Line: `--with=spiffy_theme_backend` in install list (step 2)
- Line: "The UI now runs the **Spiffy backend theme**" (documentation)
- **Step 4** ("Serve + verify") assumes Spiffy is active
- **If theme swaps, skill docs must update** (install list + verification screenshot callouts)

#### `.claude/skills/manual-deck-builder/SKILL.md`
- No explicit spiffy reference in prose, but **implies Spiffy rendering**:
  - "All images as base64, so the HTML/PDF is fully self-contained"
  - Re-capture requirement: "After any reseed, re-verify the numbers on the slides/manual and re-capture screens"
  - Does NOT discuss theme variations

---

## 7. TEST COMMENTS (external references)

**File**: `/custom-addons/cmp_deployment/tests/test_community_scope.py`

Comment only (not code dependency):
```python
# session_info() requires an HTTP request context (third-party module
# spiffy_theme_backend reads request.session.bg_color). Validated via
# the HTTP smoke in Phase L.1; cannot run under TransactionCase.
```
- **Zero functional impact** (just a note about why tests can't run under TransactionCase)
- Not a real dependency, just documentation

---

## 8. SPIFFY_THEME_BACKEND CHARACTERISTICS (for reference)

| Property | Value |
|---|---|
| **Author** | Bizople Solutions Pvt. Ltd. |
| **License** | Odoo Proprietary License v1.0 |
| **Files in repo** | 345 |
| **Size** | 171M (includes Firebase SDK, icon packs, etc.) |
| **Depends** | `['web', 'base_setup', 'portal', 'resource']` |
| **Models** | 6+ (backend_configurator, ir_menu, mail_channel, res_config_setting, spiffy_app_group, etc.) |
| **Controllers** | 2+ (main.py, pwa.py) |
| **Key features** | Dark navbar, 9-dot app launcher, vertical rail, PWA support, RTL, multi-lang, push notifications |

**NOT a rebranding addon** — it's a full theme engine with state (configs, PWA shortcuts, color palettes per company/user).

---

## 9. DEPENDENCY GRAPH (simplified)

```
spiffy_theme_backend (third-party, Bizople)
    └── medsupply_ui_refresh (in-house, SCSS overlay)

eoc_theme_backend (in-house, minimal, original)
    └── (no dependents)

ephem_theme_backend (stub, non-functional)
ephem_theme_push (stub, non-functional)

mail_debrand, portal_odoo_debranding, website_odoo_debranding, 
wk_debrand_odoo, disable_odoo_online
    └── (none depend on spiffy or theme)

CMP
    └── (no theme dependency)

Docs (manual/deck) & Skills
    └── hardcoded screenshots, terminology, and install steps
        assume spiffy_theme_backend is active
```

---

## 10. THEME SWAP IMPACT SUMMARY

If you **uninstall spiffy** and install a different backend theme:

| Area | Impact | Effort |
|---|---|---|
| **medsupply_ui_refresh** | **MUST uninstall** (hard dep on spiffy) | Immediate (cascades) |
| **eoc_theme_backend** | Safe to keep (orthogonal color overlay) | None |
| **ephem_theme_backend, ephem_theme_push** | Remove (dead code anyway) | Low (delete directories) |
| **Debranding addons** | No impact | None |
| **CMP project** | No impact | None |
| **User manual** (all 8 sections in `interface.json`, `intro.json`) | **Must re-edit** English & Arabic for new UI chrome (navbar, rail, launcher) | HIGH: re-write intro + interface chapter, re-capture all screenshots for both languages |
| **Sales deck** (15 slides) | **Must re-capture** 7+ slides with new theme's navbar/chrome | HIGH: re-capture + re-verify 15 slide layout, redo Arabic RTL screenshots |
| **Skill docs** (erp-medsupply-demo) | **Must update** install list + verification notes | MEDIUM: update manifest, test capture script |
| **capture_screens.py** | **Must rewrite** navbar wait selector + app launcher opener | MEDIUM: adapt to new theme's CSS classes |

**Conclusion**: A theme swap is **NOT trivial** — it requires full re-capture (run `capture_screens.py` with new theme), re-edit of bilingual manual & deck, and re-test of all demo verification steps. The **smallest in-house theme addon (eoc_theme_backend) could serve as a seed** for building a custom replacement, since it's minimal, original LGPL-3 code with no spiffy dependencies.



## 3. Open-source (LGPL) building blocks & licensing ground rules


# Research: Replacing Bizople Spiffy (OPL-1) with a legally clean LGPL-3 stack on Odoo 18.0 Community

## 1. OCA `web` repo — 18.0 branch status

Verified directly against the live branch (GitHub API directory listing + each module's `__manifest__.py` on 18.0, checked 2026-06-11). The branch holds **~58 addons**; all the ones you asked about ARE ported. OCA convention: no `development_status` key = **Beta** (the default OCA maturity); "Production/Stable" is explicit.

### Modules you asked about

| Module | 18.0 version | License | Maturity | Feature set (18.0) |
|---|---|---|---|---|
| `web_responsive` | 18.0.1.0.6 | **LGPL-3** | **Production/Stable** | Fullscreen **app drawer** with auto-focused quick search; sticky list headers/footers and form statusbars; bigger list checkboxes; mobile: icon-only control-panel buttons, uncramped view switcher, scaled form inputs; desktop: Alt+Shift+NUM hotkeys (avoids Firefox conflicts), document viewer docked beside chatter with maximize toggle, colored public-vs-internal message composer; optional redirect-to-home preference. Roadmap gaps: keyboard nav of apps, long form titles. |
| `web_chatter_position` | 18.0.1.1.0 | **LGPL-3** | Beta | Per-user preference: chatter on side/bottom; form sheet gets full width. Works Community & Enterprise. |
| `web_dialog_size` | 18.0.1.0.1 | AGPL-3 | Beta | Expand/restore button on dialogs to full screen width; default configurable. |
| `web_dark_mode` | 18.0.1.0.0 | AGPL-3 | Beta | Per-user dark mode toggle in user menu for **Community** (reuses Odoo's own dark assets). By initOS. Roadmap: PoS dark mode missing. |
| `web_save_discard_button` | 18.0.1.0.1 | AGPL-3 | Beta | Restores explicit Save & Discard buttons in form views. |
| `web_refresher` | 18.0.1.0.0 | AGPL-3 | Beta | Refresh button in the control panel/pager to reload view data without F5. |
| `web_company_color` | 18.0.1.0.8 | AGPL-3 | Beta | Per-company recolor of the web client (navbar/brand colors) from company form. |
| `web_environment_ribbon` | 18.0.1.0.3 | AGPL-3 | Beta | Corner ribbon showing environment name (TEST/DEV) — ops nicety. |
| `web_theme_classic` | 18.0.1.2.1 | AGPL-3 | Beta | Contrasted/bordered field styling to improve readability (classic-look restyle). |
| `web_notify` | 18.0.1.1.1 | **LGPL-3** | **Production/Stable** | Server-initiated toast notifications (`user.notify_success/danger/warning/info/default`) over bus. |
| `web_timeline` | 18.0.1.0.3 | AGPL-3 | **Production/Stable** | vis.js timeline view type for events over time. |

### Other 18.0 OCA/web modules relevant to backend UX (selection from the full branch list)

| Module | License | Note |
|---|---|---|
| `web_quick_start_screen` | AGPL-3 | Configurable start screen of quick-action tiles — closest OCA analog to a "home dashboard / pinned actions" concept. |
| `web_favicon` | AGPL-3 | Custom favicon per database. |
| `web_remember_tree_column_width` | **LGPL-3** | Persists list-view column widths per user. |
| `web_sort_menu` | AGPL-3 | Alphabetical app/menu sorting. |
| `web_m2x_options` | (check manifest; historically LGPL-3) | Tune "Create/Create&Edit" on m2o/m2m. |
| `web_toggle_chatter`, `web_group_expand`, `web_search_with_and`, `web_copy_confirm`, `web_session_auto_close`, `web_touchscreen`, `web_no_bubble`, `web_filter_header_button`, `web_widget_open_tab`, `web_tree_many2one_clickable`, `web_widget_x2many_2d_matrix`, etc. | mixed | All present on 18.0; full list verified. |

Sources: [OCA/web 18.0 branch](https://github.com/OCA/web/tree/18.0), [18.0 README addon table](https://raw.githubusercontent.com/OCA/web/18.0/README.md), per-module manifests e.g. [web_responsive](https://github.com/OCA/web/blob/18.0/web_responsive/__manifest__.py), [web_responsive README](https://github.com/OCA/web/blob/18.0/web_responsive/README.rst), [web_dark_mode README](https://github.com/OCA/web/blob/18.0/web_dark_mode/README.rst), [web_chatter_position README](https://github.com/OCA/web/blob/18.0/web_chatter_position/README.rst).

## 2. MuK 18.0 theme suite — all LGPL-3, actively maintained

Important: the legacy repo `muk-it/muk_web` is **archived-stale** (last push 2023). Current development lives in **`muk-it/odoo-modules`** — branches 15.0–19.0, **pushed 2026-06-11 (today)**, 66 stars / 74 forks / 0 open issues, repo license LGPL-3.0. Every manifest below verified on the 18.0 branch.

| Module | 18.0 version | License | Features |
|---|---|---|---|
| `muk_web_theme` | 18.0.1.2.5 | **LGPL-3** | Flagship Community backend theme: mobile-friendly responsive design, user design preferences; bundles the four modules below (`depends`); explicitly `excludes: web_enterprise`. |
| `muk_web_colors` | 18.0.1.0.6 | **LGPL-3** | Theme **color customizer** (Settings UI); ships separate light (`colors_light.scss`) and dark (`colors_dark.scss` injected into `web.assets_web_dark`) palettes — i.e. dark-mode-aware brand colors. |
| `muk_web_chatter` | 18.0.1.2.4 | **LGPL-3** | Restyled chatter + per-user chatter position preference. |
| `muk_web_dialog` | 18.0.1.0.5 | **LGPL-3** | Dialog fullscreen expand; per-user default dialog state. |
| `muk_web_appsbar` | 18.0.1.1.5 | **LGPL-3** | Vertical **apps sidebar** on the main screen (home-menu-like app list), with dark-mode variables. |
| `muk_web_actions`, `muk_web_utils` | 18.0.1.0.x | **LGPL-3** | Batch server actions/reports from client; shared utilities. |

Sources: [muk-it/odoo-modules](https://github.com/muk-it/odoo-modules) (18.0 branch contents + manifests, e.g. [muk_web_theme/\_\_manifest\_\_.py](https://github.com/muk-it/odoo-modules/blob/18.0/muk_web_theme/__manifest__.py)); legacy [muk-it/muk_web](https://github.com/muk-it/muk_web) (LGPL-3, 108 stars, stale since 2023 — do not use).

## 3. Other reputable free backend themes for 18.0

Checked on the live `CybroOdoo/CybroAddons` 18.0 branch (manifests fetched):

| Theme | 18.0? | License (verified in manifest) | What it proves feasible |
|---|---|---|---|
| Cybrosys `code_backend_theme` | Yes, 18.0.1.0.0 | **LGPL-3** | Left sidebar with app icons + company logo, restyled kanban/list/form, minimalist full-screen look. |
| Cybrosys `jazzy_backend_theme` | Yes, 18.0.1.0.1 | **LGPL-3** | Configurable theme-settings menu, click-revealed sidebar, responsive. |
| Cybrosys `hue_backend_theme` | Yes, 18.0.1.0.0 | **LGPL-3** | Another full restyle (color scheme variants). |
| Cybrosys `dark_mode_backend` | Yes, 18.0.1.0.0 | **AGPL-3** ⚠ | Dark mode for 18 Community — note the license differs from their LGPL themes; treat like OCA AGPL modules. |
| Cybrosys `backend_theme_infinito` (the one with bookmarks, recent apps, dynamic colors, multi-sidebar, dark mode, RTL) | **No — not ported**; 404 on apps store for 18.0 and absent from CybroAddons 18.0 branch (exists ≤16/17) | LGPL-3 (v16) | Proves bookmarks/recent-apps/color-studio features are buildable in an LGPL theme — its 16.0 code is legal reference reading (LGPL), but would need a real port. |
| OpenHRMS backend theme | **No** theme module on `CybroOdoo/OpenHRMS` 18.0 branch | — | Older "openhrms/openworx backend_theme" lineage stopped before 18. |

Sources: [CybroAddons 18.0 manifests](https://github.com/CybroOdoo/CybroAddons/tree/18.0) ([code_backend_theme](https://github.com/CybroOdoo/CybroAddons/blob/18.0/code_backend_theme/__manifest__.py), [jazzy](https://github.com/CybroOdoo/CybroAddons/blob/18.0/jazzy_backend_theme/__manifest__.py), [hue](https://github.com/CybroOdoo/CybroAddons/blob/18.0/hue_backend_theme/__manifest__.py), [dark_mode_backend](https://github.com/CybroOdoo/CybroAddons/blob/18.0/dark_mode_backend/__manifest__.py)), [apps.odoo.com 18.0 listings](https://apps.odoo.com/apps/themes/18.0/code_backend_theme), [backend_theme_infinito 16.0 listing](https://apps.odoo.com/apps/themes/16.0/backend_theme_infinito) (18.0 URL returns 404), [CybroOdoo/OpenHRMS](https://github.com/CybroOdoo/OpenHRMS).

## 4. Licensing ground rules

| Question | Rule | Source |
|---|---|---|
| What does OPL-1 forbid? | Publishing, distributing, sublicensing or selling copies of the Software; **copying source code or material** from it; use without a valid license. Permitted with a valid purchase: use, execute, modify *for yourself*, and write modules that use it as a library. | [Odoo 18 Licenses page (full OPL-1 text)](https://www.odoo.com/documentation/18.0/legal/licenses.html) |
| Is clean-room reimplementation of functionality / a look-alike UI legal? | Yes — copyright protects **expression** (code, SCSS, XML, images, icons), not ideas/functionality. Building "a sidebar + bookmarks + color customizer" from scratch is not a derivative of Spiffy. Practical rules: (a) no Spiffy file may be opened/copied during implementation of the replacement (clean-room discipline); (b) recreate visuals from screenshots/specs, never reuse its image/SCSS assets; (c) uninstall and delete Spiffy from the deployed codebase; (d) don't clone pixel-identical proprietary artwork/logos. OPL-1's prohibition is on copying *material*, not on competing functionality. | OPL-1 text ibid.; general copyright doctrine (idea/expression dichotomy; cf. Google v. Oracle on reimplementation) |
| Combining LGPL-3 OCA modules with our private/LGPL addons | Fine in the same database and even as `depends`. LGPL-3 module changes you redistribute must stay LGPL-3, but separate modules that merely depend on them can be any license (incl. proprietary). This is exactly why Odoo moved the core to LGPL-3 in v9. | [OCA FAQ](https://www.odoo-community.org/resources/faq), [OCA–Odoo license meeting](https://odoo-community.org/blog/news-updates-1/oca-odoo-meeting-on-licenses-21), [Odoo relicensing post](https://www.odoo.com/blog/odoo-news-5/adapting-our-open-source-license-245) |
| Combining **AGPL-3** OCA modules (web_dark_mode, web_dialog_size, web_company_color, …) | Allowed to coexist in the same DB with proprietary/LGPL modules **as long as no proprietary module `depends` on an AGPL one**. Any of our modules that depends on / extends an AGPL module must itself be AGPL-3. Network clause: anyone with access to the running instance may demand the source of the AGPL modules and everything they depend on. OCA/Odoo SA agreed not to pursue end-users who respect the non-dependency rule. | [OCA FAQ](https://www.odoo-community.org/resources/faq), [OCA–Odoo meeting on licenses](https://odoo-community.org/blog/news-updates-1/oca-odoo-meeting-on-licenses-21) |
| Obligations if WE redistribute | LGPL-3 modules (OCA/MuK/Cybrosys + ours): ship/offer their source incl. our modifications, keep notices; our own separate modules may stay private. AGPL-3 modules: full corresponding source offer to users, even SaaS users. We may NOT relicense ported modules (need all contributors' consent). | [OCA FAQ](https://www.odoo-community.org/resources/faq) |
| App-store compatibility | Odoo Apps accepts LGPL, MIT, OPL-like proprietary; enforces dependency-license compatibility checks. | [Odoo 18 Licenses](https://www.odoo.com/documentation/18.0/legal/licenses.html) |

## 5. Flagship features: core vs OCA/MuK vs must-build

| Feature | In core Odoo 18 Community? | Adopt (open source) | Build |
|---|---|---|---|
| **Command palette / global search** | **YES — core since Odoo 15.** Ctrl+K / Cmd+K; prefixes `/` menus, `@` users, `#` channels, `?` knowledge. | — | Optional extension: record-level search (SO/invoices/products) as a custom palette namespace via the core `command` service — small build (LGPL examples exist, e.g. odoo_command_center for 16). |
| **App grid home / drawer** | No (Community has dropdown apps menu; fullscreen home is Enterprise) | **OCA `web_responsive`** (LGPL-3, Production/Stable, fullscreen searchable drawer) and/or **MuK `muk_web_appsbar`** (LGPL-3 sidebar) | Nothing, or light SCSS branding on top. |
| **Dark mode** | **Half-yes:** Community `web` module ships the complete `web.assets_web_dark` bundle (`addons/web/__manifest__.py` line ~348, includes all `*.dark.scss`) — only the user-facing toggle is Enterprise. | OCA `web_dark_mode` (AGPL-3 ⚠) or Cybrosys `dark_mode_backend` (AGPL-3 ⚠); MuK `muk_web_colors`/theme integrate with the dark bundle under LGPL-3 | If avoiding AGPL: a per-user toggle that switches the assets bundle is a ~1-file LGPL build (the hard part — dark SCSS — already exists in core). |
| **Color customizer** | No (Enterprise has limited brand colors via Studio) | **MuK `muk_web_colors`** (LGPL-3, light+dark palettes, settings UI); OCA `web_company_color` (AGPL-3 ⚠, per-company) | Extra presets only. |
| **Bookmarks / pinned favorites** | Partial: core "Add to dashboard" exists only with Enterprise/spreadsheet dashboards; Community has browser-level favorites only | OCA `web_quick_start_screen` (AGPL-3 ⚠) is the closest (configurable quick-action start screen); Infinito's bookmark feature exists but **not ported to 18** | **Must-build** for LGPL purity: small `res.users`-linked model + systray dropdown storing actions/URLs. Low effort. |
| **Font picker** | No | Nothing in OCA/MuK/Cybrosys for 18 | **Must-build**: user preference + injecting a Google-font (or bundled OFL font) CSS variable; trivially small, keep fonts self-hosted offline-safe. |
| Chatter position / styling | No (fixed in core) | OCA `web_chatter_position` (LGPL-3) or MuK `muk_web_chatter` (LGPL-3) | — |
| Fullscreen dialogs | No | MuK `muk_web_dialog` (LGPL-3); OCA `web_dialog_size` (AGPL-3 ⚠) | — |
| Toasts from server, view refresh, sticky widths | No | `web_notify` (LGPL-3), `web_refresher` (AGPL-3 ⚠), `web_remember_tree_column_width` (LGPL-3) | — |

### Recommended adoption stack (all-LGPL-3, no AGPL contamination)
`muk_web_theme` (+ its 4 LGPL deps) **or** `web_responsive`, plus `web_chatter_position`, `web_notify`, `web_remember_tree_column_width`; build in-house (LGPL-3): bookmarks systray, font picker, dark-mode toggle reusing core `web.assets_web_dark`, optional record-search palette namespace. Note `muk_web_theme` and `web_responsive` both reshape the shell — pick one as the base (MuK = sidebar style like Spiffy; OCA = drawer style), they are generally not stacked.

### Key sources
- OCA/web 18.0: https://github.com/OCA/web/tree/18.0 (manifests + READMEs verified per module)
- MuK current repo: https://github.com/muk-it/odoo-modules (18.0 branch; LGPL-3; pushed 2026-06-11)
- Cybrosys: https://github.com/CybroOdoo/CybroAddons/tree/18.0 ; https://apps.odoo.com/apps/themes/18.0/code_backend_theme ; https://apps.odoo.com/apps/themes/16.0/backend_theme_infinito
- Licensing: https://www.odoo.com/documentation/18.0/legal/licenses.html ; https://www.odoo-community.org/resources/faq ; https://odoo-community.org/blog/news-updates-1/oca-odoo-meeting-on-licenses-21 ; https://www.odoo.com/blog/odoo-news-5/adapting-our-open-source-license-245
- Core features: https://www.odoo.com/documentation/18.0/applications/essentials/keyboard_shortcuts.html (Ctrl+K palette) ; https://raw.githubusercontent.com/odoo/odoo/18.0/addons/web/__manifest__.py (`web.assets_web_dark` in Community)


## 4. Architecture research (reference)

# Architecture Best Practices: Reusable In-House Odoo 18 Backend Theme / Design System (2024–2026)

Scope: one theme codebase skinning multiple products — ERP, CRM-like "CMP", public-health "ePHEM" — on Odoo 18 Community.

---

## 1. Addon decomposition: layered addons, not a mega-addon

### How the two reference vendors structure theirs

**MuK (muk-it)** — the de-facto reference for Community backend themes — ships a *suite* of small addons, each with one concern ([muk_web_theme on Odoo Apps](https://apps.odoo.com/apps/themes/18.0/muk_web_theme), [muk_web_colors](https://apps.odoo.com/apps/modules/18.0/muk_web_colors), [muk_web_chatter](https://apps.odoo.com/apps/modules/18.0/muk_web_chatter), [DeepWiki architecture overview](https://deepwiki.com/muk-it/muk_web/2-muk-web-theme), issues at [muk-it/odoo-modules](https://github.com/muk-it/odoo-modules)):

| Addon | Concern |
|---|---|
| `muk_web_theme` | shell: navbar redesign, fullscreen apps menu w/ search, mobile layout, per-company menu background image |
| `muk_web_colors` | brand/primary/context color customization incl. dark-mode variants (extends `res.config.settings` and `web_editor.assets`) |
| `muk_web_appsbar` | left apps sidebar (user-selectable size) |
| `muk_web_chatter` | chatter position/resize UX |
| `muk_web_dialog` | dialog sizing/UX |
| `muk_web_utils` | shared helpers |

Asset layering in MuK (per DeepWiki): `colors.scss` is inserted **after Odoo's primary variables** (`web._assets_primary_variables`), `variables.scss`/`mixins.scss` go into `web._assets_backend_helpers`, and component CSS goes into `web.assets_backend`. Color customizations are "stored in the database and applied through the asset generation system" via the `web_editor.assets` model.

**OCA** splits by concern across the [OCA/web](https://github.com/OCA/web) repo: [`web_responsive`](https://github.com/OCA/web/tree/18.0/web_responsive) (shell ergonomics/responsiveness/hotkeys), [`web_company_color`](https://github.com/OCA/web/tree/18.0/web_company_color) (per-company palette), `web_theme_classic` (form-visibility skin), `web_pwa_customize` (PWA branding). Website themes live in a separate repo ([OCA/website-themes](https://github.com/OCA/website-themes)). Each addon is independently versioned/installable.

### Recommended decomposition for your case (4 layers)

```
theme repo (one git repo, several addons)
├── ds_core            # LAYER 1: design tokens only
│   └── SCSS vars + mixins in web._assets_primary_variables /
│       web._assets_backend_helpers; :root CSS custom properties;
│       NO CSS rules, NO JS. Everything !default so brand packs can win.
├── ds_components      # LAYER 2: component skin
│   └── list/form/kanban/chatter/dialog/buttons styling in
│       web.assets_backend; consumes only tokens from ds_core.
├── ds_shell           # LAYER 3: web-client shell
│   └── navbar/apps-menu/home customizations: t-inherit templates,
│       registry items, the few OWL patches. Depends on ds_components.
└── brand packs        # LAYER 4: one tiny addon per product
    ├── brand_erp      # palette map, logo, fonts, login page, favicon
    ├── brand_cmp
    └── brand_ephem    # each: ~1 SCSS file prepended before ds_core
                       #  defaults + manifest + images. No JS.
```

Brand packs override tokens by being loaded **before** `ds_core`'s `!default` assignments (use `('prepend', ...)` in the bundle), exactly how Odoo's own [SCSS inheritance](https://www.odoo.com/documentation/18.0/developer/reference/user_interface/scss_inheritance.html) and the [dark-mode bundles](https://github.com/odoo/odoo/pull/99755) work.

### Mega-addon vs layered: trade-offs

| | One mega-addon | Layered addons |
|---|---|---|
| Install/ops | simplest (one module) | more modules to manage |
| Per-product reuse | forks or ugly conditionals per product | brand pack = ~50 lines per product |
| Upgrade blast radius | any 18→19 breakage blocks everything | JS-heavy `ds_shell` migrates independently; token core barely changes |
| Uninstall/regression isolation | all-or-nothing (cf. MuK's [colors-uninstall bricking issue](https://github.com/muk-it/odoo-modules/issues/7) and `web._assets_primary_variables` file-not-found outages) | a broken layer can be uninstalled alone |
| Team ownership | merged history | tokens vs shell can evolve separately |

**Recommendation:** layered. Both MuK and OCA converged on it; the only real cost is manifest `depends` discipline. Keep the *number* of layers small (4) — over-splitting (10+ micro-addons) creates dependency churn, which is the lesson of MuK's own upgrade-order issues.

---

## 2. Theming mechanics in Odoo 18

### SCSS variables vs CSS custom properties — use both, at different layers

Odoo's pipeline is SCSS-first with a strict bundle compilation order: `web.dark_mode_variables` → `web._assets_primary_variables` → `web._assets_bootstrap` → `web.assets_backend` ([SCSS coding guidelines wiki](https://github.com/odoo/odoo/wiki/SCSS-coding-guidelines), [SCSS inheritance docs](https://www.odoo.com/documentation/18.0/developer/reference/user_interface/scss_inheritance.html)). Rules:

- **Compile-time identity** (palette, radii, typography scale, Bootstrap derivations) → SCSS variables in `web._assets_primary_variables`. That bundle must contain *only* variables/mixins, no CSS rules. The `!default` flag is the whole override mechanism — first definition wins, so load order = priority.
- Bootstrap overrides go in a file **prepended** to `web._assets_backend_helpers`; always prefer overriding Odoo's own primary variables when one exists, and never override Bootstrap vars that are themselves derived from Odoo vars ([theming how-to](https://www.odoo.com/documentation/18.0/developer/howtos/website_themes/theming.html)).
- Bootstrap variables are *not* visible inside the variables bundles; the documented workaround is `$var: null !default` in the variables file, then assign from Bootstrap context later.
- **Runtime-switchable values** (per-company accent, density, user preferences) → emit them as `:root` / `html` CSS custom properties in `web.assets_backend`, and have components consume `var(--ds-...)`. Odoo core itself defines CSS-variable "contextual adaptations" at this stage.
- Style by classname only (`o_...`/your `ds_...` prefix); never IDs/tags; no SCSS wildcards in manifests (breaks on SaaS) — all from the [SCSS coding guidelines](https://github.com/odoo/odoo/wiki/SCSS-coding-guidelines).
- Custom palettes for website-style pickers: `map-merge($o-color-palettes, (...))` pattern ([Odoo 18 palette guide](https://freewebsnippets.com/blog/odoo-18-custom-color-palette-step-by-step-guide.html)).

### Runtime palette switching — three proven mechanisms

1. **ir.attachment-generated SCSS (OCA `web_company_color` pattern)** — per-company colors stored in a `Serialized` field on `res.company` (`color_navbar_bg`, …); on create/write the module renders an SCSS template, compiles via `ScssStylesheetAsset`, stores the CSS base64 in an `ir.attachment` (mimetype `text/css`) exposed at a synthetic URL `/web_company_color/static/src/scss/custom_colors.<company_id>.gen.scss` inside the bundle, then busts the assets cache ([web_company_color 18.0](https://github.com/OCA/web/tree/18.0/web_company_color); known gotcha: colors silently not applied unless *all* color fields are filled — [OCA/web#2721](https://github.com/OCA/web/issues/2721)).
2. **`web_editor.assets` variable rewriting (MuK pattern)** — `res.config.settings` fields drive an editor that rewrites variable values inside a "customized" copy of the SCSS file stored as an attachment shadowing the original in the bundle; triggers full bundle recompile ([muk_web_colors](https://apps.odoo.com/apps/modules/18.0/muk_web_colors), [DeepWiki](https://deepwiki.com/muk-it/muk_web/2-muk-web-theme)). Powerful but couples you to `web_editor` internals.
3. **`:root` CSS-var injection via QWeb template/controller** — render `<style>:root{--ds-primary: ...}</style>` from `res.company`/settings into `web.layout`. No recompilation, instant, dark-mode-orthogonal; only works for values you exposed as CSS custom properties (not for Bootstrap-derived SCSS math).

**Recommendation:** brand packs = compile-time SCSS (mechanism 0); per-company/per-tenant tweaks = CSS-var injection (3) as primary, ir.attachment SCSS (1) only if you must restyle Bootstrap-derived values. Avoid (2) unless you need an admin color UI — it's the most version-fragile.

### Dark mode (17/18 mechanism)

From the original implementation [odoo/odoo#99755](https://github.com/odoo/odoo/pull/99755): dark mode is a **separate set of bundles**, selected per user via the `color_scheme` cookie (managed by `@web/core/browser/cookie`, switched through the `color_scheme` service / user-menu item). Conventions your theme must follow:

- `*.variables.dark.scss` → loaded in `web.dark_mode_variables` **before** normal variables; wins via `!default` (preferred method).
- `*.dark.scss` → loaded **after** default bundles; contextual CSS-variable overrides with normal selectors.
- Because Bootstrap colors are SCSS, the whole bundle set recompiles per scheme (`web.assets_web_dark` variant).
- Known 18.0 quirks: dark choice not persisted across logout/login without manual refresh ([forum report](https://www.odoo.com/forum/help-1/dark-mode-in-odoo-18-not-persisting-after-login-without-manual-refresh-266741)); no OS `prefers-color-scheme` auto-detect yet ([odoo/odoo#144293](https://github.com/odoo/odoo/issues/144293)). Community edition has no built-in dark switch — MuK colors adds one; if you support dark, ship `ds_core.variables.dark.scss` from day one so tokens stay the single source of truth.

### Per-company branding

Combine: `res.company` fields (logo, favicon, menu background — MuK does per-company app-menu background) + `web_company_color`-style generated CSS or `:root` var injection keyed on `env.company`. Keep brand-pack (product identity) and company branding (tenant identity) as separate axes.

---

## 3. OWL 2 / web client extension: keep the JS surface minimal

### Preferred extension ladder (safest first)

1. **Registries** — systray items (`registry.category("systray").add(..., {sequence})`), `user_menuitems`, services ([Registries docs 18.0](https://www.odoo.com/documentation/18.0/developer/reference/frontend/registries.html)). Replacing built-ins by `remove()` + `add()` works but is flagged as a maintainability smell in community discussions ([example thread](https://www.odoo.com/forum/help-1/override-owl-component-webclient-210110)).
2. **`t-inherit` template extension** — `<t t-inherit="web.NavBar" t-inherit-mode="extension">` with xpath. Use `hasclass('...')` selectors (exact `@class` matches break when core adds classes); `owl="1"` is obsolete since 16. Register XML in the right bundle (`web.assets_backend`) — wrong-bundle registration fails *silently* ([forum example](https://www.odoo.com/forum/help-1/how-to-inherit-owl-template-and-qweb-in-custom-module-v17-0-262735)).
3. **Subclassing with `t-inherit-mode="primary"`** + `static template = "ds_shell.NavBar"` when you need a derived component without touching all consumers.
4. **`patch()` from `@web/core/utils/patch`** — last resort. Patch at module top level (patching after instantiation is documented as dangerous), always call `super`, one patch file per core component so each is individually deletable ([Odoo web framework tutorial](https://www.odoo.com/documentation/16.0/developer/tutorials/master_odoo_web_framework/02_miscellaneous.html), [Coding Dodo history of the patch API](https://codingdodo.com/owl-in-odoo-14-extend-and-patch-existing-owl-components/)).

### What breaks across Odoo minor/major upgrades

- Template DOM structure of NavBar/WebClient shifts every series → every xpath is a liability; keep an inventory file listing each `t-inherit` + the core template hash/version it was written against.
- Module export surface changes (un-exported classes have repeatedly forced rewrites, e.g. `mail` internals).
- API moves themselves (e.g. `patchMixin` → `web.utils.patch` → `@web/core/utils/patch`; `owl="1"` removal) — pin idioms per series branch.
- Odoo's official stance: custom-module compatibility on upgrade is **your** responsibility; DB can't upgrade until your modules support the target version ([Upgrade a customized database](https://www.odoo.com/documentation/18.0/developer/howtos/upgrade_custom_db.html)).

### Testing strategy for theme code

- **Hoot** is the Odoo 18 JS unit framework (QUnit is gone in 18): files end `.test.js`, registered in the `web.assets_unit_tests` bundle (glob allowed), run at `/web/tests`; `@odoo/hoot` for unit tests, `@odoo/hoot-dom` helpers (`click`, `press`, `queryAll`, `waitFor`) usable in tours; `mountWithCleanup`/`mountView` helpers; timers/fetch/localStorage mocked by default ([JS Unit Testing 18.0](https://www.odoo.com/documentation/18.0/sv/developer/reference/frontend/unit_testing.html), [HOOT reference](https://www.odoo.com/documentation/19.0/developer/reference/frontend/unit_testing/hoot.html)).
- **Tours** for integration smoke: `HttpCase.start_tour` exercising "login → open apps menu → open a list view → open a form" under each brand pack; Odoo 18's tour recorder (debug mode) scaffolds them ([Testing Odoo 18.0](https://www.odoo.com/documentation/18.0/developer/reference/backend/testing.html)).
- Theme-specific assertions worth writing: systray item presence/sequence, patched method still calls super, computed `--ds-*` CSS vars on `:root`, bundle compiles in both light/dark and ltr/rtl.

---

## 4. RTL / Arabic

### How Odoo builds the RTL bundle

Odoo compiles bundles normally, then pipes the CSS through the external **`rtlcss`** Node binary, producing mirrored bundles served from `/web/content/<id>-<hash>/rtl/web.assets_backend...` whenever the active language direction is RTL. Requirements/gotchas: `npm install -g rtlcss` must be on PATH for the Odoo process; databases created before rtlcss was installed keep LTR assets until you regenerate the assets bundle from the debug menu; the symptom of a missing binary is an `/rtl/` URL whose contents are not actually flipped ([forum: update existing DB to RTL](https://www.odoo.com/forum/help-1/how-to-update-existing-databse-to-rtl-164764), [RTL in v14 thread](https://www.odoo.com/forum/help-1/odoo-14-rtl-not-working-180374), [Persian/Arabic fonts+RTL thread](https://www.odoo.com/forum/help-1/how-to-rtl-panels-and-change-fonts-for-persian-and-arabic-in-odoo-community-288377)). **Put rtlcss installation in your deployment image and a "regenerate assets" step in your deploy runbook.**

### Logical-properties discipline

- Write all new theme CSS with logical properties: `margin-inline-start`, `padding-inline`, `inset-inline-end`, `border-start-start-radius`, `text-align: start`. They adapt to `dir` automatically and rtlcss has nothing to flip ([rtlstyling.com](https://rtlstyling.com/posts/rtl-styling/), [CSS-Tricks multi-directional layouts](https://css-tricks.com/building-multi-directional-layouts/), [Ahmad Shadeed on logical properties](https://ishadeed.com/article/css-logical-properties/)). Flex/grid are logical by default.
- Don't mix physical and logical in one component; remaining physical cases (`background-position` has no logical form, `transform: translateX`, box-shadow x-offsets) are exactly where you rely on rtlcss or `[dir="rtl"]` overrides.

### rtlcss gotchas (from [RTLCSS control directives](https://rtlcss.com/learn/usage-guide/control-directives/index.html) and real-world bugs)

- `/*rtl:ignore*/` must sit **between declarations/rules**, not inside selectors or values; value directives (`direction: ltr /*rtl:ignore*/;`) are a separate syntax.
- Block form `/*rtl:begin:ignore*/ ... /*rtl:end:ignore*/` must open and close at the same nesting level.
- **Minification/SCSS strips plain comments** — use the `/*!rtl:ignore*/` bang form or SCSS interpolation (`#{"/*rtl:ignore*/"}`) or your directives vanish before rtlcss runs (the WordPress/Gutenberg projects hit both directions of this bug: [wp-calypso#28873](https://github.com/Automattic/wp-calypso/issues/28873), [gutenberg#73205](https://github.com/WordPress/gutenberg/pull/73205)).
- Keep code blocks, phone numbers, LTR-only embeds wrapped in `direction: ltr` + ignore directives.

### Font strategy for bilingual EN/AR backends

- Candidates (all SIL OFL, on Google Fonts, with matched Latin+Arabic in one family — the key property for bilingual UI): **[IBM Plex Sans Arabic](https://fonts.google.com/specimen/IBM+Plex+Sans+Arabic)** (UI-first neutral grotesque, designed by Bold Monday/Wael Morcos — best for data-dense dashboards), **[Cairo](https://fonts.google.com/specimen/Cairo)** (Kufi-geometric, compact vertical metrics, variable font, Arabic+Farsi+Urdu), **[Alexandria](https://fonts.google.com/specimen/Alexandria)** (Montserrat-companion, 9-weight variable — and already your deck/manual font, so it gives print/screen brand consistency). 2025 UX guidance: pair scripts from the *same* family, test Arabic in real UI, mind differing baselines/x-heights, prefer variable fonts ([Arabic fonts for UX 2025](https://ahmedelramlawy.com/10-arabic-fonts-every-ux-designer-should-know-in-2025/), [29LT on Arabic UI typography](https://blog.29lt.com/2025/12/09/advancing-arabic-fonts-and-the-ideal-ui-for-arabic-typography/)).
- Implementation: self-host WOFF2 in `ds_core/static/fonts/`, `@font-face` declarations in a plain CSS file in `web.assets_backend` (never rely on CDN for an on-prem health product); expose `--ds-font-family` / `--ds-font-family-arabic` tokens; scope with `:lang(ar) { font-family: var(--ds-font-family-arabic); }` plus slightly increased `line-height` for Arabic (taller ascenders/dots). System-font fallback stack (`"Segoe UI", Tahoma, "Noto Sans Arabic", sans-serif`) keeps first paint clean; `font-display: swap`.
- Recommendation: **one family for both scripts** (IBM Plex Sans Arabic or Alexandria, weights 400/500/700, variable WOFF2) rather than Inter+Arabic-companion pairing — avoids baseline/weight mismatch entirely.

---

## 5. Accessibility & ergonomics for data-heavy backends

- **WCAG 2.1 AA essentials** (the level regulators target, incl. ADA Title II): text contrast ≥ 4.5:1 against table/background colors — enforce this in the token layer with an SCSS contrast-check function at compile time; visible focus indicators on every interactive element (sort arrows, row links); logical focus order, no keyboard traps; content intact at 200% zoom ([WCAG 2.1 AA checklist](https://www.webability.io/blog/wcag-2-1-aa-the-standard-for-accessible-web-design), [USWDS table accessibility tests](https://designsystem.digital.gov/components/table/accessibility-tests/), [W3C keyboard-accessible guideline](https://www.w3.org/WAI/WCAG22/Understanding/keyboard-accessible.html)).
- **Density modes**: follow [Cloudscape's model](https://cloudscape.design/foundation/visual-foundation/content-density/) — *comfortable default, compact opt-in, user-switchable, persisted*. Material's caveat applies: high density fails touch-target minimums, so it must be opt-in ([Material density guidance](https://m2.material.io/design/layout/applying-density.html)). Implement as a `<html data-ds-density="compact">` attribute driving CSS-var overrides of row-height/padding tokens (~48–56px standard rows, 40–44px compact per [enterprise table guidelines](https://medium.com/@calee607/data-table-design-guidelines-for-enterprise-applications-40f7ef0e0186)); store in user settings (`res.users` field + cookie like Odoo's `color_scheme`). MuK's per-user sidebar-size and chatter-position preferences are the precedent inside Odoo.
- **Keyboard**: don't fight Odoo's hotkey service — extend it. OCA `web_responsive` is the model: it remaps to `Alt+Shift+NUM` to avoid Firefox conflicts and adds one-hand-reachable mnemonics ([web_responsive 18.0](https://github.com/OCA/web/tree/18.0/web_responsive)). For any custom grid/kanban widgets follow ARIA APG grid pattern (arrow keys, Home/End, `aria-sort`) ([MUI X a11y reference](https://mui.com/x/react-data-grid/accessibility/)).
- **Reduced motion**: wrap all theme transitions (menu slide-ins, chatter resize, skeletons) in `@media (prefers-reduced-motion: reduce)` — reduce/replace large movement, keep opacity fades ([W3C technique C39](https://www.w3.org/WAI/WCAG22/Techniques/css/C39), [practical guide](https://blog.pope.tech/2025/12/08/design-accessible-animation-and-movement/)). Cheap global rule in `ds_core`: drop animation/transition durations to ~1ms under the query, plus an optional in-app toggle.

---

## 6. Versioning & distribution across the three products

### Repo layout

One shared git repo (`odoo-ds`), OCA-style: branch per Odoo series (`18.0`, later `19.0`), multiple addons at repo root, optional `setup/<addon>/` packaging dirs:

```
odoo-ds/  (branch 18.0)
├── ds_core/  ds_components/  ds_shell/
├── brand_erp/  brand_cmp/  brand_ephem/
├── setup/ or pyproject per addon (whool)
└── .pre-commit-config.yaml, .github/workflows/ci.yml
```

Brand packs can live here (simplest; one CI) or in each product's repo (if products have separate release cadences). Start co-located; split a brand pack out only when its release cycle demonstrably diverges.

### Versioning

OCA convention: manifest `version = "18.0.x.y.z"` — series prefix + semantic `breaking.feature.fix` per addon; first 18.0 release is `18.0.1.0.0` ([OCA CONTRIBUTING](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst), [versioning rationale thread](https://odoo-community.org/groups/contributors-15/oca-contributors-24064)). Bump `x` for token renames/visual breaking changes, `y` for new components/tokens, `z` for fixes. Tag the repo (`v18.0-2026.06.1` style or per-addon tags) so deployments pin exact states.

### Consumption by each deployment — submodule vs subtree vs pip

| Method | Verdict for this case |
|---|---|
| **git submodule** | **Recommended.** Officially supported on Odoo.sh (deploy keys for private repos, `.`-prefix + symlink trick to hand-pick addons); pins exact commit per product; standard in the Odoo world ([Odoo.sh submodules docs 18.0](https://www.odoo.com/documentation/18.0/administration/odoo_sh/advanced/submodules.html)). Cost: team git training. |
| git subtree | Copies code into each product repo → propagating a theme fix to 3 products is manual; only attractive if a product needs to fork-and-diverge. |
| pip (`odoo-addon-*` wheels) | Cleanest dependency resolution; tooling is **[whool](https://github.com/acsone/setuptools-odoo)** (per-addon) / hatch-odoo for 17+, since setuptools-odoo is deprecated and only supports ≤16 ([setuptools-odoo README](https://github.com/acsone/setuptools-odoo), [OCA 18.0 tooling issue](https://github.com/OCA/maintainer-tools/issues/628)). Adopt when you have a private package index; until then submodules win. |
| [git-aggregator](https://github.com/acsone/git-aggregator) / gitman | Use if deployments already mix OCA branches + pending PRs into a consolidated addons dir (`repos.yaml` + `gitaggregate -c repos.yaml -p`). |

### CI smoke tests (per push to `18.0`)

1. Lint: `pre-commit` with pylint-odoo + stylelint (enforce logical-properties / no physical margin-left in theme SCSS via stylelint rule).
2. Install matrix: spin Odoo 18 container, `-i ds_core,ds_components,ds_shell,brand_X --stop-after-init` for each of the 3 brand packs (catches bundle-compilation failures — the classic theme outage mode, cf. MuK's `_assets_primary_variables` file-not-found incident).
3. Hoot unit tests via `/web/tests` headless + Python `HttpCase` tours per brand (login → apps menu → list → form), once in `ar` language to force the rtl bundle (requires rtlcss in the CI image), once with dark cookie if you ship dark.
4. Uninstall test for each addon (themes are notorious for bricking on uninstall).
5. Optional: screenshot diff of login + list view per brand/lang as artifact.

---

## Bottom-line recommendations

1. Four-layer addon stack (`ds_core` tokens → `ds_components` → `ds_shell` → thin `brand_*` packs); no mega-addon.
2. SCSS `!default` tokens in `web._assets_primary_variables` for identity; CSS custom properties for anything runtime/per-company; dark-mode `*.variables.dark.scss` from day one.
3. Per-company branding via `:root` var injection or the `web_company_color` ir.attachment pattern — not by forking SCSS per tenant.
4. JS minimalism: registries > `t-inherit`+`hasclass()` > primary-mode subclass > `patch()`; one patch per file; inventory of every core touchpoint; Hoot + tours in CI.
5. RTL: rtlcss in every image, logical properties everywhere, `/*!rtl:ignore*/` (bang form) for intentional physical CSS, one OFL Arabic+Latin family (IBM Plex Sans Arabic or Alexandria) self-hosted with `:lang(ar)` scoping.
6. A11y: contrast-checked tokens, comfortable-default/compact-opt-in density attribute, visible focus, `prefers-reduced-motion` global rule.
7. One repo, branch-per-series, `18.0.x.y.z` per addon, consumed via pinned git submodules; CI = install matrix × brands × (ltr/rtl) + Hoot + tour smoke + uninstall test.

## Sources

- https://www.odoo.com/documentation/18.0/developer/reference/user_interface/scss_inheritance.html
- https://www.odoo.com/documentation/18.0/developer/howtos/website_themes/theming.html
- https://github.com/odoo/odoo/wiki/SCSS-coding-guidelines
- https://freewebsnippets.com/blog/odoo-18-custom-color-palette-step-by-step-guide.html
- https://github.com/odoo/odoo/pull/99755 (dark mode implementation)
- https://github.com/odoo/odoo/issues/144293
- https://www.odoo.com/forum/help-1/dark-mode-in-odoo-18-not-persisting-after-login-without-manual-refresh-266741
- https://apps.odoo.com/apps/themes/18.0/muk_web_theme , https://apps.odoo.com/apps/modules/18.0/muk_web_colors , https://apps.odoo.com/apps/modules/18.0/muk_web_chatter
- https://deepwiki.com/muk-it/muk_web/2-muk-web-theme , https://github.com/muk-it/odoo-modules/issues/7
- https://github.com/OCA/web , https://github.com/OCA/web/tree/18.0/web_responsive , https://github.com/OCA/web/tree/18.0/web_company_color , https://github.com/OCA/web/issues/2721 , https://github.com/OCA/website-themes
- https://www.odoo.com/documentation/18.0/developer/reference/frontend/registries.html
- https://www.odoo.com/documentation/16.0/developer/tutorials/master_odoo_web_framework/02_miscellaneous.html
- https://codingdodo.com/owl-in-odoo-14-extend-and-patch-existing-owl-components/
- https://www.odoo.com/documentation/18.0/developer/howtos/upgrade_custom_db.html
- https://www.odoo.com/documentation/18.0/sv/developer/reference/frontend/unit_testing.html , https://www.odoo.com/documentation/19.0/developer/reference/frontend/unit_testing/hoot.html , https://www.odoo.com/documentation/18.0/developer/reference/backend/testing.html
- https://www.odoo.com/forum/help-1/how-to-update-existing-databse-to-rtl-164764 , https://www.odoo.com/forum/help-1/odoo-14-rtl-not-working-180374
- https://rtlcss.com/learn/usage-guide/control-directives/index.html , https://github.com/Automattic/wp-calypso/issues/28873 , https://github.com/WordPress/gutenberg/pull/73205
- https://rtlstyling.com/posts/rtl-styling/ , https://ishadeed.com/article/css-logical-properties/ , https://css-tricks.com/building-multi-directional-layouts/
- https://fonts.google.com/specimen/IBM+Plex+Sans+Arabic , https://fonts.google.com/specimen/Cairo , https://fonts.google.com/specimen/Alexandria
- https://ahmedelramlawy.com/10-arabic-fonts-every-ux-designer-should-know-in-2025/ , https://blog.29lt.com/2025/12/09/advancing-arabic-fonts-and-the-ideal-ui-for-arabic-typography/
- https://designsystem.digital.gov/components/table/accessibility-tests/ , https://www.w3.org/WAI/WCAG22/Understanding/keyboard-accessible.html , https://www.webability.io/blog/wcag-2-1-aa-the-standard-for-accessible-web-design
- https://cloudscape.design/foundation/visual-foundation/content-density/ , https://m2.material.io/design/layout/applying-density.html , https://mui.com/x/react-data-grid/accessibility/ , https://medium.com/@calee607/data-table-design-guidelines-for-enterprise-applications-40f7ef0e0186
- https://www.w3.org/WAI/WCAG22/Techniques/css/C39 , https://blog.pope.tech/2025/12/08/design-accessible-animation-and-movement/
- https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst , https://odoo-community.org/groups/contributors-15/oca-contributors-24064
- https://github.com/acsone/setuptools-odoo , https://github.com/acsone/git-aggregator , https://github.com/OCA/maintainer-tools/issues/628
- https://www.odoo.com/documentation/18.0/administration/odoo_sh/advanced/submodules.html
