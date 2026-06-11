# -*- coding: utf-8 -*-
"""
Build a 16:9 sales / live-demo deck (HTML -> PDF) for the medical-supply ERP.

Bilingual: `python3 build_deck.py en` (default) or `python3 build_deck.py ar`.
The Arabic build mirrors the whole layout right-to-left, uses the Arabic UI
screenshots (docs/manual/img/ar/*) and the Alexandria Arabic font.

A tight 15-slide manager flow:  problem -> one connected system -> 7 capability
slides you can SHOW LIVE -> the decision (Excel-vs-ERP, cost & growth, switching,
4-week roadmap, next steps). Every figure is REAL data from the running
`erpmedsupply` demo (docs/manual/_ground_truth/demo.json) and every screenshot is
a real capture of the themed Odoo UI.

Output:  docs/deck/Medical-Supply_ERP_Demo_Deck_{EN,AR}.html  (self-contained)
Render to PDF with WeasyPrint (inside the odoo container, which has it):
    bash scripts/build_deck_pdf.sh        # builds both languages
"""
import base64
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_EN = os.path.join(ROOT, "docs", "manual", "img", "en")
IMG_AR = os.path.join(ROOT, "docs", "manual", "img", "ar")
FONTS = os.path.join(ROOT, "scripts", "fonts")
OUT_DIR = os.path.join(ROOT, "docs", "deck")
os.makedirs(OUT_DIR, exist_ok=True)

# ------------------------------------------------------------------- language --
LANG = (sys.argv[1] if len(sys.argv) > 1 else "en").lower()
RTL = LANG == "ar"
DIR = "rtl" if RTL else "ltr"
ALIGN = "right" if RTL else "left"
IMG = IMG_AR if RTL else IMG_EN

DATE = "10 يونيو 2026" if RTL else "10 June 2026"


def T(en, ar):
    """Pick the string for the current language."""
    return ar if RTL else en


# ---------------------------------------------------------------- palette ----
INK      = "#0B2027"
INK2     = "#13323B"
TEAL     = "#0E7C7B"
TEAL_DK  = "#0A5C5B"
TEAL_LT  = "#E7F4F3"
AMBER    = "#C77E18"
AMBER_DK = "#9A5E0E"
AMBER_LT = "#FBF1DF"
RED      = "#B23A2E"
RED_LT   = "#FBECEA"
INDIGO   = "#3C4FB0"
VIOLET   = "#6D4AA6"
SLATE    = "#3A4A57"
GRAY     = "#4A5A66"
GRAY_LT  = "#8A99A4"
BORDER   = "#E2E8EA"
BG_SOFT  = "#F5F8F8"


# ------------------------------------------------------------------ assets ----
def _b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def img_uri(name):
    return "data:image/png;base64," + _b64(os.path.join(IMG, name))


def png_size(name):
    import struct
    with open(os.path.join(IMG, name), "rb") as f:
        head = f.read(24)
    w, h = struct.unpack(">II", head[16:24])
    return w, h


def disp_h(name, w):
    iw, ih = png_size(name)
    return int(round(w * ih / iw))


def fit_w(name, w_max, h_max):
    """Largest width <= w_max whose displayed height stays within h_max, so the
    framed shot + its caption never collide with the SHOW LIVE band (y=612)."""
    ih = disp_h(name, w_max)
    if ih <= h_max:
        return w_max
    return int(w_max * h_max / ih)


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
 'flow':'<rect x="3" y="9" width="6" height="6" rx="1"/><rect x="15" y="9" width="6" height="6" rx="1"/><path d="M9 12h6"/>',
 'pin':'<path d="M12 22s7-6.5 7-12A7 7 0 0 0 5 10c0 5.5 7 12 7 12z"/><circle cx="12" cy="10" r="2.4"/>',
 'grid':'<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
}


def icon(name, color=TEAL, size=22, sw=1.8):
    return ('<svg width="%d" height="%d" viewBox="0 0 24 24" fill="none" stroke="%s" '
            'stroke-width="%s" stroke-linecap="round" stroke-linejoin="round" '
            'style="vertical-align:middle;">%s</svg>'
            % (size, size, color, sw, _ICON[name]))


# ---------------------------------------------------------------- helpers ----
def pos(x, y, w=None, h=None, extra=""):
    """Absolute box. In RTL the x coordinate anchors from the RIGHT edge, which
    mirrors every positioned element across the 1280px canvas."""
    side = "right" if RTL else "left"
    s = "position:absolute;%s:%dpx;top:%dpx;" % (side, x, y)
    if w is not None:
        s += "width:%dpx;" % w
    if h is not None:
        s += "height:%dpx;" % h
    return s + extra


def txtdir():
    return "direction:%s;text-align:%s;" % (DIR, ALIGN)


def kicker(text, color=TEAL):
    spacing = "" if RTL else "letter-spacing:2.5px;text-transform:uppercase;"
    return ('<div style="%sfont-size:13px;font-weight:700;%scolor:%s;%s">%s</div>'
            % (pos(64, 50), spacing, color, txtdir(), text))


def title(text, color=INK, size=42, top=80, width=1152):
    lh = "1.2" if RTL else "1.1"
    return ('<div style="%sfont-size:%dpx;font-weight:700;line-height:%s;color:%s;%s">%s</div>'
            % (pos(64, top, width), size, lh, color, txtdir(), text))


def accent_bar(color=TEAL):
    return '<div style="%sbackground:%s;"></div>' % (pos(0, 0, 12, 720), color)


def footer(p, accent=TEAL):
    line = '<div style="%sborder-top:1px solid %s;"></div>' % (pos(64, 678, 1152), BORDER)
    brand = T('Medical-Supply Distribution ERP', 'نظام توزيع المستلزمات الطبية')
    sub = T('Odoo 18 Community + OCA', 'Odoo 18 Community + OCA')
    left = ('<div style="%sfont-size:11px;color:%s;letter-spacing:.3px;%s">%s'
            '<span style="color:%s;"> &nbsp;·&nbsp; %s</span></div>'
            % (pos(64, 690, 560), GRAY, txtdir(), brand, GRAY_LT, sub))
    mid = ('<div style="%stext-align:center;font-size:11px;color:%s;">%s · %s</div>'
           % (pos(440, 690, 400), GRAY_LT, T('Confidential · Live demonstration', 'سرّي · عرض مباشر'), DATE))
    rt_align = "left" if RTL else "right"
    rt = ('<div style="%stext-align:%s;direction:ltr;font-size:11px;font-weight:700;color:%s;">%s / %s</div>'
          % (pos(1016, 690, 200), rt_align, accent, p, "%%T%%"))
    return line + left + mid + rt


