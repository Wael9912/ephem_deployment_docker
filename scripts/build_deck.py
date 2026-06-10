# -*- coding: utf-8 -*-
"""
Build a 16:9 sales / live-demo deck (HTML -> PDF) for the medical-supply ERP.

Every figure on the slides is REAL data from the running `erpmedsupply`
demo (see docs/manual/_ground_truth/demo.json) and every screenshot is a real
capture from the themed Odoo UI (docs/manual/img/en/*). The deck is presenter-
driven: capability slides carry a "SHOW LIVE" cue telling the presenter exactly
what to open in the system.

Output:  docs/deck/Medical-Supply_ERP_Demo_Deck.html  (self-contained)
Render to PDF with WeasyPrint (run inside the odoo container, which has it):
    bash scripts/build_deck_pdf.sh
"""
import base64
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "docs", "manual", "img", "en")
IMG_AR = os.path.join(ROOT, "docs", "manual", "img", "ar")
FONTS = os.path.join(ROOT, "scripts", "fonts")
OUT_DIR = os.path.join(ROOT, "docs", "deck")
os.makedirs(OUT_DIR, exist_ok=True)

DATE = "10 June 2026"

# ---------------------------------------------------------------- palette ----
INK      = "#0B2027"   # headline / near-black teal
INK2     = "#13323B"
TEAL     = "#0E7C7B"   # primary brand
TEAL_DK  = "#0A5C5B"
TEAL_LT  = "#E7F4F3"
AMBER    = "#C77E18"   # pain / "show live"
AMBER_DK = "#9A5E0E"
AMBER_LT = "#FBF1DF"
RED      = "#B23A2E"
RED_LT   = "#FBECEA"
INDIGO   = "#3C4FB0"   # money / currency
VIOLET   = "#6D4AA6"
SLATE    = "#3A4A57"
GRAY     = "#4A5A66"   # body text
GRAY_LT  = "#8A99A4"
BORDER   = "#E2E8EA"
BG_SOFT  = "#F5F8F8"

# ------------------------------------------------------------------ assets ----
def _b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")

def img_uri(name, ar=False):
    base = IMG_AR if ar else IMG
    return "data:image/png;base64," + _b64(os.path.join(base, name))

def png_size(name, ar=False):
    import struct
    base = IMG_AR if ar else IMG
    with open(os.path.join(base, name), "rb") as f:
        head = f.read(24)
    w, h = struct.unpack(">II", head[16:24])
    return w, h

def disp_h(name, w, ar=False):
    iw, ih = png_size(name, ar)
    return int(round(w * ih / iw))

def font_face():
    reg = _b64(os.path.join(FONTS, "Alexandria-Regular.ttf"))
    bld = _b64(os.path.join(FONTS, "Alexandria-Bold.ttf"))
    return (
        "@font-face{font-family:'Alexandria';font-weight:400;font-style:normal;"
        "src:url(data:font/ttf;base64,%s) format('truetype');}"
        "@font-face{font-family:'Alexandria';font-weight:700;font-style:normal;"
        "src:url(data:font/ttf;base64,%s) format('truetype');}" % (reg, bld)
    )

# ------------------------------------------------------------------- icons ----
_ICON = {
 'database':'<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
 'box':'<path d="M12 2 3 7v10l9 5 9-5V7z"/><path d="M3 7l9 5 9-5"/><path d="M12 12v10"/>',
 'expiry':'<rect x="3" y="4" width="18" height="17" rx="2"/><path d="M3 9h18M8 2v4M16 2v4"/><path d="M12 13v3l2 1"/>',
 'alert':'<path d="M12 3 2 20h20z"/><path d="M12 10v4M12 17v.4"/>',
 'cash':'<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="3"/>',
 'lock':'<rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
 'snow':'<path d="M12 2v20M3.7 7l16.6 10M20.3 7 3.7 17"/><path d="M9 4l3-2 3 2M9 20l3 2 3-2"/>',
 'refresh':'<path d="M3 12a9 9 0 0 1 15-6.7L21 8M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-15 6.7L3 16M3 21v-5h5"/>',
 'warehouse':'<path d="M3 21V9l9-5 9 5v12"/><path d="M7 21v-7h10v7"/>',
 'exchange':'<path d="M3 8h14l-3.5-3.5M21 16H7l3.5 3.5"/>',
 'doc':'<path d="M6 2h8l4 4v16H6z"/><path d="M14 2v4h4"/><path d="M9 13h6M9 17h5"/>',
 'chart':'<path d="M4 20V4M4 20h16"/><rect x="7" y="11" width="3" height="6"/><rect x="12" y="7" width="3" height="10"/><rect x="17" y="13" width="3" height="4"/>',
 'users':'<circle cx="9" cy="8" r="3"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><path d="M16 5.2a3 3 0 0 1 0 5.6M21 20c0-2.4-1.4-4.5-3.5-5.4"/>',
 'globe':'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',
 'layers':'<path d="M12 3 2 8l10 5 10-5z"/><path d="M2 13l10 5 10-5M2 18l10 5 10-5"/>',
 'upload':'<path d="M12 16V4M7 9l5-5 5 5"/><path d="M4 20h16"/>',
 'book':'<path d="M4 4h9a3 3 0 0 1 3 3v13a3 3 0 0 0-3-3H4z"/><path d="M20 4h-2a3 3 0 0 0-3 3v13a3 3 0 0 1 3-3h2z"/>',
 'cloud':'<path d="M7 18a4 4 0 0 1 0-8 5 5 0 0 1 9.6-1.5A4 4 0 0 1 17 18z"/>',
 'check':'<path d="M5 13l4 4L19 7"/>',
 'x':'<path d="M6 6l12 12M18 6 6 18"/>',
 'time':'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
 'tag':'<path d="M3 12V4h8l10 10-8 8L3 12z"/><circle cx="7.5" cy="7.5" r="1.4"/>',
 'play':'<path d="M7 4l13 8-13 8z"/>',
 'flow':'<rect x="3" y="9" width="6" height="6" rx="1"/><rect x="15" y="9" width="6" height="6" rx="1"/><path d="M9 12h6"/>',
 'pin':'<path d="M12 22s7-6.5 7-12A7 7 0 0 0 5 10c0 5.5 7 12 7 12z"/><circle cx="12" cy="10" r="2.4"/>',
}
def icon(name, color=TEAL, size=22, sw=1.8):
    return ('<svg width="%d" height="%d" viewBox="0 0 24 24" fill="none" stroke="%s" '
            'stroke-width="%s" stroke-linecap="round" stroke-linejoin="round">%s</svg>'
            % (size, size, color, sw, _ICON[name]))

