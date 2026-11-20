#!/usr/bin/env python3
"""Generate the ONEFOLD LABS mark, lockups and avatar as SVG.

The mark is the letter O folded once: a petrol ring whose lower-right cap is
turned over along a diagonal fold line. The flap is that cap mirrored across
the fold. All geometry lives on a 512 grid and is computed here, so every file
in logos/ can be rebuilt from this script.

The wordmark is Archivo (width 125 %) converted to outlines; the font is read
from --fonts (see tools/build.sh, which downloads it).
"""
import argparse
import math
import os

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

PETROL = "#0e5a64"
PETROL_LIGHT = "#2f8f99"
SAFFRON = "#f2b630"
INK = "#111719"
PAPER = "#f6f7f5"
WHITE = "#ffffff"

ARCHIVO = "Archivo[wdth,wght].ttf"

# Geometry on the 512 grid (centre 256, 256).
R_OUT = 226.0   # outer radius of the ring
R_IN = 113.0    # radius of the counter
D_FOLD = 151.0  # distance of the fold line from the centre, towards the lower right
FLAT_GAP = 9.0  # gap between ring and flap in the flat versions
FOLD_BOW = 16.0 # outward bow of the fold edge in the versions with depth


def fmt(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def arc_flags(c, p0, p1, through):
    """SVG large-arc and sweep flags for the arc of the circle around c from p0 to p1 that passes `through`."""
    a0 = math.atan2(p0[1] - c[1], p0[0] - c[0])
    a1 = math.atan2(p1[1] - c[1], p1[0] - c[0])
    at = math.atan2(through[1] - c[1], through[0] - c[0])
    turn = 2 * math.pi
    span = (a1 - a0) % turn
    if (at - a0) % turn < span:
        return (1 if span > math.pi else 0), 1
    span = (a0 - a1) % turn
    return (1 if span > math.pi else 0), 0


def short_arc_flags(c, p0, p1):
    """Flags for the shorter arc from p0 to p1."""
    vx = (p0[0] - c[0]) + (p1[0] - c[0])
    vy = (p0[1] - c[1]) + (p1[1] - c[1])
    n = math.hypot(vx, vy)
    r = math.hypot(p0[0] - c[0], p0[1] - c[1])
    return arc_flags(c, p0, p1, (c[0] + r * vx / n, c[1] + r * vy / n))


def circle_intersections(c1, r1, c2, r2):
    dx, dy = c2[0] - c1[0], c2[1] - c1[1]
    d = math.hypot(dx, dy)
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = math.sqrt(max(r1 * r1 - a * a, 0))
    mx, my = c1[0] + a * dx / d, c1[1] + a * dy / d
    return (mx - h * dy / d, my + h * dx / d), (mx + h * dy / d, my - h * dx / d)


def mark_geometry(gap):
    """Paths of the ring (front) and the flap, plus the two ends of the flap gradient."""
    c = (256.0, 256.0)
    s2 = math.sqrt(0.5)
    u = (s2, s2)    # towards the fold
    v = (-s2, s2)   # along the fold
    mirror = (c[0] + 2 * D_FOLD * u[0], c[1] + 2 * D_FOLD * u[1])  # centre mirrored across the fold
    h = math.sqrt(R_OUT ** 2 - D_FOLD ** 2)
    A = (c[0] + D_FOLD * u[0] + h * v[0], c[1] + D_FOLD * u[1] + h * v[1])
    B = (c[0] + D_FOLD * u[0] - h * v[0], c[1] + D_FOLD * u[1] - h * v[1])

    def side(p):
        return (p[0] - c[0]) * v[0] + (p[1] - c[1]) * v[1]

    # Front: ring minus the folded-over area (mirrored outer circle, grown by the gap).
    rg = R_OUT + gap
    E, F = circle_intersections(c, R_OUT, mirror, rg)
    if side(E) < side(F):
        E, F = F, E
    H1, H2 = circle_intersections(c, R_IN, mirror, rg)
    if side(H1) < side(H2):
        H1, H2 = H2, H1
    far = (c[0] - R_OUT * u[0], c[1] - R_OUT * u[1])
    far_in = (c[0] - R_IN * u[0], c[1] - R_IN * u[1])
    l1, s1 = arc_flags(c, E, F, far)
    l2, s2_ = short_arc_flags(mirror, F, H2)
    l3, s3 = arc_flags(c, H2, H1, far_in)
    l4, s4 = short_arc_flags(mirror, H1, E)
    front = (f"M{fmt(E[0])} {fmt(E[1])}A{fmt(R_OUT)} {fmt(R_OUT)} 0 {l1} {s1} {fmt(F[0])} {fmt(F[1])}"
             f"A{fmt(rg)} {fmt(rg)} 0 {l2} {s2_} {fmt(H2[0])} {fmt(H2[1])}"
             f"A{fmt(R_IN)} {fmt(R_IN)} 0 {l3} {s3} {fmt(H1[0])} {fmt(H1[1])}"
             f"A{fmt(rg)} {fmt(rg)} 0 {l4} {s4} {fmt(E[0])} {fmt(E[1])}Z")

    # Flap: the cap beyond the fold, mirrored onto the ring.
    tip = (mirror[0] - R_OUT * u[0], mirror[1] - R_OUT * u[1])
    l5, s5 = arc_flags(mirror, B, A, tip)
    bow = FOLD_BOW if gap == 0 else 0.0
    q = (c[0] + (D_FOLD + 2 * bow) * u[0], c[1] + (D_FOLD + 2 * bow) * u[1])
    edge = f"Q{fmt(q[0])} {fmt(q[1])} {fmt(B[0])} {fmt(B[1])}" if bow else f"L{fmt(B[0])} {fmt(B[1])}"
    flap = f"M{fmt(A[0])} {fmt(A[1])}{edge}A{fmt(R_OUT)} {fmt(R_OUT)} 0 {l5} {s5} {fmt(A[0])} {fmt(A[1])}Z"
    fold_mid = (c[0] + D_FOLD * u[0], c[1] + D_FOLD * u[1])
    return front, flap, tip, fold_mid


_ids = [0]


def mark(x, y, size, front_col, flap_col, depth=False, dark=False):
    """The mark at (x, y) with the given size; flat or with gradients and shadow."""
    k = size / 512
    if not depth:
        fr, fl, _, _ = mark_geometry(FLAT_GAP)
        return (f'<g transform="translate({fmt(x)} {fmt(y)}) scale({k:.5f})">'
                f'<path fill="{front_col}" d="{fr}"/><path fill="{flap_col}" d="{fl}"/></g>')
    _ids[0] += 1
    i = _ids[0]
    fr, fl, tip, fm = mark_geometry(0)
    f0, f1 = ("#3aa3ad", "#1f7880") if dark else ("#17717c", "#0a4a53")
    shadow = "0.6" if dark else "0.4"
    return (f'<defs>'
            f'<linearGradient id="of{i}" x1="60" y1="60" x2="452" y2="452" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{f0}"/><stop offset="1" stop-color="{f1}"/></linearGradient>'
            f'<linearGradient id="ob{i}" x1="{fmt(tip[0])}" y1="{fmt(tip[1])}" x2="{fmt(fm[0])}" y2="{fmt(fm[1])}" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="#fbd468"/><stop offset="0.55" stop-color="#f2b630"/><stop offset="1" stop-color="#d98e17"/></linearGradient>'
            f'<filter id="os{i}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="11"/></filter>'
            f'<clipPath id="oc{i}"><path d="{fl}"/></clipPath>'
            f'</defs>'
            f'<g transform="translate({fmt(x)} {fmt(y)}) scale({k:.5f})">'
            f'<path fill="url(#of{i})" d="{fr}"/>'
            f'<path fill="#06262b" opacity="{shadow}" filter="url(#os{i})" transform="translate(14 20)" d="{fl}"/>'
            f'<path fill="url(#ob{i})" d="{fl}"/>'
            f'<path fill="none" stroke="#fff3c9" stroke-opacity="0.55" stroke-width="3" clip-path="url(#oc{i})" d="{fl}"/>'
            f'</g>')


class Wordmark:
    def __init__(self, font_dir):
        self.font_dir = font_dir
        self.cache = {}

    def font(self, wght):
        if wght not in self.cache:
            ft = TTFont(os.path.join(self.font_dir, ARCHIVO))
            self.cache[wght] = instancer.instantiateVariableFont(ft, {"wght": wght, "wdth": 125})
        return self.cache[wght]

    def text(self, text, wght, size, x, y, tracking=0.0):
        """Outline path of `text` with its baseline at y; returns (path, advance width)."""
        ft = self.font(wght)
        gs = ft.getGlyphSet()
        cmap = ft.getBestCmap()
        upm = ft["head"].unitsPerEm
        hmtx = ft["hmtx"]
        sc = size / upm
        pen = SVGPathPen(gs)
        pos = 0.0
        for i, ch in enumerate(text):
            gn = cmap[ord(ch)]
            gs[gn].draw(TransformPen(pen, (sc, 0, 0, -sc, x + pos * sc, y)))
            pos += hmtx[gn][0] + (tracking * upm if i < len(text) - 1 else 0)
        return pen.getCommands(), pos * sc

    def cap_height(self, wght, size):
        ft = self.font(wght)
        return ft["OS/2"].sCapHeight * size / ft["head"].unitsPerEm


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {fmt(w)} {fmt(h)}" width="{fmt(w)}" height="{fmt(h)}" role="img">'
            f'<title>ONEFOLD LABS</title>{body}</svg>\n')


