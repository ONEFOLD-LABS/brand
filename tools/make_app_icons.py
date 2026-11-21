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



APPS = [
    # key, name, mark, name of the mark
    ("studiocraft", "StudioCraft", mark_studio, "Decay"),
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


# Domain palettes: semantic colours an app's own data needs, per theme, as {name: hue or None}.
# Hues are chosen per meaning; lightness is solved for readability like the semantic colours.
# StudioCraft needs none yet.
DOMAIN: dict[str, dict[str, int | None]] = {}


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