# ---------------------------------------------------------------- helpers ----
def abs_box(x, y, w=None, h=None, extra=""):
    s = "position:absolute;left:%dpx;top:%dpx;" % (x, y)
    if w is not None: s += "width:%dpx;" % w
    if h is not None: s += "height:%dpx;" % h
    return s + extra

def kicker(text, color=TEAL):
    return ('<div style="%sfont-size:13px;font-weight:700;letter-spacing:2.5px;'
            'color:%s;text-transform:uppercase;">%s</div>'
            % (abs_box(64, 50), color, text))

def title(text, color=INK, size=42, top=80, width=1152):
    return ('<div style="%sfont-size:%dpx;font-weight:700;line-height:1.08;'
            'color:%s;">%s</div>' % (abs_box(64, top, width), size, color, text))

def accent_bar(color=TEAL):
    return '<div style="%sbackground:%s;"></div>' % (abs_box(0, 0, 12, 720), color)

def footer(p, accent=TEAL):
    line = '<div style="%sborder-top:1px solid %s;"></div>' % (abs_box(64, 678, 1152), BORDER)
    left = ('<div style="%sfont-size:11px;color:%s;letter-spacing:.4px;">'
            'Medical-Supply Distribution ERP'
            '<span style="color:%s;"> &nbsp;·&nbsp; Odoo 18 Community + OCA</span></div>'
            % (abs_box(64, 690), GRAY, GRAY_LT))
    mid = ('<div style="%stext-align:center;font-size:11px;color:%s;">'
           'Confidential · Live demonstration · %s</div>'
           % (abs_box(440, 690, 400), GRAY_LT, DATE))
    rt = ('<div style="%stext-align:right;font-size:11px;font-weight:700;color:%s;">%s / %s</div>'
          % (abs_box(1016, 690, 200), accent, p, "%%T%%"))
    return line + left + mid + rt

def live_cue(text, accent=AMBER):
    return ('<div style="%sbackground:%s;border-radius:10px;padding:0 18px;'
            'display:flex;align-items:center;border:1px solid %s33;">'
            '<span style="display:inline-flex;align-items:center;justify-content:center;'
            'width:24px;height:24px;border-radius:6px;background:%s;margin-right:12px;">%s</span>'
            '<span style="font-size:13px;font-weight:700;color:%s;letter-spacing:.4px;'
            'text-transform:uppercase;margin-right:10px;">Show live</span>'
            '<span style="font-size:13.5px;color:%s;">%s</span></div>'
            % (abs_box(64, 612, 1152, 48), AMBER_LT, accent, accent,
               icon('play', '#FFFFFF', 12, 0), AMBER_DK, INK2, text))

def chips(items, x=64, y=560, width=478, accent=TEAL):
    inner = ""
    for it in items:
        inner += ('<span style="display:inline-block;margin-right:9px;margin-bottom:8px;'
                  'padding:6px 13px;border-radius:20px;background:%s;color:%s;'
                  'font-size:12.5px;font-weight:700;border:1px solid %s33;">%s</span>'
                  % (TEAL_LT, TEAL_DK, accent, it))
    return '<div style="%s">%s</div>' % (abs_box(x, y, width), inner)

def shot(name, x, y, w, ar=False, caption=None):
    """A framed screenshot (browser-card look)."""
    html = ('<div style="%sborder:1px solid %s;border-radius:12px;overflow:hidden;'
            'box-shadow:0 18px 40px -18px rgba(11,32,39,.45);background:#fff;">'
            '<div style="height:26px;background:%s;display:flex;align-items:center;padding:0 12px;">'
            '<span style="width:8px;height:8px;border-radius:50%%;background:#E76A5E;display:inline-block;margin-right:6px;"></span>'
            '<span style="width:8px;height:8px;border-radius:50%%;background:#E6B95C;display:inline-block;margin-right:6px;"></span>'
            '<span style="width:8px;height:8px;border-radius:50%%;background:#7FC08A;display:inline-block;"></span></div>'
            '<img src="%s" style="display:block;width:%dpx;height:auto;"/></div>'
            % (abs_box(x, y, w), BORDER, BG_SOFT, img_uri(name, ar), w))
    if caption:
        html += ('<div style="%stext-align:center;font-size:12px;color:%s;font-weight:700;">%s</div>'
                 % (abs_box(x, y - 1, w), GRAY, caption))  # placeholder, real caption below
    return html

def caption(text, x, y, w):
    if not text:
        return ""
    return ('<div style="%stext-align:center;font-size:12px;color:%s;">%s</div>'
            % (abs_box(x, y, w), GRAY, text))