def live_cue(text, accent=AMBER):
    """The bottom 'SHOW LIVE' band. Laid out with inline-block flow (NOT flex):
    under an rtl page WeasyPrint pushes the leading flex child of a right-anchored
    positioned box clean off the right edge of the slide. inline-block items in a
    `direction`/`text-align` line — vertically centred with `line-height` (the same
    pattern the cover mark, roadmap circles and close steps use) — stay inside the
    band in both languages. `white-space:nowrap` keeps the chip + label + cue on a
    single centred line."""
    mside = "margin-left" if RTL else "margin-right"
    play = ('<svg width="11" height="11" viewBox="0 0 24 24" style="vertical-align:middle;">'
            '<path d="M7 4l13 8-13 8z" fill="#fff"/></svg>')
    chip = ('<span style="display:inline-block;vertical-align:middle;direction:ltr;text-align:center;'
            'line-height:26px;width:26px;height:26px;border-radius:7px;background:%s;%s:10px;">%s</span>'
            % (accent, mside, play))
    label = ('<span style="display:inline-block;vertical-align:middle;font-size:13px;font-weight:700;'
             'color:%s;letter-spacing:.4px;%s:14px;%s">%s</span>'
             % (AMBER_DK, mside, ("" if RTL else "text-transform:uppercase;"),
                T('Show live', 'اعرض مباشرةً')))
    body = ('<span style="display:inline-block;vertical-align:middle;font-size:13.5px;color:%s;">%s</span>'
            % (INK2, text))
    return ('<div style="%sbackground:%s;border-radius:10px;padding:0 18px;line-height:48px;'
            'white-space:nowrap;overflow:hidden;border:1px solid %s33;%s">%s%s%s</div>'
            % (pos(64, 612, 1152, 48), AMBER_LT, accent, txtdir(), chip, label, body))


def note_band(text):
    """Full-width teal callout band at the bottom of a slide. inline-block flow
    (NOT flex): a positioned right-anchored flex band pushes its leading icon clean
    off the right edge under an rtl page (same defect as live_cue), so the icon is
    laid inline-block and the line is centred with line-height instead."""
    mside = "margin-left" if RTL else "margin-right"
    ic = ('<span style="display:inline-block;vertical-align:middle;direction:ltr;%s:14px;">%s</span>'
          % (mside, icon('tag', TEAL_DK, 22, 1.8)))
    tx = ('<span style="display:inline-block;vertical-align:middle;font-size:15px;color:%s;">%s</span>'
          % (INK, text))
    return ('<div style="%sbackground:%s;border-radius:12px;padding:0 24px;line-height:50px;'
            'white-space:nowrap;overflow:hidden;%s">%s%s</div>'
            % (pos(64, 612, 1152, 50), TEAL_LT, txtdir(), ic, tx))


def chips(items, x=64, y=560, width=478, accent=TEAL):
    mside = "margin-left" if RTL else "margin-right"
    inner = ""
    for it in items:
        inner += ('<span style="display:inline-block;%s:9px;margin-bottom:8px;'
                  'padding:6px 13px;border-radius:20px;background:%s;color:%s;'
                  'font-size:12.5px;font-weight:700;border:1px solid %s33;">%s</span>'
                  % (mside, TEAL_LT, TEAL_DK, accent, it))
    return '<div style="%s%s">%s</div>' % (pos(x, y, width), txtdir(), inner)


def shot(name, x, y, w):
    """A framed screenshot (browser-card look)."""
    dots = ('<span style="width:8px;height:8px;border-radius:50%%;background:#E76A5E;display:inline-block;margin:0 3px;"></span>'
            '<span style="width:8px;height:8px;border-radius:50%%;background:#E6B95C;display:inline-block;margin:0 3px;"></span>'
            '<span style="width:8px;height:8px;border-radius:50%%;background:#7FC08A;display:inline-block;margin:0 3px;"></span>')
    return ('<div style="%sborder:1px solid %s;border-radius:12px;overflow:hidden;'
            'box-shadow:0 18px 40px -18px rgba(11,32,39,.45);background:#fff;">'
            '<div style="height:26px;background:%s;display:flex;align-items:center;padding:0 9px;">%s</div>'
            '<img src="%s" style="display:block;width:%dpx;height:auto;"/></div>'
            % (pos(x, y, w), BORDER, BG_SOFT, dots, img_uri(name), w))


def caption(text, x, y, w):
    if not text:
        return ""
    return ('<div style="%stext-align:center;font-size:12px;color:%s;">%s</div>'
            % (pos(x, y, w), GRAY, text))


def bullets(items, x=64, y=198, w=478, slot=66, accent=TEAL, fs=15.5):
    html = ""
    if RTL:
        ipos = "right:0;"
        tmargin = "margin-right:42px;"
    else:
        ipos = "left:0;"
        tmargin = "margin-left:42px;"
    for i, it in enumerate(items):
        cy = y + i * slot
        html += ('<div style="%s">'
                 '<div style="position:absolute;%stop:2px;width:28px;height:28px;border-radius:8px;'
                 'background:%s;direction:ltr;display:flex;align-items:center;justify-content:center;">%s</div>'
                 '<div style="%sfont-size:%spx;line-height:1.4;color:%s;%s">%s</div>'
                 '</div>' % (pos(x, cy, w), ipos, TEAL_LT, icon('check', accent, 16, 2.4),
                             tmargin, fs, GRAY, txtdir(), it))
    return html


# ------------------------------------------------------------------ slides ----
SLIDES = []


def add(html, accent=TEAL, full=False, p=True):
    bg = "background:%s;" % INK if full else "background:#FFFFFF;"
    foot = "" if not p else footer(len(SLIDES) + 1, accent)
    SLIDES.append('<section class="slide" style="%s%s">%s%s</section>'
                  % (bg, txtdir(), html, foot))


def deco_cross(x, y, sz):
    return ('<div style="%sopacity:.5;"><svg width="%d" height="%d" viewBox="0 0 24 24">'
            '<path d="M10 3h4v7h7v4h-7v7h-4v-7H3v-4h7z" fill="none" stroke="#2C4A50" stroke-width=".4"/></svg></div>'
            % (pos(x, y), sz, sz))


