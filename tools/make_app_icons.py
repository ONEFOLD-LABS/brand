"""ONEFOLD LABS app icons and app colour sets, computed from the brand tokens.

Follows "The app family" in the brand book (README.md): a disc in the app's colour, gradient one
step lighter at the top left to one step darker at the bottom right, the app's motif cut out as
a real hole (computed geometry, one shape, no mask). 512 viewBox, disc radius 226, transparent
ground, no tile. Motifs are round-capped strokes: 30 px in `icon.svg` (from 48 px), 44 px in the
simplified `icon-small.svg` (16 to 32 px).

Inputs: `app-<name>` colours and the neutral tokens from tokens/tokens.json. StudioCraft's
shipped icon is reproduced unchanged. Outputs in apps/: <app>/icon.svg, <app>/icon-small.svg,
palette.json (ramps, UI accents per theme, semantic and domain colours, all contrast-checked).

Run from the repository root:  uv run --with shapely python tools/make_app_icons.py
"""
import json
import math
import sys
from pathlib import Path

from shapely.geometry import LineString, Point
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).parent))
from oklch import contrast, hex_to_rgb, oklch, rgb_to_oklch

ROOT = Path(__file__).resolve().parent.parent

SIZE, C0, RADIUS = 512, 256, 226
LINE, LINE_SMALL = 30, 44

# Gradient steps around the app colour (OKLCH lightness) and the dark-theme accent, modelled on
# the brand's petrol (#0e5a64 light, #4fa9b3 with near-black text in the dark theme).
STEP_LIGHT, STEP_DARK = 0.12, -0.08
DARK_ACCENT_L = 0.70

# ------------------------------------------------------------------ geometry helpers


def stroke(points, width):
    return LineString(points).buffer(width / 2, quad_segs=16)


def dot(x, y, r):
    return Point(x, y).buffer(r, quad_segs=32)


def bezier(p0, p1, p2, p3, steps=48):
    out = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        out.append((
            u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1],
        ))
    return out


def arc(cx, cy, rx, ry, a0, a1, steps=64):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / steps)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / steps))) for i in range(steps + 1)]


# ------------------------------------------------------------------ marks
# Each mark returns the shape to cut out, for a stroke width w (30 or 44).


def mark_studio(w):
    """Ausklang: a struck tone that rises and rings out (StudioCraft's existing mark)."""
    swings = 2.5 if w == LINE else 1.8
    amp = 150 if w == LINE else 140
    pts = []
    for i in range(241):
        t = i / 240
        env = min(1.0, t / 0.12) * math.exp(-1.9 * t)
        pts.append((118 + 282 * t, C0 - amp * env * math.sin(2 * math.pi * swings * t)))
    return stroke(pts, w)


def mark_git(w):
    """Abzweig: a line of history with a branch that leaves it; three commits as dots.

    A common motif for branches, drawn from scratch here (own geometry, no icon set traced).
    The whole mark is centred on the disc."""
    r = 34 if w == LINE else 46
    dx = 16  # centre the mark: lines span x 200..316 before the shift
    main = stroke([(200 + dx, 132), (200 + dx, 380)], w)
    branch = stroke(bezier((200 + dx, 352), (200 + dx, 270), (316 + dx, 286), (316 + dx, 196)), w)
    return unary_union([main, branch, dot(200 + dx, 132, r), dot(200 + dx, 380, r),
                        dot(316 + dx, 168, r)])


def mark_term(w):
    """Prompt: a chevron and a waiting cursor."""
    s = 0 if w == LINE else 8
    chev = stroke([(150 + s, 168), (246, 256), (150 + s, 344)], w)
    cursor = stroke([(290, 344), (372 - s, 344)], w)
    return unary_union([chev, cursor])


def mark_code(w):
    """Klammern: angle brackets around a slash."""
    if w == LINE:
        parts = [[(196, 172), (124, 256), (196, 340)], [(316, 172), (388, 256), (316, 340)],
                 [(282, 150), (230, 362)]]
    else:  # fewer, bolder parts: the slash stays, brackets move inward
        parts = [[(200, 176), (132, 256), (200, 336)], [(312, 176), (380, 256), (312, 336)],
                 [(276, 160), (236, 352)]]
    return unary_union([stroke(p, w) for p in parts])


