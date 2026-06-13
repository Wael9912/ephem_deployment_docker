# -*- coding: utf-8 -*-
"""Verify the customizable app-launcher (9-dots) background (nile_config).

Proves:
  A. The drawer no longer uses web_responsive's hardcoded lavender / SVG overlay.
  B. With "follow palette" it tracks the company palette (teal vs plum differ).
  C. A custom color set via the Theme dialog persists and recolors the drawer.
  D. App labels stay readable (dark text on the light tint).
  E. The Google-Fonts help text now renders in Arabic (translation fix).

Non-destructive: restores the company's original appmenu bg / palette and the
admin's language at the end.
Usage: python3 scripts/qa_test_appmenu_bg.py [db]
"""
import os
import re
import sys
import xmlrpc.client
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8069"
DB = sys.argv[1] if len(sys.argv) > 1 else "erpmedsupply"
USER = PWD = "admin"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "theme-audit", "qa", "appmenu")
os.makedirs(OUT, exist_ok=True)

failures = []


def check(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name + (f" ({detail})" if detail else ""))
    if not cond:
        failures.append(f"{name}: {detail}")


# --- xmlrpc handles + original state (restored at the end) -------------------
common = xmlrpc.client.ServerProxy(f"{BASE}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PWD, {})
models = xmlrpc.client.ServerProxy(f"{BASE}/xmlrpc/2/object")


def kw(model, method, *args):
    return models.execute_kw(DB, uid, PWD, model, method, *args)


cid = kw("res.users", "read", [[uid], ["company_id"]])[0]["company_id"][0]
orig = kw("res.company", "read",
          [[cid], ["nile_palette_preset", "nile_color_primary", "nile_appmenu_bg"]])[0]
orig_lang = kw("res.users", "read", [[uid], ["lang"]])[0]["lang"]
orig_dark = kw("res.users", "read", [[uid], ["nile_dark_mode"]])[0]["nile_dark_mode"]
kw("res.users", "write", [[uid], {"lang": "en_US"}])


def set_company(vals):
    kw("res.company", "write", [[cid], vals])


def login(page, lang_db=DB):
    page.goto(f"{BASE}/web/login?db={lang_db}", timeout=30000)
    if page.locator("input[name=login]").count():
        page.fill("input[name=login]", USER)
        page.fill("input[name=password]", PWD)
        page.click("button[type=submit]")
    page.wait_for_selector(".o_main_navbar", timeout=20000)
    page.wait_for_timeout(1200)


def open_launcher(page):
    page.locator(".o_grid_apps_menu__button").first.click()
    page.wait_for_selector(".app-menu-container", timeout=8000)
    page.wait_for_timeout(500)


def drawer_bg(page):
    """Resolved background-image (the gradient) of the open drawer."""
    return page.eval_on_selector(
        ".app-menu-container",
        "el => getComputedStyle(el).backgroundImage",
    )


def rgbs(s):
    return re.findall(r"rgba?\(([^)]+)\)", s or "")


def parse_color(tok):
    """rgb(...)/rgba(...) or Chromium's color(srgb r g b) -> [r,g,b] 0-255."""
    m = re.match(r"rgba?\(([^)]+)\)", tok or "")
    if m:
        return [float(x) for x in [p.strip() for p in m.group(1).split(",")][:3]]
    m = re.match(r"color\(srgb\s+([^)]+)\)", tok or "")
    if m:
        return [float(x) * 255 for x in m.group(1).split()[:3]]
    return None


def luminance(rgb):
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def first_color(grad):
    m = re.search(r"(rgba?\([^)]*\)|color\(srgb[^)]*\))", grad or "")
    return parse_color(m.group(1)) if m else None


print(f"\n== app-menu background verification on {DB} ==")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    # ---- A + B(1): follow palette = teal (default brand) --------------------
    set_company({"nile_palette_preset": "teal", "nile_appmenu_bg": False})
    login(page)
    open_launcher(page)
    bg_teal = drawer_bg(page)
    page.screenshot(path=os.path.join(OUT, "appmenu_follow_teal.png"))
    check("A: gradient replaces web_responsive default",
          "gradient" in bg_teal and "233, 230, 249" not in bg_teal
          and ".svg" not in bg_teal and "home-menu" not in bg_teal,
          bg_teal[:80])

    # label readability — theme-agnostic: each apps_menu theme keeps its own
    # label-color contract (milk=dark on a light tint, community=white on a bold
    # wash), so assert a healthy luminance gap between label and drawer instead
    # of a fixed color.
    lbl = page.eval_on_selector(
        ".o-app-menu-item__name",
        "el => getComputedStyle(el).color") if page.locator(".o-app-menu-item__name").count() else "none"
    bg_top = first_color(bg_teal)
    lab = parse_color(lbl)
    readable = bool(bg_top) and bool(lab) and abs(luminance(bg_top) - luminance(lab)) > 0.35
    check("D: app labels readable on the drawer (luminance gap)", readable,
          f"label={lbl} bg_top={bg_top}")

    # ---- B(2): follow palette = plum → drawer hue must change ---------------
    set_company({"nile_palette_preset": "plum", "nile_appmenu_bg": False})
    login(page)
    open_launcher(page)
    bg_plum = drawer_bg(page)
    page.screenshot(path=os.path.join(OUT, "appmenu_follow_plum.png"))
    check("B: drawer follows the palette (teal != plum)",
          bg_plum != bg_teal and "gradient" in bg_plum, bg_plum[:80])

    # ---- C: custom color via the Theme dialog (UI + persistence) ------------
    set_company({"nile_palette_preset": "teal", "nile_appmenu_bg": False})
    login(page)
    page.locator(".o_nile_theme_systray").click()
    page.wait_for_selector(".o_nile_theme_dialog", timeout=8000)
    page.get_by_role("tab", name="Brand").click()
    page.wait_for_timeout(300)
    has_section = page.get_by_text("App Menu Background").count() > 0
    check("C1: 'App Menu Background' control on Brand tab", has_section)
    # switch to Custom → the inline HSV picker appears
    page.get_by_role("button", name="Custom").last.click()
    page.wait_for_timeout(300)
    pickers = page.locator(".o_nile_theme_dialog .o_nile_color_picker")
    check("C2: Custom reveals the color picker", pickers.count() >= 1)
    # type a vivid crimson into the app-menu picker's hex field, then Save
    pickers.last.locator(".o_nile_hex_input").fill("#BE123C")
    pickers.last.locator(".o_nile_hex_input").dispatch_event("input")
    page.wait_for_timeout(300)
    page.get_by_role("button", name="Save").click()
    page.wait_for_selector(".o_main_navbar", timeout=20000)
    page.wait_for_timeout(1200)
    persisted = kw("res.company", "read", [[cid], ["nile_appmenu_bg"]])[0]["nile_appmenu_bg"]
    check("C3: custom color persisted", persisted == "#BE123C", str(persisted))
    open_launcher(page)
    bg_custom = drawer_bg(page)
    page.screenshot(path=os.path.join(OUT, "appmenu_custom_crimson.png"))
    # crimson tint: the top stop should be red-dominant (r > g and r > b)
    triples = [t.split(",") for t in rgbs(bg_custom)]
    red_dom = any(int(t[0]) > int(t[1]) and int(t[0]) > int(t[2]) for t in triples if len(t) >= 3)
    check("C4: drawer shows the custom crimson tint", red_dom and bg_custom != bg_teal, bg_custom[:80])

    # ---- E: Arabic help text (translation fix) ------------------------------
    kw("res.users", "write", [[uid], {"lang": "ar_001"}])
    login(page)
    page.locator(".o_nile_theme_systray").click()
    page.wait_for_selector(".o_nile_theme_dialog", timeout=8000)
    # Typography tab — Arabic label is "الخطوط"
    page.get_by_role("tab", name="الخطوط").click()
    page.wait_for_timeout(300)
    help_txt = page.locator(".o_nile_theme_dialog .form-text").last.inner_text()
    is_arabic = bool(re.search(r"[؀-ۿ]", help_txt)) and "Paste a Google" not in help_txt
    check("E: Google-Fonts help text renders Arabic", is_arabic, help_txt[:60])

    # ---- F: dark mode wins over a custom app-menu color ---------------------
    # dark.scss sets --app-menu-background DIRECTLY on .app-menu-container; that
    # direct value must beat our inherited ancestor rule so the drawer stays a
    # neutral dark surface (NOT the crimson custom color) in dark mode.
    kw("res.users", "write", [[uid], {"lang": "en_US", "nile_dark_mode": True}])
    set_company({"nile_appmenu_bg": "#BE123C"})  # vivid custom color still set
    dark_ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    dark_ctx.add_cookies([{"name": "color_scheme", "value": "dark", "url": BASE}])
    dpage = dark_ctx.new_page()
    login(dpage)
    open_launcher(dpage)
    bg_dark = drawer_bg(dpage)
    # dark.scss uses a SOLID surface color, so it lands in background-color
    # (background-image is "none") — fall back to it.
    bg_dark_col = dpage.eval_on_selector(
        ".app-menu-container", "el => getComputedStyle(el).backgroundColor")
    dpage.screenshot(path=os.path.join(OUT, "appmenu_dark_neutral.png"))
    top = first_color(bg_dark) or parse_color(bg_dark_col)
    red_dom = bool(top) and top[0] > top[1] and top[0] > top[2]
    is_neutral = bool(top) and luminance(top) < 0.12 and not red_dom
    check("F: dark mode stays neutral (custom color suppressed)", is_neutral,
          f"bg_top={top}")
    dark_ctx.close()

    browser.close()

# --- restore -----------------------------------------------------------------
set_company({
    "nile_palette_preset": orig["nile_palette_preset"],
    "nile_color_primary": orig["nile_color_primary"] or False,
    "nile_appmenu_bg": orig["nile_appmenu_bg"] or False,
})
kw("res.users", "write", [[uid], {"lang": orig_lang, "nile_dark_mode": orig_dark}])
print(f"\nrestored: palette={orig['nile_palette_preset']} appmenu_bg={orig['nile_appmenu_bg']} "
      f"lang={orig_lang} dark={orig_dark}")

print(f"\nscreenshots -> {OUT}")
if failures:
    print(f"\n{len(failures)} FAILURE(S):")
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("\nALL CHECKS PASSED")