def lockup(wm, front, flap, ink, labs, depth=False, dark=False):
    """Mark, then ONEFOLD (extra bold) and LABS (light) on one line."""
    H = 160
    size = H * 0.42 / (wm.cap_height(760, 1000) / 1000)
    cap = wm.cap_height(760, size)
    tx = H + H * 0.30
    base = H / 2 + cap / 2
    p1, w1 = wm.text("ONEFOLD", 760, size, tx, base, 0.02)
    space = size * 0.32
    p2, w2 = wm.text("LABS", 340, size, tx + w1 + space, base, 0.02)
    W = tx + w1 + space + w2 + 4
    return svg(W, H, mark(0, 0, H, front, flap, depth, dark) + f'<path fill="{ink}" d="{p1}"/><path fill="{labs}" d="{p2}"/>')


def stacked(wm, front, flap, ink, labs, dark=False):
    """Mark above ONEFOLD, LABS tracked out and centred below."""
    size = 120
    cap = wm.cap_height(760, size)
    _, W = wm.text("ONEFOLD", 760, size, 0, 0, 0.02)
    M = W * 0.42
    ty = M + size * 0.55 + cap
    p1, _ = wm.text("ONEFOLD", 760, size, 0, ty, 0.02)
    lsize = size * 0.40
    _, wl = wm.text("LABS", 420, lsize, 0, 0, 0.42)
    ly = ty + size * 0.36 + wm.cap_height(420, lsize)
    p2, _ = wm.text("LABS", 420, lsize, (W - wl) / 2, ly, 0.42)
    return svg(W, ly + 6, mark((W - M) / 2, 0, M, front, flap, True, dark) + f'<path fill="{ink}" d="{p1}"/><path fill="{labs}" d="{p2}"/>')


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fonts", required=True, help="directory holding Archivo[wdth,wght].ttf")
    ap.add_argument("--out", required=True, help="output directory for the SVGs")
    args = ap.parse_args()
    wm = Wordmark(args.fonts)
    files = {
        "onefold-mark.svg": svg(512, 512, mark(0, 0, 512, PETROL, SAFFRON, depth=True)),
        "onefold-mark-on-dark.svg": svg(512, 512, mark(0, 0, 512, PETROL_LIGHT, SAFFRON, depth=True, dark=True)),
        "onefold-mark-flat.svg": svg(512, 512, mark(0, 0, 512, PETROL, SAFFRON)),
        "onefold-mark-ink.svg": svg(512, 512, mark(0, 0, 512, INK, INK)),
        "onefold-mark-white.svg": svg(512, 512, mark(0, 0, 512, WHITE, WHITE)),
        "onefold-lockup.svg": lockup(wm, PETROL, SAFFRON, INK, INK, True),
        "onefold-lockup-on-dark.svg": lockup(wm, PETROL_LIGHT, SAFFRON, WHITE, WHITE, True, True),
        "onefold-lockup-ink.svg": lockup(wm, INK, INK, INK, INK),
        "onefold-lockup-stacked.svg": stacked(wm, PETROL, SAFFRON, INK, PETROL),
        "onefold-lockup-stacked-on-dark.svg": stacked(wm, PETROL_LIGHT, SAFFRON, WHITE, SAFFRON, True),
        "onefold-avatar.svg": svg(512, 512, f'<rect width="512" height="512" fill="{PAPER}"/>' + mark(66, 60, 380, PETROL, SAFFRON, depth=True)),
    }
    os.makedirs(args.out, exist_ok=True)
    for name, content in files.items():
        with open(os.path.join(args.out, name), "w") as fh:
            fh.write(content)
    print(f"wrote {len(files)} files to {args.out}")


if __name__ == "__main__":
    main()