def mark_data(w):
    """Speicher: a database cylinder."""
    rx, ry = (112, 40) if w == LINE else (108, 44)
    top, bot = 168, 344
    parts = [arc(256, top, rx, ry, 0, 360, 96),
             [(256 - rx, top), (256 - rx, bot)], [(256 + rx, top), (256 + rx, bot)],
             arc(256, bot, rx, ry, 0, 180)]
    if w == LINE:
        parts.append(arc(256, (top + bot) / 2, rx, ry, 0, 180))
    return unary_union([stroke(p, w) for p in parts])


def mark_cloud(w):
    """Baustein: an isometric block, the unit of infrastructure."""
    r = 136 if w == LINE else 128
    hexagon = [(256 + r * math.cos(math.radians(a)), 256 + r * math.sin(math.radians(a)))
               for a in (-90, -30, 30, 90, 150, 210, -90)]
    inner = [(256, 256), (256, 256 + r)], [(256, 256), hexagon[1]], [(256, 256), hexagon[5]]
    return unary_union([stroke(hexagon, w)] + [stroke(p, w) for p in inner])


def mark_issue(w):
    """Erledigt: a check mark."""
    return stroke([(150, 262), (226, 336), (366, 184)], w + (6 if w == LINE else 0))


APPS = [
    # key, name, mark, name of the mark
    ("studiocraft", "StudioCraft", mark_studio, "Decay"),
    ("codecraft", "CodeCraft", mark_code, "Brackets"),
    ("termcraft", "TermCraft", mark_term, "Prompt"),
    ("gitcraft", "GitCraft", mark_git, "Branch"),
    ("datacraft", "DataCraft", mark_data, "Store"),
    ("cloudcraft", "CloudCraft", mark_cloud, "Block"),
    ("issuecraft", "IssueCraft", mark_issue, "Done"),
]

# ------------------------------------------------------------------ colours

def load_tokens():
    data = json.loads((ROOT / "tokens" / "tokens.json").read_text())
    return {tok["name"]: tok["value"] for tok in data["color"]["tokens"]}


TOKENS = load_tokens()


def themed(name, theme):
    v = TOKENS[name]
    return v[theme] if isinstance(v, dict) else v


# Grounds every coloured text has to read on (brand: paper, surface, surface-sunken).
GROUNDS = {t: [themed(n, t) for n in ("paper", "surface", "surface-sunken")]
           for t in ("light", "dark")}

# Semantic hues for states every app shows; not in the brand tokens yet.
SEMANTIC_HUES = {"success": 150, "warning": 75, "danger": 27, "info": 245, "neutral": None}


def readable(h, theme, chroma=0.14, target=4.6):
    """A colour of hue h (None: grey) that reads as text on both panel colours of the theme.

    Dark theme: the darkest lightness that still passes (keeps the colour saturated instead of
    near white); light theme: the lightest that passes.
    """
    bgs = GROUNDS[theme]

    def colour(L):
        return oklch(L, chroma, h) if h is not None else oklch(L, 0, 0)

    passing = [i / 200 for i in range(201)
               if min(contrast(colour(i / 200), b) for b in bgs) >= target]
    if theme == "dark":
        passing = [L for L in passing if L > 0.5]
        return colour(min(passing))
    passing = [L for L in passing if L < 0.6]
    return colour(max(passing))


def semantic(theme):
    return {k: readable(h, theme) for k, h in SEMANTIC_HUES.items()}


def lch(hexcolour):
    return rgb_to_oklch(hex_to_rgb(hexcolour))