# ---- 1. COVER ----
def cover():
    # inline-block layout (a positioned display:flex mark mis-renders under an rtl page)
    mark = ('<div style="%sdirection:%s;">'
            '<span style="display:inline-block;vertical-align:middle;width:54px;height:54px;border-radius:14px;'
            'background:%s;direction:ltr;text-align:center;line-height:54px;box-shadow:0 8px 22px -8px %s;">'
            '<svg width="30" height="30" viewBox="0 0 24 24" style="vertical-align:middle;"><path d="M10 3h4v7h7v4h-7v7h-4v-7H3v-4h7z" fill="#fff"/></svg></span>'
            '<span style="display:inline-block;vertical-align:middle;margin:0 16px;color:#fff;text-align:%s;">'
            '<span style="display:block;font-size:21px;font-weight:700;letter-spacing:.3px;">%s</span>'
            '<span style="display:block;font-size:12px;color:#7FB7B4;letter-spacing:%s;">%s</span>'
            '</span></div>'
            % (pos(80, 70), DIR, TEAL, TEAL, ALIGN,
               T('Medical-Supply ERP', 'نظام توزيع المستلزمات الطبية'),
               ("0" if RTL else "1.5px"),
               T('DISTRIBUTION MANAGEMENT PLATFORM', 'منصّة إدارة التوزيع')))
    eyebrow = ('<div style="%sfont-size:14px;font-weight:700;letter-spacing:%s;color:%s;%s">%s</div>'
               % (pos(80, 250), ("0" if RTL else "4px"), "#5FB0AD", txtdir(),
                  T('LIVE SYSTEM DEMONSTRATION', 'عرض مباشر للنظام')))
    head_en = 'Run your entire business<br/>in <span style="color:#5FD4CF;">one system</span>.'
    head_ar = 'أدِر عملك بالكامل<br/>من <span style="color:#5FD4CF;">نظام واحد</span>.'
    head = ('<div style="%sfont-size:%dpx;font-weight:700;line-height:%s;color:#fff;%s">%s</div>'
            % (pos(80, 286, 1000), 56 if RTL else 60, "1.25" if RTL else "1.05", txtdir(), T(head_en, head_ar)))
    sub = ('<div style="%sfont-size:20px;line-height:1.5;color:#C7D6D8;%s">%s</div>'
           % (pos(80, 470, 900), txtdir(),
              T('From scattered Excel sheets to a single, connected platform &mdash; '
                'inventory, procurement, sales and accounting, in Arabic and English.',
                'من جداول إكسل المتفرّقة إلى منصّة واحدة مترابطة &mdash; '
                'المخزون والمشتريات والمبيعات والمحاسبة، بالعربية والإنجليزية.')))
    mside = "margin-left" if RTL else "margin-right"
    pill = ('<div style="%sdisplay:inline-block;padding:10px 18px;border-radius:24px;'
            'background:rgba(95,212,207,.12);border:1px solid rgba(95,212,207,.35);%s">'
            '<span style="display:inline-block;vertical-align:middle;%s:10px;">%s</span>'
            '<span style="display:inline-block;vertical-align:middle;font-size:14px;font-weight:700;color:#A9E4E0;">%s</span></div>'
            % (pos(80, 560), txtdir(), mside, icon('check', '#5FD4CF', 18, 2.4),
               T('Built on Odoo 18 Community + OCA &mdash; no per-user licence fees',
                 'مبنيّ على Odoo 18 Community و OCA &mdash; بلا رسوم تراخيص لكل مستخدم')))
    foot = ('<div style="%sfont-size:13px;color:#85A0A2;border-top:1px solid rgba(255,255,255,.12);padding-top:14px;%s">%s</div>'
            % (pos(80, 636, 1120), txtdir(),
               T('Live demonstration &nbsp;·&nbsp; %s &nbsp;·&nbsp; '
                 'Demo environment: <b style="color:#B9CDCE;">Sudan MedSupply Co. (Khartoum)</b> '
                 '&nbsp;·&nbsp; every figure shown is real data you can open and inspect' % DATE,
                 'عرض مباشر &nbsp;·&nbsp; %s &nbsp;·&nbsp; '
                 'بيئة العرض: <b style="color:#B9CDCE;">شركة السودان للمستلزمات الطبية (الخرطوم)</b> '
                 '&nbsp;·&nbsp; كل رقم تراه هنا بيانات حقيقية يمكنك فتحها وتدقيقها' % DATE)))
    band = '<div style="%sbackground:%s;"></div>' % (pos(0, 0, 12, 720), TEAL)
    add(band + mark + eyebrow + head + sub + pill + foot, full=True, p=False)