def bullet_list(items, x=64, y=200, w=470, accent=TEAL, gap=20, fs=16):
    html = ""
    cy = y
    for it in items:
        html += ('<div style="%s">'
                 '<div style="position:absolute;left:0;top:2px;width:26px;height:26px;border-radius:7px;'
                 'background:%s;display:flex;align-items:center;justify-content:center;">%s</div>'
                 '<div style="margin-left:40px;font-size:%dpx;line-height:1.42;color:%s;">%s</div>'
                 '</div>' % (abs_box(x, cy, w), TEAL_LT, icon('check', TEAL, 16, 2.4), fs, GRAY, it))
        # estimate height
        approx_lines = max(1, (len(_strip(it)) // 46) + 1)
        cy += 16 + approx_lines * int(fs * 1.42)
        cy = max(cy, _y_unused := cy)  # noop keeps lint calm
        cy = y + (cy - y)
    return html

def _strip(s):
    out, skip = [], False
    for ch in s:
        if ch == '<': skip = True
        elif ch == '>': skip = False
        elif not skip: out.append(ch)
    return "".join(out)

# A more predictable bullet layout: fixed slot height per item.
def bullets(items, x=64, y=198, w=478, slot=66, accent=TEAL, fs=15.5):
    html = ""
    for i, it in enumerate(items):
        cy = y + i * slot
        html += ('<div style="%s">'
                 '<div style="position:absolute;left:0;top:2px;width:28px;height:28px;border-radius:8px;'
                 'background:%s;display:flex;align-items:center;justify-content:center;">%s</div>'
                 '<div style="margin-left:42px;font-size:%spx;line-height:1.4;color:%s;">%s</div>'
                 '</div>' % (abs_box(x, cy, w), TEAL_LT, icon('check', accent, 16, 2.4), fs, GRAY, it))
    return html

# ------------------------------------------------------------------ slides ----
SLIDES = []
def add(html, accent=TEAL, full=False, p=True):
    """Wrap slide body in canvas. full=dark full-bleed (no white bg)."""
    bg = "background:%s;" % INK if full else "background:#FFFFFF;"
    foot = "" if not p else footer(len(SLIDES) + 1, accent)
    SLIDES.append('<section class="slide" style="%s">%s%s</section>'
                  % (bg, html, foot))

# ---- 1. COVER ----
def cover():
    mark = ('<div style="%sdisplay:flex;align-items:center;">'
            '<div style="width:54px;height:54px;border-radius:14px;background:%s;'
            'display:flex;align-items:center;justify-content:center;box-shadow:0 8px 22px -8px %s;">'
            '<svg width="30" height="30" viewBox="0 0 24 24"><path d="M10 3h4v7h7v4h-7v7h-4v-7H3v-4h7z" fill="#fff"/></svg></div>'
            '<div style="margin-left:16px;color:#fff;">'
            '<div style="font-size:21px;font-weight:700;letter-spacing:.3px;">Medical-Supply ERP</div>'
            '<div style="font-size:12.5px;color:#7FB7B4;letter-spacing:1.5px;">DISTRIBUTION MANAGEMENT PLATFORM</div>'
            '</div></div>' % (abs_box(80, 70), TEAL, TEAL))
    eyebrow = ('<div style="%sfont-size:14px;font-weight:700;letter-spacing:4px;color:%s;">'
               'LIVE SYSTEM DEMONSTRATION</div>' % (abs_box(80, 250), "#5FB0AD"))
    head = ('<div style="%sfont-size:60px;font-weight:700;line-height:1.05;color:#fff;">'
            'Run your entire business<br/>in <span style="color:%s;">one system</span>.</div>'
            % (abs_box(80, 286, 1000), "#5FD4CF"))
    sub = ('<div style="%sfont-size:20px;line-height:1.5;color:#C7D6D8;">'
           'From scattered Excel sheets to a single, connected platform &mdash; '
           'inventory, procurement, sales and accounting, in Arabic and English.</div>'
           % (abs_box(80, 470, 880)))
    pill = ('<div style="%sdisplay:inline-flex;align-items:center;padding:10px 18px;border-radius:24px;'
            'background:rgba(95,212,207,.12);border:1px solid rgba(95,212,207,.35);">'
            '<span style="margin-right:10px;">%s</span>'
            '<span style="font-size:14px;font-weight:700;color:#A9E4E0;">'
            'Built on Odoo 18 Community + OCA &mdash; no per-user licence fees</span></div>'
            % (abs_box(80, 560), icon('check', '#5FD4CF', 18, 2.4)))
    foot = ('<div style="%sfont-size:13px;color:#85A0A2;border-top:1px solid rgba(255,255,255,.12);padding-top:14px;">'
            'Live demonstration &nbsp;·&nbsp; %s &nbsp;·&nbsp; '
            'Demo environment: <b style="color:#B9CDCE;">Sudan MedSupply Co. (Khartoum)</b> '
            '&nbsp;·&nbsp; every figure shown is real data you can open and inspect</div>'
            % (abs_box(80, 636, 1120), DATE))
    deco = ('<div style="%sopacity:.5;"><svg width="360" height="360" viewBox="0 0 24 24">'
            '<path d="M10 3h4v7h7v4h-7v7h-4v-7H3v-4h7z" fill="none" stroke="%s" stroke-width=".4"/></svg></div>'
            % (abs_box(940, 360), "#2C4A50"))
    band = '<div style="%sbackground:%s;"></div>' % (abs_box(0, 0, 12, 720), TEAL)
    add(band + deco + mark + eyebrow + head + sub + pill + foot, full=True, p=False)

# ---- 2. THE PROBLEM (operational cracks) ----
def problem():
    body = accent_bar(AMBER)
    body += kicker("The challenge today", AMBER)
    body += title('Excel got you started.<br/>It won’t keep you safe.', INK, 40, 80)
    cards = [
        ('database', 'No single source of truth',
         'Every sheet is a different version. The numbers never quite agree.'),
        ('box', 'Stock is a guess',
         'On-hand quantities are only true the day someone counts them.'),
        ('expiry', 'Medicine expires on the shelf',
         'No expiry or batch tracking means silent write-offs every month.'),
        ('alert', 'Critical items run out',
         'Nothing warns you when insulin or gloves quietly hit zero.'),
        ('cash', 'Money you can’t see',
         'Who owes you, how much, how overdue? Buried across tabs.'),
        ('lock', 'No accountability',
         'Anyone can change any cell &mdash; and no one knows who did.'),
    ]
    xs = [64, 460, 856]
    ys = [228, 432]
    for i, (ic, t, d) in enumerate(cards):
        x = xs[i % 3]; y = ys[i // 3]
        body += ('<div style="%sbackground:#fff;border:1px solid %s;border-left:4px solid %s;'
                 'border-radius:12px;padding:18px 18px 16px;">'
                 '<div style="display:flex;align-items:center;margin-bottom:8px;">'
                 '<span style="width:34px;height:34px;border-radius:9px;background:%s;display:flex;'
                 'align-items:center;justify-content:center;margin-right:11px;">%s</span>'
                 '<span style="font-size:16.5px;font-weight:700;color:%s;">%s</span></div>'
                 '<div style="font-size:13.5px;line-height:1.45;color:%s;">%s</div></div>'
                 % (abs_box(x, y, 360, 178), BORDER, AMBER, AMBER_LT,
                    icon(ic, AMBER_DK, 19, 1.8), INK, t, GRAY, d))
    body += ('<div style="%sfont-size:15px;font-weight:700;color:%s;text-align:center;">'
             'Every one of these is a real cost &mdash; in cash, in spoilage, and in patient trust.</div>'
             % (abs_box(64, 632, 1152), AMBER_DK))
    add(body, accent=AMBER)

# ---- 3. THE HIDDEN COST ----
def cost():
    body = accent_bar(RED)
    body += kicker("What it costs you", RED)
    body += title('The hidden tax of running on spreadsheets', INK, 38, 80)
    cards = [
        ('expiry', 'Expired stock', 'Medicines have hard expiry dates. Without batch tracking, they reach it on your shelf &mdash; pure loss.'),
        ('alert', 'Stockouts', 'Running out of a life-saving item means a lost sale today and a lost customer tomorrow.'),
        ('exchange', 'FX erosion', 'You buy in USD and sell in SDG. Without dated rates, the exchange quietly eats your margin.'),
        ('time', 'Wasted hours', 'Every week, the same numbers are re-typed across sheets &mdash; time your team could sell with.'),
    ]
    xs = [64, 360, 656, 952]
    for i, (ic, t, d) in enumerate(cards):
        x = xs[i]
        body += ('<div style="%sbackground:#fff;border:1px solid %s;border-radius:14px;padding:22px 18px;">'
                 '<span style="width:46px;height:46px;border-radius:12px;background:%s;display:flex;'
                 'align-items:center;justify-content:center;margin-bottom:16px;">%s</span>'
                 '<div style="font-size:19px;font-weight:700;color:%s;margin-bottom:10px;">%s</div>'
                 '<div style="font-size:13.5px;line-height:1.5;color:%s;">%s</div></div>'
                 % (abs_box(x, 220, 264, 300), BORDER, RED_LT, icon(ic, RED, 24, 1.8), INK, t, GRAY, d))
    body += ('<div style="%sbackground:%s;border-radius:14px;display:flex;align-items:center;'
             'justify-content:center;">'
             '<span style="font-size:17px;color:%s;text-align:center;">'
             'None of this shows up on an invoice &mdash; which is exactly why it never gets fixed. '
             '<b style="color:%s;">One system makes all of it visible.</b></span></div>'
             % (abs_box(64, 548, 1152, 64), INK, "#C7D6D8", "#5FD4CF"))
    add(body, accent=RED)

# ---- 4. THE BIG IDEA / FLOW ----
def big_idea():
    body = accent_bar(TEAL)
    body += kicker("The solution", TEAL)
    body += title('One system. Enter once &mdash; it flows everywhere.', INK, 40, 80)
    nodes = [
        ('warehouse', 'Procurement', 'Order from suppliers in USD or SDG'),
        ('box', 'Warehouse', 'Stock updates the moment goods arrive'),
        ('doc', 'Sales', 'Quote → order → delivery → invoice'),
        ('chart', 'Accounting', 'Every move posts to the books, live'),
    ]
    x = 64
    w = 258
    gap = (1152 - 4 * w) // 3
    for i, (ic, t, d) in enumerate(nodes):
        nx = 64 + i * (w + gap)
        body += ('<div style="%sbackground:#fff;border:1px solid %s;border-top:4px solid %s;'
                 'border-radius:14px;padding:22px 18px;text-align:center;">'
                 '<span style="width:54px;height:54px;border-radius:14px;background:%s;display:inline-flex;'
                 'align-items:center;justify-content:center;margin-bottom:14px;">%s</span>'
                 '<div style="font-size:19px;font-weight:700;color:%s;margin-bottom:8px;">%s</div>'
                 '<div style="font-size:13px;line-height:1.45;color:%s;">%s</div></div>'
                 % (abs_box(nx, 250, w, 196), BORDER, TEAL, TEAL_LT, icon(ic, TEAL, 27, 1.8), INK, t, GRAY, d))
        if i < 3:
            ax = nx + w + (gap - 22) // 2
            body += ('<div style="%scolor:%s;font-size:30px;line-height:1;">&#8594;</div>'
                     % (abs_box(ax, 330, 30), TEAL))
    body += ('<div style="%sbackground:%s;border-radius:14px;display:flex;align-items:center;'
             'justify-content:center;padding:0 30px;">'
             '<span style="font-size:18px;color:%s;text-align:center;line-height:1.5;">'
             'A purchase updates your stock. A sale updates stock <b>and</b> raises the invoice '
             '<b>and</b> posts to your accounts &mdash; <b style="color:%s;">automatically</b>. '
             'No re-typing. One set of numbers everyone trusts.</span></div>'
             % (abs_box(64, 500, 1152, 110), TEAL_LT, INK, TEAL_DK))
    add(body, accent=TEAL)

# ---- 5. REAL SYSTEM (apps_home) ----
def real_system():
    body = accent_bar(TEAL)
    body += kicker("A working system, not a mock-up", TEAL)
    body += title('Everything today is live &mdash; data you can open and inspect', INK, 33, 80)
    body += bullets([
        '<b>Seven connected apps</b>, one login, one database &mdash; Contacts, Sales, Purchase, Inventory, Accounting, Dashboards and Settings.',
        '<b>Web-based.</b> Open it from the office, the warehouse, or a phone &mdash; nothing to install on each PC.',
        '<b>Real records.</b> The orders, invoices and stock you’ll see are seeded demo data for <b>Sudan MedSupply Co.</b>',
        'Switch on more apps any time &mdash; the platform grows with you.',
    ], y=190, w=470, slot=82)
    body += shot('apps_home.png', 566, 158, 650)
    body += caption('The Odoo app launcher — the real, themed interface',
                    566, 158 + disp_h('apps_home.png', 650) + 9, 650)
    body += live_cue('Open the app launcher (the 9-dot grid) and show the live apps.')
    add(body, accent=TEAL)

# ---- 6. AGENDA ----
def agenda():
    body = accent_bar(TEAL)
    body += kicker("Today’s walk-through", TEAL)
    body += title('What we’ll show you &mdash; live', INK, 40, 80)
    items = [
        ('box', 'Your catalogue & live stock'),
        ('snow', 'Expiry, batches & cold chain'),
        ('refresh', 'Automatic re-ordering'),
        ('warehouse', 'Multiple warehouses & locations'),
        ('exchange', 'Buy in USD, sell in SDG'),
        ('doc', 'Sell & invoice in a few clicks'),
        ('cash', 'Who owes you & your cash position'),
        ('lock', 'Roles, control & accountability'),
    ]
    xs = [64, 660]
    for i, (ic, t) in enumerate(items):
        x = xs[i % 2]; y = 210 + (i // 2) * 96
        body += ('<div style="%sdisplay:flex;align-items:center;background:#fff;border:1px solid %s;'
                 'border-radius:12px;padding:16px 18px;">'
                 '<span style="width:38px;height:38px;border-radius:50%%;background:%s;color:#fff;'
                 'display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:700;'
                 'margin-right:14px;flex:none;">%d</span>'
                 '<span style="margin-right:12px;">%s</span>'
                 '<span style="font-size:17px;font-weight:700;color:%s;">%s</span></div>'
                 % (abs_box(x, y, 556, 78), BORDER, TEAL, i + 1, icon(ic, TEAL, 21, 1.8), INK, t))
    body += ('<div style="%sfont-size:14px;color:%s;text-align:center;">'
             '&hellip; then your questions: <b style="color:%s;">cost, growth, moving off Excel, training & support.</b></div>'
             % (abs_box(64, 632, 1152), GRAY, TEAL_DK))
    add(body, accent=TEAL)

# ---- generic capability (single screenshot, right) ----
def cap(kick, ttl, blist, shot_name, cue, chiplist=None, accent=TEAL, ar=False,
        cap_text=None, ttl_size=33):
    body = accent_bar(accent)
    body += kicker(kick, accent)
    body += title(ttl, INK, ttl_size, 80)
    n = len(blist)
    slot = 92 if n <= 3 else 74
    body += bullets(blist, y=190, w=470, slot=slot, accent=accent)
    body += shot(shot_name, 566, 158, 650, ar=ar)
    cap_y = 158 + disp_h(shot_name, 650, ar) + 9
    body += caption(cap_text or "", 566, cap_y, 650)
    if chiplist:
        body += chips(chiplist, x=64, y=494, width=478, accent=accent)
    body += live_cue(cue, accent=AMBER)
    add(body, accent=accent)

# ---- generic dual-screenshot capability ----
def cap2(kick, ttl, lead, shots, cue, accent=TEAL, ttl_size=34):
    body = accent_bar(accent)
    body += kicker(kick, accent)
    body += title(ttl, INK, ttl_size, 80)
    body += ('<div style="%sfont-size:16px;line-height:1.45;color:%s;">%s</div>'
             % (abs_box(64, 168, 1152), GRAY, lead))
    # two frames, centred
    w = 512
    gap = 40
    total = 2 * w + gap
    x1 = (1280 - total) // 2
    x2 = x1 + w + gap
    y = 244
    for (name, cp, arflag), x in zip(shots, (x1, x2)):
        body += shot(name, x, y, w, ar=arflag)
        body += caption(cp, x, y + disp_h(name, w, arflag) + 10, w)
    body += live_cue(cue, accent=AMBER)
    add(body, accent=accent)

# ---- 16. section divider ----
def divider(label, ttl, sub, accent=TEAL):
    band = '<div style="%sbackground:%s;"></div>' % (abs_box(0, 0, 12, 720), accent)
    deco = ('<div style="%sopacity:.5;"><svg width="320" height="320" viewBox="0 0 24 24">'
            '<path d="M10 3h4v7h7v4h-7v7h-4v-7H3v-4h7z" fill="none" stroke="#2C4A50" stroke-width=".4"/></svg></div>'
            % abs_box(980, 380))
    k = ('<div style="%sfont-size:14px;font-weight:700;letter-spacing:4px;color:%s;">%s</div>'
         % (abs_box(80, 286), "#5FB0AD", label))
    t = ('<div style="%sfont-size:54px;font-weight:700;line-height:1.07;color:#fff;">%s</div>'
         % (abs_box(80, 320, 1000), ttl))
    s = ('<div style="%sfont-size:19px;line-height:1.5;color:#C7D6D8;">%s</div>'
         % (abs_box(80, 470, 900), sub))
    add(band + deco + k + t + s, full=True, p=False)

# ---- qa slide (text-forward objection handling) ----
def qa(kick, ttl, blist, accent=TEAL, footer_note=None, ttl_size=40, icon_name=None):
    body = accent_bar(accent)
    body += kicker(kick, accent)
    body += title(ttl, INK, ttl_size, 80)
    body += bullets(blist, y=210, w=1040, slot=78, accent=accent, fs=17)
    if footer_note:
        body += ('<div style="%sbackground:%s;border-radius:12px;display:flex;align-items:center;'
                 'padding:0 24px;">'
                 '<span style="margin-right:14px;flex:none;">%s</span>'
                 '<span style="font-size:15px;color:%s;">%s</span></div>'
                 % (abs_box(64, 612, 1152, 50), TEAL_LT, icon('tag', TEAL_DK, 22, 1.8), INK, footer_note))
    add(body, accent=accent)

# ============================================================ BUILD ORDER ====
cover()
problem()
cost()
big_idea()
real_system()
agenda()

# 01 catalogue
cap("01 · Your catalogue",
    'Every product, with real-time stock &mdash; one source of truth',
    ['<b>All 10 medical items</b> in one catalogue: Pharmaceuticals, Consumables and Devices.',
     '<b>Live on-hand</b> that updates itself: Insulin 50, Paracetamol 150, Gloves 60 units.',
     'Internal references, cost, sale price and 15% tax built into every product.'],
    'products_list.png',
    'Open Inventory ▸ Products, search “Insulin” and open its card.',
    chiplist=['10 products', '3 categories', 'Live on-hand'],
    accent=TEAL, cap_text='The product catalogue with live on-hand quantities')

# 02 expiry / cold chain
cap("02 · Medical traceability",
    'Never write off expired stock again',
    ['<b>Every batch carries its expiry date</b> &mdash; and the system sells oldest-first (FEFO) on its own.',
     '<b>Cold-chain items</b> like Insulin live in a dedicated <b>Cold Storage (2–8&deg;C)</b> location.',
     '<b>Full recall traceability</b> &mdash; find every unit of a bad lot in seconds.'],
    'lots_list.png',
    'Inventory ▸ Lots/Serial Numbers — open LOT-GULF-01 (Insulin) and show its expiry.',
    chiplist=['Lot + expiry', 'FEFO removal', 'Cold Storage 2–8°C', 'Recall-ready'],
    accent=TEAL, cap_text='Lots grouped by location — note Cold Storage (2-8C)')

# 03 reorder
cap("03 · Never run out",
    'The system watches your stock so you don’t have to',
    ['<b>Set a min / max per item</b>: Insulin 20/80, Paracetamol 50/200, Gloves 30/120.',
     'When stock hits the minimum, it <b>flags &mdash; or drafts the purchase order &mdash; automatically</b>.',
     'No more learning about a stockout from an unhappy customer.'],
    'reordering_rules.png',
    'Inventory ▸ Operations ▸ Reordering Rules — show On-Hand vs Min/Max and the To-Order column.',
    chiplist=['Min / Max rules', 'Auto purchase orders', 'Per warehouse'],
    accent=TEAL, cap_text='Reordering rules with live on-hand vs min/max')

# 04 multi-warehouse
cap("04 · Multi-warehouse",
    'Khartoum, Port Sudan &mdash; and every location in between',
    ['<b>Two warehouses</b> today (Khartoum Central, Port Sudan) &mdash; add more any time.',
     'Track stock by <b>internal location</b>: Cold Storage, Quarantine, Expired / Damaged.',
     '<b>Transfer between sites</b> with a full paper trail; always know what’s where.'],
    'warehouses.png',
    'Inventory ▸ Configuration ▸ Warehouses, then open the Locations list.',
    chiplist=['2 warehouses', 'Internal locations', 'Tracked transfers'],
    accent=TEAL, cap_text='Warehouses: Khartoum Central (KRT) & Port Sudan (PRT)')

# 05 multi-currency (dual)
cap2("05 · Multi-currency",
     'Buy in USD, sell in SDG &mdash; your margin protected automatically',
     'Import from Gulf MedTrade in US dollars and sell to hospitals in Sudanese pounds. The system keeps a '
     '<b>dated exchange-rate history</b> and converts every document for you &mdash; no manual maths, no guesswork.',
     [('po_usd.png', 'Purchase P00002 — $1,288.00  ⇄  5,796,000 SDG', False),
      ('currency_usd.png', 'Dated FX history — 1 USD = 2,400 → 4,500 SDG', False)],
     'Purchase ▸ open P00002 (Gulf MedTrade) — show the $ total and its SDG equivalent.',
     accent=INDIGO)

# 06 sales -> invoice (dual)
cap2("06 · Quote to cash",
     'From quotation to a paid invoice &mdash; in a few clicks',
     'One confirmed order creates the delivery <b>and</b> the invoice; the 15% tax is calculated for you and '
     'nothing is re-typed. The same order you sell becomes the invoice you collect.',
     [('sale_order.png', 'Order S00001 — Khartoum Teaching Hospital · 2,038,950 SDG', False),
      ('customer_invoice.png', 'Invoice INV/2026/00001 — Posted & Paid', False)],
     'Sales ▸ open S00001, then its invoice — show the green PAID banner.',
     accent="#0F8A5F")

# 07 receivables / cash
cap("07 · Know who owes you",
    'See your cash position the moment you log in',
    ['<b>Live dashboard</b>: 3 invoices unpaid (3,966,350 SDG), 2 already overdue.',
     '<b>Bank of Khartoum balance 3,924,950 SDG</b> at a glance, with a trend.',
     'One click prints an <b>Aged Receivable</b> report &mdash; chase the right people, on time.'],
    'accounting_dashboard.png',
    'Accounting ▸ Dashboard — point at Unpaid / Late and the live bank balance.',
    chiplist=['Unpaid & overdue', 'Bank balances live', 'Balance Sheet · P&L · Aged — any day'],
    accent=VIOLET, cap_text='The Accounting dashboard — invoices, bills and bank, live',
    ttl_size=34)

# 08 roles / control
cap("08 · Control & accountability",
    'Each person sees exactly what they should',
    ['<b>Six role-based users</b>: Manager, Procurement, Sales, Warehouse, Accountant, Admin.',
     'The <b>warehouse keeper can’t edit prices</b>; the <b>sales rep can’t see the books</b>.',
     'Every record keeps a <b>full history of who changed what, and when</b> &mdash; Excel can’t.'],
    'user_role.png',
    'Settings ▸ Users — open Layla (General Manager) ▸ Access Rights.',
    chiplist=['6 user roles', 'Granular permissions', 'Full audit trail'],
    accent=SLATE, cap_text='Access Rights for Layla (General Manager)')

# 09 bilingual
cap("09 · Arabic & English",
    'The whole system &mdash; and the manual &mdash; in full Arabic',
    ['<b>Right-to-left, fully translated.</b> Your team works in the language it’s comfortable in.',
     '<b>Per-user</b> &mdash; the accountant in Arabic, an English-speaking partner in English, same data.',
     'The 17-chapter <b>user manual ships in both languages</b>, with real screenshots.'],
    'sale_order.png',
    'Switch my user to Arabic and reload — show the same screen, right-to-left.',
    chiplist=['Full RTL', 'Per-user language', 'Bilingual manual'],
    accent="#B0568A", ar=True, cap_text='The same order S00001 — in Arabic, right-to-left')

# ----- Questions section -----
divider("Your questions, answered",
        "The questions every<br/>owner asks first",
        "Cost, growth, moving off Excel, training &mdash; the practical realities of switching, answered plainly.",
        accent=TEAL)

# Q cost
qa("What will it cost me?",
   'No per-user licence fees. Ever.',
   ['Built on <b>Odoo 18 Community</b> and trusted open-source (OCA) modules &mdash; the <b>software licence is free</b>.',
    'You invest in <b>setup, training and support</b> &mdash; not in monthly seats.',
    'Add users (you saw six) at <b>no extra licence cost</b> as your team grows.',
    'You <b>own your data and your database</b>. No vendor lock-in, no ransom at renewal.'],
   accent=TEAL,
   footer_note='Enterprise ERPs charge <b>per user, per month</b> &mdash; for the same features you just saw working.')

# Q growth / extensibility (module grid)
def growth():
    body = accent_bar(TEAL)
    body += kicker("Can it grow with us?", TEAL)
    body += title('Start with what you need. Add the rest when you’re ready.', INK, 33, 80)
    body += ('<div style="%sfont-size:16px;line-height:1.45;color:%s;">'
             'Today you’re running five apps. The same platform has dozens more &mdash; switch them on when '
             'the business calls for them, with no migration and nothing to rip out.</div>'
             % (abs_box(64, 162, 1152), GRAY))
    active = ['Inventory', 'Purchase', 'Sales', 'Accounting', 'Contacts']
    avail = ['Manufacturing', 'Point of Sale', 'Barcode scanning', 'HR & Payroll', 'CRM',
             'e-Commerce', 'Projects', 'Maintenance', 'Quality', 'Fleet']
    body += ('<div style="%sfont-size:12px;font-weight:700;letter-spacing:1.5px;color:%s;text-transform:uppercase;">Running today</div>'
             % (abs_box(64, 234), TEAL_DK))
    dot = ('<span style="display:inline-block;width:8px;height:8px;border-radius:50%%;'
           'background:%s;vertical-align:middle;margin-right:9px;"></span>')
    act_html = ""
    for a in active:
        act_html += ('<span style="display:inline-block;margin-right:11px;margin-bottom:11px;'
                     'background:%s;border:1px solid %s55;border-radius:22px;padding:9px 17px;'
                     'font-size:14px;font-weight:700;color:%s;white-space:nowrap;vertical-align:middle;">%s%s</span>'
                     % (TEAL_LT, TEAL, TEAL_DK, dot % TEAL, a))
    body += '<div style="%s">%s</div>' % (abs_box(64, 254, 1150), act_html)
    body += ('<div style="%sfont-size:12px;font-weight:700;letter-spacing:1.5px;color:%s;text-transform:uppercase;">Available to switch on</div>'
             % (abs_box(64, 332), GRAY_LT))
    av_html = ""
    for a in avail:
        av_html += ('<span style="display:inline-block;margin-right:11px;margin-bottom:11px;'
                    'background:#fff;border:1px dashed %s;border-radius:22px;padding:9px 17px;'
                    'font-size:14px;font-weight:700;color:%s;white-space:nowrap;vertical-align:middle;">%s%s</span>'
                    % (BORDER, SLATE, dot % GRAY_LT, a))
    body += '<div style="%s">%s</div>' % (abs_box(64, 356, 1150), av_html)
    body += ('<div style="%sbackground:%s;border-radius:12px;display:flex;align-items:center;padding:0 24px;">'
             '<span style="margin-right:14px;flex:none;">%s</span>'
             '<span style="font-size:15px;color:%s;">Need something specific to your business? '
             '<b>Custom modules and reports are built to fit</b> &mdash; the platform is yours to extend.</span></div>'
             % (abs_box(64, 612, 1152, 50), TEAL_LT, icon('layers', TEAL_DK, 22, 1.8), INK))
    add(body, accent=TEAL)
growth()

# Q migration
qa("How do we move off Excel?",
   'Your spreadsheets are the starting point, not the enemy',
   ['<b>Import products, customers, suppliers and opening stock</b> straight from your Excel / CSV files.',
    'We <b>map your columns once</b> &mdash; the data lands in the right place.',
    'Run the new system <b>alongside Excel</b> for a short parallel period to build confidence.',
    'Go live <b>when you’re ready</b>, not before.'],
   accent=TEAL,
   footer_note='Most of what you keep in Excel today imports in a single afternoon.')

# Q training
qa("How will my team learn it?",
   'A complete manual already exists &mdash; in Arabic and English',
   ['A <b>17-chapter illustrated user manual</b> with <b>53 real screenshots</b>, written for non-accountants.',
    '<b>Role-based</b>: each person learns only their part &mdash; warehouse, sales, accounting.',
    '<b>Hands-on training</b> during rollout, on your own data.',
    'We don’t hand you a login and a goodbye &mdash; <b>ongoing support</b> is part of it.'],
   accent=TEAL,
   footer_note='The manual you saw referenced is already written, bilingual, and ready for your team.')

# Q deployment
qa("Where does it run?",
   'Secure, web-based, reachable from office, warehouse or phone',
   ['Runs on <b>your own server or in the cloud</b> &mdash; your choice, your control.',
    'Access from <b>any browser</b> &mdash; no software to install and update on each PC.',
    '<b>Automated daily backups</b> so your business is never one crash from disaster.',
    '<b>Encrypted login</b> and role-based access keep your data safe.'],
   accent=TEAL,
   footer_note='Start on a single server today; move to the cloud as you grow — same system, same data.')

# ----- Close -----
# compare table
def compare():
    body = accent_bar(TEAL)
    body += kicker("The bottom line", TEAL)
    body += title('Excel today vs. your new system', INK, 38, 80)
    rows = [
        ('Single source of truth', 'Many files, many versions', 'One shared database'),
        ('Real-time stock levels', 'Only after a manual count', 'Live, always current'),
        ('Expiry & batch tracking', 'None', 'Per-lot, with FEFO'),
        ('Re-order alerts', 'You find out too late', 'Automatic min/max'),
        ('Multi-currency (USD / SDG)', 'Manual, error-prone', 'Dated rates, auto-converted'),
        ('Invoicing & 15% tax', 'Typed by hand', 'One click from the order'),
        ('Who owes you / cash view', 'Buried in tabs', 'Live dashboard & aged report'),
        ('Per-person access & audit', 'Anyone edits anything', 'Roles + full history'),
        ('Arabic + English', 'Whatever you build', 'Built-in, right-to-left'),
        ('Room to grow', 'Hits a ceiling', 'Add apps & custom features'),
    ]
    y0 = 168
    rh = 47
    # header
    body += ('<div style="%sdisplay:flex;align-items:center;border-bottom:2px solid %s;padding-bottom:8px;">'
             '<span style="width:430px;font-size:13px;font-weight:700;letter-spacing:1px;color:%s;text-transform:uppercase;">Capability</span>'
             '<span style="width:360px;font-size:13px;font-weight:700;letter-spacing:1px;color:%s;text-transform:uppercase;">Excel today</span>'
             '<span style="font-size:13px;font-weight:700;letter-spacing:1px;color:%s;text-transform:uppercase;">Your new ERP</span></div>'
             % (abs_box(64, y0, 1152), INK, GRAY_LT, RED, TEAL_DK))
    for i, (cap_, ex, erp) in enumerate(rows):
        ry = y0 + 34 + i * rh
        bg = "#FFFFFF" if i % 2 else BG_SOFT
        body += ('<div style="%sbackground:%s;border-radius:8px;display:flex;align-items:center;padding:0 8px;">'
                 '<span style="width:418px;font-size:14.5px;font-weight:700;color:%s;">%s</span>'
                 '<span style="width:352px;font-size:13.5px;color:%s;display:flex;align-items:center;">'
                 '<span style="margin-right:8px;flex:none;">%s</span>%s</span>'
                 '<span style="font-size:13.5px;color:%s;font-weight:700;display:flex;align-items:center;">'
                 '<span style="margin-right:8px;flex:none;">%s</span>%s</span></div>'
                 % (abs_box(64, ry, 1152, rh - 5), bg, INK, cap_, GRAY,
                    icon('x', RED, 16, 2.4), ex, TEAL_DK, icon('check', TEAL, 16, 2.6), erp))
    add(body, accent=TEAL)
compare()

# roadmap
def roadmap():
    body = accent_bar(TEAL)
    body += kicker("Getting started", TEAL)
    body += title('Live in about four weeks', INK, 40, 80)
    phases = [
        ('Week 1', 'Configure', ['Your company, branches & users', 'Warehouses & locations', 'Taxes & currencies']),
        ('Week 2', 'Import data', ['Products & categories', 'Customers & suppliers', 'Opening stock from Excel']),
        ('Week 3', 'Train & parallel', ['Role-based training', 'Run alongside Excel', 'Build the team’s confidence']),
        ('Week 4', 'Go live', ['Switch over fully', 'Real orders & invoices', 'Ongoing support begins']),
    ]
    w = 264
    gap = (1152 - 4 * w) // 3
    # connector line
    body += '<div style="%sbackground:%s;"></div>' % (abs_box(64 + 30, 286, 1152 - 60, 3), BORDER)
    for i, (wk, t, pts) in enumerate(phases):
        x = 64 + i * (w + gap)
        body += ('<div style="position:absolute;left:%dpx;top:274px;width:26px;height:26px;border-radius:50%%;'
                 'background:%s;color:#fff;display:flex;align-items:center;justify-content:center;'
                 'font-size:13px;font-weight:700;">%d</div>' % (x + 18, TEAL, i + 1))
        body += ('<div style="%sbackground:#fff;border:1px solid %s;border-top:4px solid %s;border-radius:14px;'
                 'padding:18px;">'
                 '<div style="font-size:12px;font-weight:700;letter-spacing:1.5px;color:%s;text-transform:uppercase;">%s</div>'
                 '<div style="font-size:21px;font-weight:700;color:%s;margin:4px 0 12px;">%s</div>%s</div>'
                 % (abs_box(x, 320, w, 250), BORDER, TEAL, TEAL_DK, wk, INK, t,
                    "".join('<div style="font-size:13.5px;line-height:1.4;color:%s;margin-bottom:9px;'
                            'padding-left:16px;position:relative;">'
                            '<span style="position:absolute;left:0;top:7px;width:6px;height:6px;border-radius:50%%;'
                            'background:%s;"></span>%s</div>' % (GRAY, TEAL, p) for p in pts)))
    body += ('<div style="%sbackground:%s;border-radius:12px;display:flex;align-items:center;justify-content:center;">'
             '<span style="font-size:16px;color:%s;">A clear, low-risk path &mdash; '
             '<b style="color:%s;">you’re never without a working system for a single day.</b></span></div>'
             % (abs_box(64, 600, 1152, 54), TEAL_LT, INK, TEAL_DK))
    add(body, accent=TEAL)
roadmap()

# CTA / close
def close2():
    band = '<div style="%sbackground:%s;"></div>' % (abs_box(0, 0, 12, 720), TEAL)
    deco = ('<div style="%sopacity:.5;"><svg width="300" height="300" viewBox="0 0 24 24">'
            '<path d="M10 3h4v7h7v4h-7v7h-4v-7H3v-4h7z" fill="none" stroke="#2C4A50" stroke-width=".4"/></svg></div>'
            % abs_box(990, 400))
    k = ('<div style="%sfont-size:14px;font-weight:700;letter-spacing:4px;color:%s;">NEXT STEPS</div>'
         % (abs_box(80, 96), "#5FB0AD"))
    t = ('<div style="%sfont-size:48px;font-weight:700;line-height:1.08;color:#fff;">'
         'Let’s set up <span style="color:%s;">your</span> business<br/>in the system.</div>'
         % (abs_box(80, 128, 1000), "#5FD4CF"))
    steps = [
        ('upload', 'We take your real product & customer list'),
        ('layers', 'We configure a private demo with your own data'),
        ('users', 'You and your team test-drive it, hands-on'),
        ('pin', 'We agree a go-live date that suits you'),
    ]
    body = band + deco + k + t
    for i, (ic, txt) in enumerate(steps):
        y = 286 + i * 62
        body += ('<div style="%sdisplay:flex;align-items:center;">'
                 '<span style="width:40px;height:40px;border-radius:11px;background:rgba(95,212,207,.14);'
                 'border:1px solid rgba(95,212,207,.3);display:flex;align-items:center;justify-content:center;'
                 'margin-right:16px;flex:none;">%s</span>'
                 '<span style="font-size:18px;color:#DCE8E9;">%s</span></div>'
                 % (abs_box(80, y, 760), icon(ic, '#7FE3DE', 20, 1.8), txt))
    body += ('<div style="%sfont-size:22px;font-weight:700;color:#fff;line-height:1.4;'
             'border-top:1px solid rgba(255,255,255,.14);padding-top:20px;">'
             'Everything you saw today was real.&nbsp; '
             '<span style="color:#5FD4CF;">Next, let’s make it yours.</span></div>'
             % (abs_box(80, 568, 1000)))
    body += ('<div style="%sfont-size:13px;color:#85A0A2;">Medical-Supply Distribution ERP &nbsp;·&nbsp; '
             'Built on Odoo 18 Community + OCA &nbsp;·&nbsp; %s</div>'
             % (abs_box(80, 662, 1000), DATE))
    add(body, full=True, p=False)
close2()

# ----------------------------------------------------------------- assemble ----
T = len(SLIDES)
CSS = (
    "*{margin:0;padding:0;box-sizing:border-box;}"
    + font_face() +
    "html,body{font-family:'Alexandria',sans-serif;-webkit-font-smoothing:antialiased;}"
    "@page{size:1280px 720px;margin:0;}"
    ".slide{position:relative;width:1280px;height:720px;overflow:hidden;page-break-after:always;}"
    ".slide:last-child{page-break-after:auto;}"
)
html = ("<!DOCTYPE html><html><head><meta charset='utf-8'><style>%s</style></head><body>%s</body></html>"
        % (CSS, "".join(s.replace("%%T%%", str(T)) for s in SLIDES)))

out_html = os.path.join(OUT_DIR, "Medical-Supply_ERP_Demo_Deck.html")
with open(out_html, "w", encoding="utf-8") as f:
    f.write(html)
print("Wrote %s  (%d slides, %.1f MB)" % (out_html, T, len(html) / 1e6))