def app_colours(app):
    """Gradient and UI accents for an app colour (the `app-<name>` token)."""
    L, C, h = lch(app)
    light = {"accent": app, "on_accent": "#ffffff",
             "accent_strong": oklch(L - 0.08, C, h),
             "accent_tint": oklch(0.93, min(C, 0.04), h)}
    # Dark theme: lighter accent with near-black text, like petrol; at least 3:1 on the grounds.
    dark_accent = oklch(DARK_ACCENT_L, min(C, 0.15), h)
    dark = {"accent": dark_accent, "on_accent": themed("on-petrol", "dark"),
            "accent_strong": oklch(DARK_ACCENT_L + 0.08, min(C, 0.15), h),
            "accent_tint": oklch(0.30, min(C, 0.06), h)}
    for theme, ui in (("light", light), ("dark", dark)):
        ui["contrast_on_accent"] = round(contrast(ui["accent"], ui["on_accent"]), 2)
        ui["contrast_on_grounds"] = round(min(contrast(ui["accent"], g) for g in GROUNDS[theme]), 2)
    return {
        "app": app,
        "ramp_light": oklch(L + STEP_LIGHT, C * 0.95, h + 2),
        "ramp_dark": oklch(L + STEP_DARK, C * 0.95, h - 1),
        "ui": {"light": light, "dark": dark},
    }


# Domain palettes: semantic colours the app's own data needs, per theme. Hues are chosen per
# meaning; lightness is solved for readability like the semantic colours.
DOMAIN = {
    "gitcraft": {"added": 145, "modified": 80, "deleted": 25, "renamed": 245, "conflict": 45,
                 "untracked": None},
    "termcraft": {  # ANSI colours 1-6 (0/7 and brights are neutrals and lighter variants)
        "red": 25, "green": 145, "yellow": 95, "blue": 255, "magenta": 330, "cyan": 200},
    "codecraft": {"keyword": 300, "string": 140, "number": 60, "comment": None, "type": 200,
                  "function": 255, "constant": 25},
    "datacraft": {"null": None, "number": 60, "text": 140, "boolean": 300, "date": 200,
                  "key": 85, "transaction_open": 75, "autocommit": 145},
    "cloudcraft": {"production": 25, "staging": 75, "development": 145, "local": 245,
                   "running": 145, "stopped": None, "failed": 25, "pending": 75},
    "issuecraft": {"bug": 25, "feature": 255, "task": None, "improvement": 145, "epic": 300,
                   "urgent": 25, "high": 50, "medium": 80, "low": 245},
}


def domain(key, theme):
    return {k: readable(h, theme, chroma=0.13) for k, h in DOMAIN.get(key, {}).items()}


# ------------------------------------------------------------------ output


def svg(shape, colours, title):
    disc = Point(C0, C0).buffer(RADIUS, quad_segs=64)
    body = disc.difference(shape)
    d = ""
    for poly in [body] if body.geom_type == "Polygon" else list(body.geoms):
        for ring in [poly.exterior, *poly.interiors]:
            d += "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in list(ring.coords)[:-1]) + " Z"
    grad = (f'<linearGradient id="face" x1="0.2" y1="0" x2="0.8" y2="1">'
            f'<stop offset="0" stop-color="{colours["ramp_light"]}"/>'
            f'<stop offset="1" stop-color="{colours["ramp_dark"]}"/></linearGradient>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" width="{SIZE}" '
            f'height="{SIZE}" role="img"><title>{title}</title><defs>{grad}</defs>'
            f'<path fill-rule="evenodd" fill="url(#face)" d="{d}"/></svg>\n')


def main():
    out = ROOT / "apps"
    palette = {"note": "Generated by tools/make_app_icons.py from tokens/tokens.json.",
               "semantic": {t: semantic(t) for t in ("light", "dark")}, "apps": {}}
    for key, name, mark, mark_name in APPS:
        colours = app_colours(TOKENS[f"app-{key}"])
        if key == "studiocraft":  # the shipped icon stays exactly as it is
            colours.update(ramp_light="#d9587a", ramp_dark="#8e1f3c")
        d = out / key
        d.mkdir(parents=True, exist_ok=True)
        (d / "icon.svg").write_text(svg(mark(LINE), colours, name))
        (d / "icon-small.svg").write_text(svg(mark(LINE_SMALL), colours, name))
        palette["apps"][key] = {"name": name, "mark": mark_name, **colours,
                                "domain": {t: domain(key, t) for t in ("light", "dark")}}
    (out / "palette.json").write_text(json.dumps(palette, indent=2, ensure_ascii=False) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