# ---- 2. THE PROBLEM ----
def problem():
    body = accent_bar(AMBER)
    body += kicker(T("The challenge today", "التحدّي اليوم"), AMBER)
    body += title(T('Excel got you started.<br/>It won&rsquo;t keep you safe.',
                    'إكسل أوصلك إلى هنا،<br/>لكنه لن يحميك بعد الآن.'), INK, 40, 80)
    cards = [
        ('database', T('No single source of truth', 'لا مصدر موحّد للحقيقة'),
         T('Every sheet is a different version. The numbers never quite agree.',
           'كل جدول نسخة مختلفة، والأرقام لا تتطابق أبداً.')),
        ('box', T('Stock is a guess', 'المخزون مجرّد تخمين'),
         T('On-hand quantities are only true the day someone counts them.',
           'الكميات المتوفّرة لا تكون صحيحة إلا يوم يجردها أحدهم.')),
        ('expiry', T('Medicine expires on the shelf', 'الدواء ينتهي على الرفّ'),
         T('No expiry or batch tracking means silent write-offs every month.',
           'بلا تتبّع للصلاحية والدُفعات، تتكرّر الخسائر الصامتة كل شهر.')),
        ('alert', T('Critical items run out', 'نفاد الأصناف الحرجة'),
         T('Nothing warns you when insulin or gloves quietly hit zero.',
           'لا شيء ينبّهك حين يصل الإنسولين أو القفازات إلى الصفر بهدوء.')),
        ('cash', T('Money you can&rsquo;t see', 'أموال لا تراها'),
         T('Who owes you, how much, how overdue? Buried across tabs.',
           'من يدين لك؟ وكم؟ ومنذ متى؟ كله مدفون بين التبويبات.')),
        ('lock', T('No accountability', 'لا مساءلة'),
         T('Anyone can change any cell &mdash; and no one knows who did.',
           'أي شخص يغيّر أي خلية &mdash; ولا أحد يعرف من فعلها.')),
    ]
    bl = "border-right:4px solid %s;" % AMBER if RTL else "border-left:4px solid %s;" % AMBER
    mside = "margin-left" if RTL else "margin-right"
    for i, (ic, t, d) in enumerate(cards):
        x = [64, 460, 856][i % 3]
        y = [228, 432][i // 3]
        body += ('<div style="%sbackground:#fff;border:1px solid %s;%sborder-radius:12px;padding:18px;%s">'
                 '<div style="display:flex;align-items:center;margin-bottom:8px;">'
                 '<span style="width:34px;height:34px;border-radius:9px;background:%s;direction:ltr;display:flex;flex:none;'
                 'align-items:center;justify-content:center;%s:11px;">%s</span>'
                 '<span style="font-size:16.5px;font-weight:700;color:%s;">%s</span></div>'
                 '<div style="font-size:13.5px;line-height:1.45;color:%s;">%s</div></div>'
                 % (pos(x, y, 360, 178), BORDER, bl, txtdir(), AMBER_LT, mside,
                    icon(ic, AMBER_DK, 19, 1.8), INK, t, GRAY, d))
    body += ('<div style="%sfont-size:15px;font-weight:700;color:%s;text-align:center;">%s</div>'
             % (pos(64, 632, 1152), AMBER_DK,
                T('Every one of these is a real cost &mdash; in cash, in spoilage, and in patient trust.',
                  'كل واحدة من هذه المشكلات خسارة حقيقية &mdash; في المال، وفي تلف المخزون، وفي ثقة المرضى.')))
    add(body, accent=AMBER)


# ---- generic single-screenshot capability ----
def cap(kick, ttl, blist, shot_name, cue, chiplist=None, accent=TEAL,
        cap_text=None, ttl_size=33):
    # bullets occupy the reading-start half; screenshot the other half
    body = accent_bar(accent)
    body += kicker(kick, accent)
    body += title(ttl, INK, ttl_size, 80)
    n = len(blist)
    slot = 92 if n <= 3 else 74
    body += bullets(blist, y=190, w=470, slot=slot, accent=accent)
    sw = fit_w(shot_name, 650, 393)          # keep caption clear of the cue band
    sx = 566 + (650 - sw) // 2
    body += shot(shot_name, sx, 158, sw)
    cap_y = 158 + 26 + disp_h(shot_name, sw) + 9
    body += caption(cap_text or "", sx, cap_y, sw)
    if chiplist:
        body += chips(chiplist, x=64, y=494, width=478, accent=accent)
    body += live_cue(cue)
    add(body, accent=accent)


# ---- generic dual-screenshot capability ----
def cap2(kick, ttl, lead, shots, cue, accent=TEAL, ttl_size=34):
    body = accent_bar(accent)
    body += kicker(kick, accent)
    body += title(ttl, INK, ttl_size, 80)
    body += ('<div style="%sfont-size:16px;line-height:1.45;color:%s;%s">%s</div>'
             % (pos(64, 168, 1152), GRAY, txtdir(), lead))
    w = min(fit_w(name, 512, 309) for name, _ in shots)   # equal width, clear of cue
    gap = 40
    total = 2 * w + gap
    x1 = (1280 - total) // 2
    x2 = x1 + w + gap
    y = 244
    for (name, cp), x in zip(shots, (x1, x2)):
        body += shot(name, x, y, w)
        body += caption(cp, x, y + 26 + disp_h(name, w) + 10, w)
    body += live_cue(cue)
    add(body, accent=accent)


# ---- compare table ----
def compare():
    body = accent_bar(TEAL)
    body += kicker(T("The bottom line", "الخلاصة"), TEAL)
    body += title(T('Excel today vs. your new system', 'إكسل اليوم مقابل نظامك الجديد'), INK, 38, 80)
    rows = [
        (T('Single source of truth', 'مصدر موحّد للحقيقة'), T('Many files, many versions', 'ملفات كثيرة ونسخ متعدّدة'), T('One shared database', 'قاعدة بيانات واحدة مشتركة')),
        (T('Real-time stock levels', 'مستويات مخزون لحظية'), T('Only after a manual count', 'فقط بعد جرد يدوي'), T('Live, always current', 'حيّة ومحدّثة دائماً')),
        (T('Expiry & batch tracking', 'تتبّع الصلاحية والدُفعات'), T('None', 'غير موجود'), T('Per-lot, with FEFO', 'لكل دُفعة، مع FEFO')),
        (T('Re-order alerts', 'تنبيهات إعادة الطلب'), T('You find out too late', 'تكتشف بعد فوات الأوان'), T('Automatic min/max', 'حد أدنى/أقصى تلقائي')),
        (T('Multi-currency (USD / SDG)', 'تعدّد العملات (دولار/جنيه)'), T('Manual, error-prone', 'يدوي وعُرضة للخطأ'), T('Dated rates, auto-converted', 'أسعار مؤرّخة وتحويل تلقائي')),
        (T('Invoicing & 15% tax', 'الفوترة وضريبة 15%'), T('Typed by hand', 'تُكتب يدوياً'), T('One click from the order', 'بنقرة من الطلب')),
        (T('Who owes you / cash view', 'من يدين لك / السيولة'), T('Buried in tabs', 'مدفون في التبويبات'), T('Live dashboard & aged report', 'لوحة حيّة وتقرير أعمار')),
        (T('Per-person access & audit', 'وصول ومساءلة لكل شخص'), T('Anyone edits anything', 'أي أحد يعدّل أي شيء'), T('Roles + full history', 'أدوار + سجلّ كامل')),
        (T('Arabic + English', 'عربي + إنجليزي'), T('Whatever you build', 'ما تبنيه بنفسك'), T('Built-in, right-to-left', 'مدمج، من اليمين لليسار')),
        (T('Room to grow', 'مساحة للنمو'), T('Hits a ceiling', 'يصطدم بسقف'), T('Add apps & custom features', 'أضِف تطبيقات وميزات مخصّصة')),
    ]
    CAPW, EXW, ERPW = 418, 358, 360
    mside = "margin-left" if RTL else "margin-right"
    hdr_uc = "" if RTL else "text-transform:uppercase;letter-spacing:1px;"

    # A real <table> with dir=DIR: WeasyPrint mirrors the columns natively for RTL
    # (Capability column on the right in AR) — far more reliable than flexbox,
    # which mis-mirrors inside a direction:rtl page.
    def cell_inner(ic, ic_color, text):
        if ic is None:
            return text
        g = '<span style="%s:8px;display:inline-block;vertical-align:middle;">%s</span>' % (mside, icon(ic, ic_color, 16, 2.4))
        return g + '<span style="vertical-align:middle;">%s</span>' % text

    th = ('<th style="width:%dpx;padding:0 10px 8px;font-size:13px;font-weight:700;text-align:%s;'
          'border-bottom:2px solid %s;%s%s">%s</th>')
    thead = ('<tr>'
             + th % (CAPW, ALIGN, INK, hdr_uc, "color:%s;" % GRAY_LT, T('Capability', 'الميزة'))
             + th % (EXW, ALIGN, INK, hdr_uc, "color:%s;" % RED, T('Excel today', 'إكسل اليوم'))
             + th % (ERPW, ALIGN, INK, hdr_uc, "color:%s;" % TEAL_DK, T('Your new ERP', 'نظامك الجديد'))
             + '</tr>')
    body_rows = ""
    for i, (cap_, ex, erp) in enumerate(rows):
        bg = "#FFFFFF" if i % 2 else BG_SOFT
        td = ('<td style="height:42px;padding:0 10px;background:%s;text-align:%s;font-size:%spx;'
              'font-weight:%s;color:%s;%s">%s</td>')
        body_rows += ('<tr>'
                      + td % (bg, ALIGN, "14.5", "700", INK, "", cell_inner(None, None, cap_))
                      + td % (bg, ALIGN, "13.5", "400", GRAY, "", cell_inner('x', RED, ex))
                      + td % (bg, ALIGN, "13.5", "700", TEAL_DK, "", cell_inner('check', TEAL, erp))
                      + '</tr>')
    table = ('<table dir="%s" style="width:1152px;border-collapse:collapse;table-layout:fixed;">'
             '<thead>%s</thead><tbody>%s</tbody></table>' % (DIR, thead, body_rows))
    body += '<div style="%s">%s</div>' % (pos(64, 170, 1152), table)
    add(body, accent=TEAL)


# ---- cost & growth ----
def cost_growth():
    body = accent_bar(TEAL)
    body += kicker(T("What it costs & how it grows", "التكلفة وآفاق النموّ"), TEAL)
    body += title(T('No per-user licence fees &mdash; and room to grow',
                    'بلا رسوم تراخيص لكل مستخدم &mdash; ومساحة للنمو'), INK, 33, 80)
    body += bullets([
        T('Built on <b>Odoo 18 Community + OCA</b> &mdash; the software licence is <b>free</b>.',
          'مبنيّ على <b>Odoo 18 Community و OCA</b> &mdash; ترخيص البرمجية <b>مجاني</b>.'),
        T('You invest in <b>setup, training and support</b> &mdash; not in monthly per-seat fees.',
          'تستثمر في <b>الإعداد والتدريب والدعم</b> &mdash; لا في رسوم شهرية لكل مقعد.'),
        T('Add users as your team grows at <b>no extra licence cost</b>. You <b>own your data</b>.',
          'أضِف مستخدمين كلما نما فريقك <b>بلا كلفة ترخيص إضافية</b>. و<b>بياناتك ملكك</b>.'),
    ], y=192, w=448, slot=86)
    # module grid on the other half
    gx = 552
    active = T('Inventory · Purchase · Sales · Accounting · Contacts', '').split(' · ') if not RTL else \
        ['المخزون', 'المشتريات', 'المبيعات', 'المحاسبة', 'جهات الاتصال']
    if not RTL:
        active = ['Inventory', 'Purchase', 'Sales', 'Accounting', 'Contacts']
    avail = (['Manufacturing', 'Point of Sale', 'Barcode', 'HR & Payroll', 'CRM',
              'e-Commerce', 'Projects', 'Maintenance', 'Quality', 'Fleet'] if not RTL else
             ['التصنيع', 'نقاط البيع', 'الباركود', 'الموارد البشرية', 'إدارة العلاقات',
              'التجارة الإلكترونية', 'المشاريع', 'الصيانة', 'الجودة', 'الأسطول'])
    hdr_uc = "" if RTL else "text-transform:uppercase;letter-spacing:1.5px;"
    dot = ('<span style="display:inline-block;width:8px;height:8px;border-radius:50%%;'
           'background:%s;vertical-align:middle;%s:8px;"></span>')
    mside = "margin-left" if RTL else "margin-right"
    body += ('<div style="%sfont-size:12px;font-weight:700;%scolor:%s;%s">%s</div>'
             % (pos(gx, 186, 664), hdr_uc, TEAL_DK, txtdir(), T('Running today', 'يعمل اليوم')))
    act = ""
    for a in active:
        act += ('<span style="display:inline-block;%s:10px;margin-bottom:10px;background:%s;'
                'border:1px solid %s55;border-radius:22px;padding:8px 15px;font-size:13.5px;'
                'font-weight:700;color:%s;white-space:nowrap;vertical-align:middle;">%s%s</span>'
                % (mside, TEAL_LT, TEAL, TEAL_DK, dot % (TEAL, mside), a))
    body += '<div style="%s%s">%s</div>' % (pos(gx, 208, 664), txtdir(), act)
    body += ('<div style="%sfont-size:12px;font-weight:700;%scolor:%s;%s">%s</div>'
             % (pos(gx, 286, 664), hdr_uc, GRAY_LT, txtdir(), T('Available to switch on', 'متاح للتفعيل')))
    av = ""
    for a in avail:
        av += ('<span style="display:inline-block;%s:10px;margin-bottom:10px;background:#fff;'
               'border:1px dashed %s;border-radius:22px;padding:8px 15px;font-size:13.5px;'
               'font-weight:700;color:%s;white-space:nowrap;vertical-align:middle;">%s%s</span>'
               % (mside, BORDER, SLATE, dot % (GRAY_LT, mside), a))
    body += '<div style="%s%s">%s</div>' % (pos(gx, 308, 664), txtdir(), av)
    body += note_band(
        T('Enterprise ERPs charge <b>per user, per month</b> &mdash; for the same features you just saw working.',
          'أنظمة ERP التجارية تتقاضى رسماً <b>لكل مستخدم شهرياً</b> &mdash; لنفس الميزات التي رأيتها تعمل للتو.'))
    add(body, accent=TEAL)


# ---- switching (off Excel) ----
def switching():
    body = accent_bar(TEAL)
    body += kicker(T("Moving off Excel", "الانتقال من إكسل"), TEAL)
    body += title(T('A low-risk switch &mdash; with training and support',
                    'انتقال منخفض المخاطر &mdash; مع تدريب ودعم'), INK, 36, 80)
    cards = [
        ('upload', T('Import your data', 'استورد بياناتك'),
         T('Products, customers, suppliers and opening stock import straight from your '
           'Excel / CSV files. Run alongside Excel, go live when you&rsquo;re ready.',
           'المنتجات والعملاء والمورّدون والمخزون الافتتاحي تُستورَد مباشرةً من ملفات '
           'إكسل / CSV. شغّله بالتوازي مع إكسل، وانطلق حين تجهز.')),
        ('book', T('Train your team', 'درِّب فريقك'),
         T('A <b>17-chapter bilingual manual</b> with 53 real screenshots, plus hands-on, '
           'role-based training on your own data.',
           '<b>دليل من 17 فصلاً بلغتين</b> مع 53 لقطة حقيقية، إضافةً إلى تدريب عملي '
           'حسب الدور على بياناتك.')),
        ('cloud', T('Run it anywhere, safely', 'شغّله بأمان أينما شئت'),
         T('Your own server or the cloud, any browser, <b>encrypted login</b>, role-based '
           'access and <b>automated daily backups</b>.',
           'خادمك الخاص أو السحابة، أي متصفّح، <b>دخول مشفَّر</b>، صلاحيات حسب الدور، '
           'و<b>نسخ احتياطي يومي تلقائي</b>.')),
    ]
    w = 360
    gap = (1152 - 3 * w) // 2
    for i, (ic, t, d) in enumerate(cards):
        x = 64 + i * (w + gap)
        body += ('<div style="%sbackground:#fff;border:1px solid %s;border-top:4px solid %s;'
                 'border-radius:14px;padding:24px 22px;%s">'
                 '<span style="width:48px;height:48px;border-radius:13px;background:%s;direction:ltr;display:flex;'
                 'align-items:center;justify-content:center;margin-bottom:16px;">%s</span>'
                 '<div style="font-size:19px;font-weight:700;color:%s;margin-bottom:10px;">%s</div>'
                 '<div style="font-size:14px;line-height:1.5;color:%s;">%s</div></div>'
                 % (pos(x, 210, w, 322), BORDER, TEAL, txtdir(), TEAL_LT,
                    icon(ic, TEAL, 25, 1.8), INK, t, GRAY, d))
    body += note_band(
        T('Most of what you keep in Excel imports in a single afternoon &mdash; and ongoing support is part of it.',
          'معظم ما تحتفظ به في إكسل يُستورَد خلال ساعات &mdash; والدعم المستمر جزء من الخدمة.'))
    add(body, accent=TEAL)


# ---- roadmap ----
def roadmap():
    body = accent_bar(TEAL)
    body += kicker(T("Getting started", "البداية"), TEAL)
    body += title(T('Live in about four weeks', 'التشغيل خلال نحو أربعة أسابيع'), INK, 40, 80)
    phases = [
        (T('Week 1', 'الأسبوع 1'), T('Configure', 'الإعداد'),
         [T('Company, branches & users', 'الشركة والفروع والمستخدمون'),
          T('Warehouses & locations', 'المستودعات والمواقع'),
          T('Taxes & currencies', 'الضرائب والعملات')]),
        (T('Week 2', 'الأسبوع 2'), T('Import data', 'استيراد البيانات'),
         [T('Products & categories', 'المنتجات والفئات'),
          T('Customers & suppliers', 'العملاء والمورّدون'),
          T('Opening stock from Excel', 'المخزون الافتتاحي من إكسل')]),
        (T('Week 3', 'الأسبوع 3'), T('Train & parallel', 'تدريب وتوازٍ'),
         [T('Role-based training', 'تدريب حسب الدور'),
          T('Run alongside Excel', 'التشغيل بالتوازي مع إكسل'),
          T('Build the team&rsquo;s confidence', 'بناء ثقة الفريق')]),
        (T('Week 4', 'الأسبوع 4'), T('Go live', 'الانطلاق'),
         [T('Switch over fully', 'التحوّل الكامل'),
          T('Real orders & invoices', 'طلبات وفواتير حقيقية'),
          T('Ongoing support begins', 'يبدأ الدعم المستمر')]),
    ]
    w = 264
    gap = (1152 - 4 * w) // 3
    body += '<div style="%sbackground:%s;"></div>' % (pos(64 + 30, 286, 1152 - 60, 3), BORDER)
    for i, (wk, t, pts) in enumerate(phases):
        x = 64 + i * (w + gap)
        cside = "left:%dpx" % (1280 - (x + 18) - 26) if RTL else "left:%dpx" % (x + 18)
        body += ('<div style="position:absolute;%s;top:274px;width:26px;height:26px;border-radius:50%%;'
                 'background:%s;color:#fff;text-align:center;line-height:26px;'
                 'font-size:13px;font-weight:700;">%d</div>' % (cside, TEAL, i + 1))
        items = "".join('<div style="font-size:13.5px;line-height:1.4;color:%s;margin-bottom:9px;'
                        'padding-%s:16px;position:relative;%s">'
                        '<span style="position:absolute;%s:0;top:7px;width:6px;height:6px;border-radius:50%%;'
                        'background:%s;"></span>%s</div>'
                        % (GRAY, ALIGN, txtdir(), ALIGN, TEAL, p) for p in pts)
        body += ('<div style="%sbackground:#fff;border:1px solid %s;border-top:4px solid %s;border-radius:14px;'
                 'padding:18px;%s">'
                 '<div style="font-size:12px;font-weight:700;%scolor:%s;">%s</div>'
                 '<div style="font-size:21px;font-weight:700;color:%s;margin:4px 0 12px;">%s</div>%s</div>'
                 % (pos(x, 320, w, 250), BORDER, TEAL, txtdir(),
                    ("" if RTL else "letter-spacing:1.5px;text-transform:uppercase;"), TEAL_DK, wk, INK, t, items))
    body += ('<div style="%sbackground:%s;border-radius:12px;display:flex;align-items:center;justify-content:center;">'
             '<span style="font-size:16px;color:%s;text-align:center;">%s</span></div>'
             % (pos(64, 600, 1152, 54), TEAL_LT, INK,
                T('A clear, low-risk path &mdash; <b style="color:%s;">you&rsquo;re never without a working system for a single day.</b>' % TEAL_DK,
                  'مسار واضح ومنخفض المخاطر &mdash; <b style="color:%s;">لن تبقى يوماً واحداً بلا نظام يعمل.</b>' % TEAL_DK)))
    add(body, accent=TEAL)


# ---- CTA / close ----
def close():
    band = '<div style="%sbackground:%s;"></div>' % (pos(0, 0, 12, 720), TEAL)
    k = ('<div style="%sfont-size:14px;font-weight:700;letter-spacing:%s;color:%s;%s">%s</div>'
         % (pos(80, 96), ("0" if RTL else "4px"), "#5FB0AD", txtdir(), T('NEXT STEPS', 'الخطوات التالية')))
    t = ('<div style="%sfont-size:48px;font-weight:700;line-height:%s;color:#fff;%s">%s</div>'
         % (pos(80, 128, 1000), "1.25" if RTL else "1.08", txtdir(),
            T('Let&rsquo;s set up <span style="color:#5FD4CF;">your</span> business<br/>in the system.',
              'لنُجهّز <span style="color:#5FD4CF;">عملك</span><br/>داخل النظام.')))
    steps = [
        ('upload', T('We take your real product & customer list', 'نأخذ قائمة منتجاتك وعملائك الحقيقية')),
        ('layers', T('We configure a private demo with your own data', 'نُعدّ نسخة تجريبية خاصة ببياناتك')),
        ('users', T('You and your team test-drive it, hands-on', 'تجرّبه أنت وفريقك عملياً')),
        ('pin', T('We agree a go-live date that suits you', 'نتّفق على موعد انطلاق يناسبك')),
    ]
    body = band + k + t
    mside = "margin-left" if RTL else "margin-right"
    for i, (ic, txt) in enumerate(steps):
        y = 286 + i * 62
        # positioned block + inline-block children (a positioned display:flex row
        # mis-renders under an rtl page); explicit left mirrors it.
        geom = "position:absolute;left:%dpx;top:%dpx;width:820px;direction:%s;" % ((1280 - 80 - 820) if RTL else 80, y, DIR)
        body += ('<div style="%s">'
                 '<span style="display:inline-block;vertical-align:middle;width:40px;height:40px;border-radius:11px;'
                 'background:rgba(95,212,207,.14);direction:ltr;text-align:center;line-height:40px;'
                 'border:1px solid rgba(95,212,207,.3);%s:16px;">%s</span>'
                 '<span style="display:inline-block;vertical-align:middle;font-size:18px;color:#DCE8E9;">%s</span></div>'
                 % (geom, mside, icon(ic, '#7FE3DE', 20, 1.8), txt))
    body += ('<div style="%sfont-size:22px;font-weight:700;color:#fff;line-height:1.4;'
             'border-top:1px solid rgba(255,255,255,.14);padding-top:20px;%s">%s</div>'
             % (pos(80, 568, 1000), txtdir(),
                T('Everything you saw today was real.&nbsp; <span style="color:#5FD4CF;">Next, let&rsquo;s make it yours.</span>',
                  'كل ما رأيته اليوم حقيقي.&nbsp; <span style="color:#5FD4CF;">والخطوة التالية أن نجعله لك.</span>')))
    body += ('<div style="%sfont-size:13px;color:#85A0A2;%s">%s</div>'
             % (pos(80, 662, 1000), txtdir(),
                T('Medical-Supply Distribution ERP &nbsp;·&nbsp; Built on Odoo 18 Community + OCA &nbsp;·&nbsp; %s' % DATE,
                  'نظام توزيع المستلزمات الطبية &nbsp;·&nbsp; مبنيّ على Odoo 18 Community و OCA &nbsp;·&nbsp; %s' % DATE)))
    add(body, full=True, p=False)


# ============================================================ BUILD ORDER ====
cover()                                                                 # 1
problem()                                                               # 2

# 3 — the solution: one connected, live system (concept in bullets + real apps)
cap(T("The solution", "الحل"),
    T('One connected system &mdash; enter once, it flows everywhere',
      'نظام واحد مترابط &mdash; أدخِل البيانات مرّة، فتتدفّق إلى كل مكان'),
    [T('<b>Seven connected apps</b>, one login, one database &mdash; Contacts, Sales, Purchase, Inventory, Accounting and Dashboards.',
       '<b>سبعة تطبيقات مترابطة</b> بتسجيل دخول واحد وقاعدة بيانات واحدة &mdash; جهات الاتصال والمبيعات والمشتريات والمخزون والمحاسبة ولوحات التحكّم.'),
     T('A purchase updates stock; a <b>sale updates stock AND raises the invoice AND posts to the books</b> &mdash; automatically.',
       'الشراء يُحدِّث المخزون؛ و<b>البيع يُحدِّث المخزون ويُصدِر الفاتورة ويُقيِّدها في الدفاتر</b> &mdash; تلقائياً.'),
     T('<b>Web-based</b> &mdash; open it from the office, the warehouse, or a phone. Nothing to install on each PC.',
       '<b>يعمل عبر الويب</b> &mdash; افتحه من المكتب أو المستودع أو الهاتف. لا شيء يُثبَّت على كل جهاز.')],
    'apps_home.png',
    T('Open the 9-dot app launcher and show the live apps.',
      'افتح مشغّل التطبيقات (الشبكة ذات النقاط التسع) واعرض التطبيقات الحيّة.'),
    chiplist=[T('7 connected apps', '7 تطبيقات مترابطة'), T('One login', 'دخول واحد'), T('Web-based', 'عبر الويب')],
    accent=TEAL, cap_text=T('The real, themed app launcher', 'مشغّل التطبيقات الحقيقي'))

# 4 — catalogue & live stock
cap(T("01 · Your catalogue", "01 · كتالوج منتجاتك"),
    T('Every product, with live stock &mdash; one source of truth',
      'كل منتج بمخزون لحظي &mdash; مصدر واحد للحقيقة'),
    [T('<b>All 10 medical items</b> in one catalogue: Pharmaceuticals, Consumables and Devices.',
       '<b>جميع الأصناف الطبية العشرة</b> في كتالوج واحد: أدوية ومستهلكات وأجهزة.'),
     T('<b>Live on-hand</b> that updates itself: Insulin 50, Paracetamol 150, Gloves 60 units.',
       '<b>كميات متوفّرة لحظية</b> تتحدّث ذاتياً: إنسولين 50، باراسيتامول 150، قفازات 60 وحدة.'),
     T('Internal references, cost, sale price and 15% tax built into every product.',
       'مرجع داخلي وتكلفة وسعر بيع وضريبة 15% مضمّنة في كل منتج.')],
    'products_list.png',
    T('Open Inventory ▸ Products, search &ldquo;Insulin&rdquo; and open its card.',
      'افتح المخزون ▸ المنتجات، وابحث عن «الإنسولين» وافتح بطاقته.'),
    chiplist=[T('10 products', '10 منتجات'), T('3 categories', '3 فئات'),
              T('2 warehouses', 'مستودعان'), T('Live on-hand', 'مخزون لحظي')],
    accent=TEAL, cap_text=T('The product catalogue with live on-hand quantities',
                            'كتالوج المنتجات مع الكميات المتوفّرة اللحظية'))

# 5 — expiry / batches / cold chain
cap(T("02 · Medical traceability", "02 · التتبّع الطبي"),
    T('Never write off expired stock again', 'لا مزيد من شطب المخزون منتهي الصلاحية'),
    [T('<b>Every batch carries its expiry date</b> &mdash; and the system sells oldest-first (FEFO) on its own.',
       '<b>كل دُفعة تحمل تاريخ صلاحيتها</b> &mdash; والنظام يبيع الأقدم أولاً (FEFO) تلقائياً.'),
     T('<b>Cold-chain items</b> like Insulin live in a dedicated <b>Cold Storage (2&ndash;8&deg;C)</b> location.',
       '<b>أصناف سلسلة التبريد</b> مثل الإنسولين تُحفظ في موقع <b>تخزين بارد مخصّص (2&ndash;8&deg;م)</b>.'),
     T('<b>Full recall traceability</b> &mdash; find every unit of a bad lot in seconds.',
       '<b>تتبّع كامل للاسترجاع</b> &mdash; اعثر على كل وحدة من دُفعة معيبة في ثوانٍ.')],
    'lots_list.png',
    T('Inventory ▸ Lots/Serial Numbers &mdash; open LOT-GULF-01 (Insulin) and show its expiry.',
      'المخزون ▸ الدُفعات/الأرقام التسلسلية &mdash; افتح LOT-GULF-01 (إنسولين) واعرض صلاحيتها.'),
    chiplist=[T('Lot + expiry', 'دُفعة + صلاحية'), T('FEFO removal', 'صرف FEFO'),
              T('Cold Storage 2&ndash;8°C', 'تخزين بارد 2&ndash;8°'), T('Recall-ready', 'جاهز للاسترجاع')],
    accent=TEAL, cap_text=T('Lots grouped by location &mdash; note Cold Storage (2&ndash;8°C)',
                            'الدُفعات مجمَّعة حسب الموقع &mdash; لاحظ التخزين البارد (2&ndash;8°م)'))

# 6 — auto reorder
cap(T("03 · Never run out", "03 · لا تنفد أبداً"),
    T('The system watches your stock so you don&rsquo;t have to',
      'النظام يراقب مخزونك نيابةً عنك'),
    [T('<b>Set a min / max per item</b>: Insulin 20/80, Paracetamol 50/200, Gloves 30/120.',
       '<b>حدِّد حدّاً أدنى/أقصى لكل صنف</b>: إنسولين 20/80، باراسيتامول 50/200، قفازات 30/120.'),
     T('When stock hits the minimum, it <b>flags &mdash; or drafts the purchase order &mdash; automatically</b>.',
       'عند بلوغ الحدّ الأدنى، <b>ينبّه النظام &mdash; أو يُنشئ أمر الشراء &mdash; تلقائياً</b>.'),
     T('No more learning about a stockout from an unhappy customer.',
       'لن تعرف بنفاد صنف من شكوى زبون غاضب بعد الآن.')],
    'reordering_rules.png',
    T('Inventory ▸ Operations ▸ Reordering Rules &mdash; show On-Hand vs Min/Max.',
      'المخزون ▸ العمليات ▸ قواعد إعادة الطلب &mdash; اعرض المتوفّر مقابل الأدنى/الأقصى.'),
    chiplist=[T('Min / Max rules', 'قواعد حد أدنى/أقصى'), T('Auto purchase orders', 'أوامر شراء تلقائية'),
              T('Per warehouse', 'لكل مستودع')],
    accent=TEAL, cap_text=T('Reordering rules with live on-hand vs min/max',
                            'قواعد إعادة الطلب: المتوفّر مقابل الأدنى/الأقصى'))

# 7 — multi-currency (dual)
cap2(T("04 · Multi-currency", "04 · تعدّد العملات"),
     T('Buy in USD, sell in SDG &mdash; your margin protected automatically',
       'اشترِ بالدولار وبِع بالجنيه &mdash; هامش ربحك محميّ تلقائياً'),
     T('Import from Gulf MedTrade in US dollars and sell to hospitals in Sudanese pounds. The system keeps a '
       '<b>dated exchange-rate history</b> and converts every document for you &mdash; no manual maths, no guesswork.',
       'استورد من «جلف ميد-تريد» بالدولار وبِع للمستشفيات بالجنيه السوداني. يحتفظ النظام بـ'
       '<b>سجلّ أسعار صرف مؤرّخ</b> ويحوّل كل مستند نيابةً عنك &mdash; بلا حسابات يدوية ولا تخمين.'),
     [('po_usd.png', T('Purchase P00002 &mdash; $1,288.00  ⇄  5,796,000 SDG', 'أمر شراء P00002 &mdash; 1,288.00 $  ⇄  5,796,000 ج.س')),
      ('currency_usd.png', T('Dated FX history &mdash; 1 USD = 2,400 → 4,500 SDG', 'سجلّ صرف مؤرّخ &mdash; 1 دولار = 2,400 ← 4,500 ج.س'))],
     T('Purchase ▸ open P00002 (Gulf MedTrade) &mdash; show the $ total and its SDG equivalent.',
       'المشتريات ▸ افتح P00002 &mdash; اعرض الإجمالي بالدولار ومقابله بالجنيه.'),
     accent=INDIGO)

# 8 — quote to cash (dual)
cap2(T("05 · Quote to cash", "05 · من العرض إلى التحصيل"),
     T('From quotation to a paid invoice &mdash; in a few clicks',
       'من عرض السعر إلى فاتورة مدفوعة &mdash; بنقرات قليلة'),
     T('One confirmed order creates the delivery <b>and</b> the invoice; the 15% tax is calculated for you and '
       'nothing is re-typed. The same order you sell becomes the invoice you collect.',
       'طلب واحد مؤكَّد يُنشئ التسليم <b>و</b>الفاتورة معاً؛ تُحتسب ضريبة 15% تلقائياً ولا يُعاد إدخال شيء. '
       'الطلب نفسه الذي تبيعه يصبح الفاتورة التي تحصّلها.'),
     [('sale_order.png', T('Order S00001 &mdash; Khartoum Teaching Hospital · 2,038,950 SDG', 'طلب S00001 &mdash; مستشفى الخرطوم التعليمي · 2,038,950 ج.س')),
      ('customer_invoice.png', T('Invoice INV/2026/00001 &mdash; Posted & Paid', 'فاتورة INV/2026/00001 &mdash; مُرحَّلة ومدفوعة'))],
     T('Sales ▸ open S00001, then its invoice &mdash; show the green PAID banner.',
       'المبيعات ▸ افتح S00001 ثم فاتورته &mdash; اعرض شارة «مدفوعة» الخضراء.'),
     accent="#0F8A5F")

# 9 — receivables / cash position
cap(T("06 · Your money", "06 · أموالك"),
    T('Know who owes you &mdash; and see your cash the moment you log in',
      'اعرف من يدين لك &mdash; وشاهد سيولتك لحظة دخولك'),
    [T('<b>Live dashboard</b>: 3 invoices unpaid (3,966,350 SDG), 2 already overdue.',
       '<b>لوحة حيّة</b>: 3 فواتير غير مدفوعة (3,966,350 ج.س)، اثنتان متأخّرتان.'),
     T('<b>Bank of Khartoum balance 3,924,950 SDG</b> at a glance, with a trend.',
       '<b>رصيد بنك الخرطوم 3,924,950 ج.س</b> بلمحة واحدة، مع اتجاهه.'),
     T('One click prints an <b>Aged Receivable</b> report &mdash; chase the right people, on time.',
       'نقرة واحدة تطبع تقرير <b>أعمار الذمم</b> &mdash; طالِب الأشخاص الصحيحين في الوقت المناسب.')],
    'accounting_dashboard.png',
    T('Accounting ▸ Dashboard &mdash; point at Unpaid / Late and the live bank balance.',
      'المحاسبة ▸ لوحة التحكّم &mdash; أشِر إلى غير المدفوع/المتأخّر والرصيد البنكي الحيّ.'),
    chiplist=[T('Unpaid & overdue', 'غير مدفوع ومتأخّر'), T('Bank balances live', 'أرصدة بنكية حيّة'),
              T('Aged · P&L · Balance Sheet', 'أعمار · أرباح · ميزانية')],
    accent=VIOLET, cap_text=T('The Accounting dashboard &mdash; invoices, bills and bank, live',
                              'لوحة المحاسبة &mdash; الفواتير والمطالبات والبنك، مباشرةً'),
    ttl_size=31)

# 10 — roles, control & Arabic
cap(T("07 · Control & language", "07 · التحكّم واللغة"),
    T('Each person sees only their part &mdash; in Arabic or English',
      'كل شخص يرى ما يخصّه فقط &mdash; بالعربية أو الإنجليزية'),
    [T('<b>Six role-based users</b>: Manager, Procurement, Sales, Warehouse, Accountant, Admin.',
       '<b>ستة مستخدمين حسب الدور</b>: مدير، مشتريات، مبيعات، مستودع، محاسب، مسؤول نظام.'),
     T('The <b>warehouse keeper can&rsquo;t edit prices</b>; the <b>sales rep can&rsquo;t see the books</b>. Every change is logged.',
       '<b>أمين المستودع لا يعدّل الأسعار</b>؛ و<b>مندوب المبيعات لا يرى الدفاتر</b>. وكل تغيير مسجَّل.'),
     T('The whole system &mdash; and the 17-chapter manual &mdash; in <b>full Arabic, right-to-left</b>, per user.',
       'النظام بأكمله &mdash; ودليل المستخدم من 17 فصلاً &mdash; <b>بالعربية الكاملة، من اليمين لليسار</b>، لكل مستخدم.')],
    'user_role.png',
    T('Settings ▸ Users ▸ open Layla (General Manager) ▸ Access Rights; then switch a user to Arabic and reload.',
      'الإعدادات ▸ المستخدمون ▸ افتح ليلى (المديرة العامة) ▸ حقوق الوصول؛ ثم بدّل مستخدماً إلى العربية وأعد التحميل.'),
    chiplist=[T('6 user roles', '6 أدوار'), T('Full audit trail', 'سجلّ تدقيق كامل'),
              T('Full Arabic RTL', 'عربية كاملة RTL'), T('Bilingual manual', 'دليل ثنائي اللغة')],
    accent=SLATE, cap_text=T('Access Rights for Layla (General Manager)',
                             'حقوق الوصول لليلى (المديرة العامة)'))

# ----- decision -----
compare()                                                               # 11
cost_growth()                                                           # 12
switching()                                                            # 13
roadmap()                                                              # 14
close()                                                                # 15

# ----------------------------------------------------------------- assemble ----
TOTAL = len(SLIDES)
CSS = (
    "*{margin:0;padding:0;box-sizing:border-box;}"
    + font_face() +
    "html,body{font-family:'Alexandria',sans-serif;-webkit-font-smoothing:antialiased;}"
    "@page{size:1280px 720px;margin:0;}"
    ".slide{position:relative;width:1280px;height:720px;overflow:hidden;page-break-after:always;}"
    ".slide:last-child{page-break-after:auto;}"
)
html = ("<!DOCTYPE html><html dir='%s'><head><meta charset='utf-8'><style>%s</style></head><body>%s</body></html>"
        % (DIR, CSS, "".join(s.replace("%%T%%", str(TOTAL)) for s in SLIDES)))

suffix = "AR" if RTL else "EN"
out_html = os.path.join(OUT_DIR, "Medical-Supply_ERP_Demo_Deck_%s.html" % suffix)
with open(out_html, "w", encoding="utf-8") as f:
    f.write(html)
print("Wrote %s  (%d slides, %.1f MB, lang=%s)" % (out_html, TOTAL, len(html) / 1e6, LANG))
