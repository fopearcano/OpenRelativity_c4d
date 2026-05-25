#!/usr/bin/env python3
"""Generate the plugin's flat command icons - reproducibly, with NO dependencies.

The icons are a **coherent family**: each is a section-coloured **rounded-square
tile** with a flat **white glyph** on top (a translucent white, ``INK_DIM``, is
used for secondary marks, and the tile colour is reused to "cut" holes in white
shapes). Consistent 32x32 canvas, consistent tile inset/corner radius, consistent
padding, and consistent stroke widths give them one look. Section colours follow
docs/UI_DESIGN_SYSTEM.md:

    Setup=blue  Preview=violet  Octane=orange  Export=green  Diagnostics=gray
    Help=cyan

From a single per-icon shape list we emit:

  * an **SVG** vector source  -> resources/icons/src/<name>.svg
  * a **PNG** raster (32 + 64) -> resources/icons/png/<name>.png (+ _64.png)
  * a **preview sheet**        -> resources/icons/icon_sheet.svg (labelled)
                                  resources/icons/icon_sheet.png

PNG is written by hand with only the standard library (``zlib`` + ``struct``):
no Pillow, no external icon library, nothing downloaded. Raster edges are
anti-aliased by rendering at an integer supersample and box-averaging down
(premultiplied alpha). Output is deterministic - re-running reproduces the assets.

Usage:
    python tools/generate_icons.py            # write all SVG + PNG assets + sheet
    python tools/generate_icons.py --list     # just print the icon names

These are intentionally simple prototype assets (see docs/ICONS.md). Generating
them changes no command behavior.
"""

import math
import os
import struct
import sys
import zlib

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_DIR = os.path.join(REPO_ROOT, "openrelativity_c4d", "resources", "icons")
SRC_DIR = os.path.join(ICON_DIR, "src")
PNG_DIR = os.path.join(ICON_DIR, "png")

CANVAS = 32  # design coordinate space (also the primary PNG size)
PNG_SIZES = (32, 64)
SUPERSAMPLE = {32: 4, 64: 3}  # hi-res factor per output size

# --- palette (RGBA) ---------------------------------------------------------
# One medium-saturated accent per section (the tile), plus a shared two-tone
# white "ink" for the glyph. Medium tiles keep the white glyph high-contrast.
BLUE = (54, 122, 204, 255)     # Setup
VIOLET = (130, 100, 208, 255)  # Preview
ORANGE = (224, 126, 50, 255)   # Octane
GREEN = (52, 162, 100, 255)    # Export
GRAY = (122, 130, 140, 255)    # Diagnostics
CYAN = (52, 170, 192, 255)     # Help
INK = (247, 248, 250, 255)      # primary glyph (near-white)
INK_DIM = (247, 248, 250, 130)  # secondary glyph (translucent white -> pastel)

SECTION_COLOR = {
    "Setup": BLUE, "Preview": VIOLET, "Octane": ORANGE,
    "Export": GREEN, "Diagnostics": GRAY, "Help": CYAN,
}

# Shared family geometry (in the 0..32 space).
_TILE_INSET = 1.5
_TILE_RADIUS = 6.5


# --- primitive constructors (coordinates in the 0..32 design space) ---------
def R(x, y, w, h, c, r=0.0):
    return {"t": "rect", "x": x, "y": y, "w": w, "h": h, "r": r, "c": c}


def D(cx, cy, rr, c):
    return {"t": "disc", "cx": cx, "cy": cy, "r": rr, "c": c}


def RING(cx, cy, rr, tk, c):
    return {"t": "ring", "cx": cx, "cy": cy, "r": rr, "tk": tk, "c": c}


def L(x1, y1, x2, y2, tk, c):
    return {"t": "line", "x1": x1, "y1": y1, "x2": x2, "y2": y2, "tk": tk, "c": c}


def P(pts, c):
    return {"t": "poly", "pts": pts, "c": c}


def _tile(accent):
    """The shared rounded-square background tile in the section ``accent``."""
    size = CANVAS - 2 * _TILE_INSET
    return R(_TILE_INSET, _TILE_INSET, size, size, accent, r=_TILE_RADIUS)


def _spark(cx, cy, outer, inner, c):
    """A 4-point star (8 vertices) centred at ``(cx, cy)``."""
    d = inner * 0.70
    return P([
        (cx, cy - outer), (cx + d, cy - d), (cx + outer, cy), (cx + d, cy + d),
        (cx, cy + outer), (cx - d, cy + d), (cx - outer, cy), (cx - d, cy - d),
    ], c)


# --- icon glyphs: (name, section, [glyph shapes]) ---------------------------
# Each glyph is drawn in white INK (+ INK_DIM for secondary marks; the section
# accent is reused to punch "holes" into white shapes). The tile is prepended
# automatically in :func:`_icons`. Grouped by section so the family reads clearly.
def _glyphs():
    return [
        # --- Setup (blue) ---------------------------------------------------
        ("icon_setup_controller", "Setup", [
            RING(16, 16, 10.5, 1.8, INK_DIM),
            L(16, 5, 16, 27, 2.2, INK), L(5, 16, 27, 16, 2.2, INK),
            D(16, 16, 3.6, INK), D(16, 16, 1.5, BLUE),
        ]),
        ("icon_setup_camera", "Setup", [
            R(7.5, 8, 5.5, 3.3, INK, r=1.0),
            R(5.5, 11, 21, 11.5, INK, r=2.2),
            D(14.5, 16.7, 4.3, BLUE), D(14.5, 16.7, 1.7, INK),
        ]),
        ("icon_setup_objects", "Setup", [
            R(5, 5, 9, 9, INK, r=1.6),
            R(18, 5, 9, 9, INK_DIM, r=1.6),
            R(11.5, 17, 9, 9, INK, r=1.6),
        ]),
        ("icon_create_test_scene", "Setup", [
            L(5, 26, 27, 26, 1.5, INK_DIM), L(7, 22, 25, 22, 1.3, INK_DIM),
            L(10, 26, 11.5, 22, 1.2, INK_DIM), L(16, 26, 16, 22, 1.2, INK_DIM),
            L(22, 26, 20.5, 22, 1.2, INK_DIM),
            D(16, 13.5, 5.8, INK),
        ]),
        # --- Preview (violet) ----------------------------------------------
        ("icon_doppler_preview", "Preview", [
            RING(16, 16, 12.0, 1.6, INK_DIM),
            L(15, 16, 9.5, 16, 2.4, INK), P([(9.5, 12), (5.3, 16), (9.5, 20)], INK),
            L(17, 16, 22.5, 16, 2.4, INK), P([(22.5, 12), (26.7, 16), (22.5, 20)], INK),
        ]),
        ("icon_searchlight_preview", "Preview", [
            P([(9, 16), (26, 7), (26, 25)], INK),
            L(11, 16, 25, 10, 1.2, VIOLET), L(11, 16, 25, 22, 1.2, VIOLET),
            D(8.5, 16, 2.6, INK),
        ]),
        ("icon_all_previews", "Preview", [
            R(9.5, 12.5, 15, 11, INK_DIM, r=2.0),
            R(6.0, 8.5, 15, 11, INK, r=2.0),
            _spark(22.6, 21.0, 3.4, 1.5, INK),
        ]),
        ("icon_lorentz_create", "Preview", [
            R(13.5, 7, 5, 18, INK, r=1.2),
            L(4, 16, 8.5, 16, 2.0, INK), P([(8, 12.5), (12, 16), (8, 19.5)], INK),
            L(28, 16, 23.5, 16, 2.0, INK), P([(24, 12.5), (20, 16), (24, 19.5)], INK),
        ]),
        ("icon_lorentz_remove", "Preview", [
            R(9.5, 9.3, 13, 2.4, INK, r=1.0),
            R(13.5, 7, 5, 2.2, INK, r=1.0),
            P([(11, 12), (21, 12), (19.8, 25), (12.2, 25)], INK),
            L(14, 15, 14, 22, 1.3, VIOLET), L(16, 15, 16, 22, 1.3, VIOLET),
            L(18, 15, 18, 22, 1.3, VIOLET),
        ]),
        # --- Octane (orange) -----------------------------------------------
        ("icon_octane_status", "Octane", [
            RING(16, 16, 11.0, 2.6, INK),
            D(16, 16, 3.2, INK),
        ]),
        ("icon_aov_plan", "Octane", [
            R(7.0, 8.5, 14.5, 10, INK_DIM, r=1.5),
            R(10.5, 12.5, 14.5, 10, INK, r=1.5),
        ]),
        # --- Export (green) ------------------------------------------------
        ("icon_export_metadata", "Export", [
            R(8, 4, 12, 15, INK, r=1.3),
            R(10, 7, 8, 1.4, GREEN, r=0.7), R(10, 10, 8, 1.4, GREEN, r=0.7),
            R(10, 13, 5, 1.4, GREEN, r=0.7),
            R(14.7, 17, 2.6, 4.6, INK), P([(12.6, 21), (19.4, 21), (16, 26)], INK),
        ]),
        ("icon_export_osl", "Export", [
            R(24.5, 7.5, 2.0, 17, INK_DIM, r=1.0),
            L(7.5, 16, 24, 8.5, 1.8, INK), L(7.5, 16, 24, 16, 1.8, INK),
            L(7.5, 16, 24, 23.5, 1.8, INK),
            D(7.5, 16, 2.8, INK),
        ]),
        # --- Diagnostics (gray) --------------------------------------------
        ("icon_diagnostics", "Diagnostics", [
            L(5, 16, 11, 16, 2.4, INK), L(11, 16, 14, 8.5, 2.4, INK),
            L(14, 8.5, 18, 23.5, 2.4, INK), L(18, 23.5, 21, 16, 2.4, INK),
            L(21, 16, 27, 16, 2.4, INK),
        ]),
        # --- Help (cyan) ----------------------------------------------------
        ("icon_about", "Help", [
            D(16, 10.5, 2.1, INK),
            R(14.5, 14, 3.0, 8.5, INK, r=1.3),
        ]),
        ("icon_control_panel", "Help", [
            R(6.5, 9.5, 19, 2.2, INK_DIM, r=1.1), R(6.5, 15, 19, 2.2, INK_DIM, r=1.1),
            R(6.5, 20.5, 19, 2.2, INK_DIM, r=1.1),
            D(11, 10.6, 2.8, INK), D(21, 16.1, 2.8, INK), D(9, 21.6, 2.8, INK),
        ]),
    ]


def _icons():
    """Return ``[(name, section, shapes)]`` with the section tile prepended."""
    out = []
    for name, section, glyph in _glyphs():
        accent = SECTION_COLOR[section]
        out.append((name, section, [_tile(accent)] + glyph))
    return out


# --- rasterizer (supersampled, premultiplied downsample) --------------------
class _Canvas:
    def __init__(self, size):
        self.size = size
        self.buf = bytearray(size * size * 4)  # RGBA, starts fully transparent

    def blend(self, x, y, c):
        if x < 0 or y < 0 or x >= self.size or y >= self.size:
            return
        sa = c[3] / 255.0
        if sa <= 0:
            return
        i = (y * self.size + x) * 4
        dr, dg, db, da = self.buf[i], self.buf[i + 1], self.buf[i + 2], self.buf[i + 3]
        da = da / 255.0
        oa = sa + da * (1.0 - sa)
        if oa <= 0:
            self.buf[i:i + 4] = b"\x00\x00\x00\x00"
            return
        self.buf[i] = int((c[0] * sa + dr * da * (1.0 - sa)) / oa + 0.5)
        self.buf[i + 1] = int((c[1] * sa + dg * da * (1.0 - sa)) / oa + 0.5)
        self.buf[i + 2] = int((c[2] * sa + db * da * (1.0 - sa)) / oa + 0.5)
        self.buf[i + 3] = int(oa * 255.0 + 0.5)


def _rrect_sdf(px, py, cx, cy, hw, hh, r):
    qx = abs(px - cx) - (hw - r)
    qy = abs(py - cy) - (hh - r)
    return math.hypot(max(qx, 0.0), max(qy, 0.0)) + min(max(qx, qy), 0.0) - r


def _seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    l2 = dx * dx + dy * dy
    if l2 <= 1e-9:
        return math.hypot(px - x1, py - y1)
    t = ((px - x1) * dx + (py - y1) * dy) / l2
    t = 0.0 if t < 0 else (1.0 if t > 1 else t)
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def _point_in_poly(px, py, pts):
    inside = False
    n = len(pts)
    j = n - 1
    for i in range(n):
        xi, yi = pts[i]
        xj, yj = pts[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def _bbox_iter(canvas, x0, y0, x1, y1):
    for py in range(max(0, int(math.floor(y0))), min(canvas.size, int(math.ceil(y1)) + 1)):
        for px in range(max(0, int(math.floor(x0))), min(canvas.size, int(math.ceil(x1)) + 1)):
            yield px, py


def _draw(canvas, s, k):
    c = s["c"]
    if s["t"] == "rect":
        cx = (s["x"] + s["w"] / 2.0) * k
        cy = (s["y"] + s["h"] / 2.0) * k
        hw, hh, r = s["w"] / 2.0 * k, s["h"] / 2.0 * k, s["r"] * k
        for px, py in _bbox_iter(canvas, cx - hw - 1, cy - hh - 1, cx + hw + 1, cy + hh + 1):
            if _rrect_sdf(px + 0.5, py + 0.5, cx, cy, hw, hh, r) <= 0:
                canvas.blend(px, py, c)
    elif s["t"] == "disc":
        cx, cy, r = s["cx"] * k, s["cy"] * k, s["r"] * k
        for px, py in _bbox_iter(canvas, cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1):
            if math.hypot(px + 0.5 - cx, py + 0.5 - cy) <= r:
                canvas.blend(px, py, c)
    elif s["t"] == "ring":
        cx, cy, r, tk = s["cx"] * k, s["cy"] * k, s["r"] * k, s["tk"] * k
        for px, py in _bbox_iter(canvas, cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1):
            d = math.hypot(px + 0.5 - cx, py + 0.5 - cy)
            if (r - tk) <= d <= r:
                canvas.blend(px, py, c)
    elif s["t"] == "line":
        x1, y1, x2, y2, tk = s["x1"] * k, s["y1"] * k, s["x2"] * k, s["y2"] * k, s["tk"] * k
        rr = tk / 2.0
        for px, py in _bbox_iter(canvas, min(x1, x2) - rr - 1, min(y1, y2) - rr - 1,
                                 max(x1, x2) + rr + 1, max(y1, y2) + rr + 1):
            if _seg_dist(px + 0.5, py + 0.5, x1, y1, x2, y2) <= rr:
                canvas.blend(px, py, c)
    elif s["t"] == "poly":
        pts = [(x * k, y * k) for x, y in s["pts"]]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        for px, py in _bbox_iter(canvas, min(xs) - 1, min(ys) - 1, max(xs) + 1, max(ys) + 1):
            if _point_in_poly(px + 0.5, py + 0.5, pts):
                canvas.blend(px, py, c)


def _downsample(canvas, ss, out_size):
    out = bytearray(out_size * out_size * 4)
    hi = canvas.size
    buf = canvas.buf
    n = float(ss * ss)
    for oy in range(out_size):
        for ox in range(out_size):
            sr = sg = sb = sa = 0.0
            for j in range(ss):
                row = ((oy * ss + j) * hi + ox * ss) * 4
                for i in range(ss):
                    idx = row + i * 4
                    a = buf[idx + 3] / 255.0
                    sr += buf[idx] * a
                    sg += buf[idx + 1] * a
                    sb += buf[idx + 2] * a
                    sa += a
            o = (oy * out_size + ox) * 4
            if sa <= 0:
                continue  # stays transparent
            out[o] = int(sr / sa + 0.5)
            out[o + 1] = int(sg / sa + 0.5)
            out[o + 2] = int(sb / sa + 0.5)
            out[o + 3] = int(sa / n * 255.0 + 0.5)
    return bytes(out)


def render_png_bytes(shapes, out_size):
    ss = SUPERSAMPLE[out_size]
    canvas = _Canvas(out_size * ss)
    k = (out_size * ss) / float(CANVAS)
    for s in shapes:
        _draw(canvas, s, k)
    return _downsample(canvas, ss, out_size)


# --- PNG writer (stdlib only) -----------------------------------------------
def _png_chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))


def write_png(path, width, height, rgba):
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)  # 8-bit RGBA
    stride = width * 4
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # filter type 0 (None)
        raw += rgba[y * stride:(y + 1) * stride]
    idat = zlib.compress(bytes(raw), 9)
    with open(path, "wb") as fh:
        fh.write(sig)
        fh.write(_png_chunk(b"IHDR", ihdr))
        fh.write(_png_chunk(b"IDAT", idat))
        fh.write(_png_chunk(b"IEND", b""))


# --- SVG writer -------------------------------------------------------------
def _hex(c):
    return "#%02X%02X%02X" % (c[0], c[1], c[2])


def _opacity(c):
    return "" if c[3] >= 255 else ' opacity="%.3f"' % (c[3] / 255.0)


def _svg_shape(s):
    c = s["c"]
    fill = ' fill="%s"%s' % (_hex(c), _opacity(c))
    if s["t"] == "rect":
        rx = ' rx="%g"' % s["r"] if s["r"] else ""
        return '<rect x="%g" y="%g" width="%g" height="%g"%s%s/>' % (
            s["x"], s["y"], s["w"], s["h"], rx, fill)
    if s["t"] == "disc":
        return '<circle cx="%g" cy="%g" r="%g"%s/>' % (s["cx"], s["cy"], s["r"], fill)
    if s["t"] == "ring":
        return ('<circle cx="%g" cy="%g" r="%g" fill="none" stroke="%s"%s '
                'stroke-width="%g"/>') % (s["cx"], s["cy"], s["r"] - s["tk"] / 2.0,
                                          _hex(c), _opacity(c), s["tk"])
    if s["t"] == "line":
        return ('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s"%s '
                'stroke-width="%g" stroke-linecap="round"/>') % (
                    s["x1"], s["y1"], s["x2"], s["y2"], _hex(c), _opacity(c), s["tk"])
    if s["t"] == "poly":
        pts = " ".join("%g,%g" % (x, y) for x, y in s["pts"])
        return '<polygon points="%s"%s/>' % (pts, fill)
    return ""


def render_svg(shapes):
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" '
        'viewBox="0 0 32 32">',
        "<!-- generated by tools/generate_icons.py - flat prototype icon -->",
    ]
    lines += [_svg_shape(s) for s in shapes]
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


# --- preview sheet ----------------------------------------------------------
_SHEET_COLS = 4
_SHEET_BG = (38, 38, 42, 255)


def render_sheet_svg(icons):
    """A labelled vector contact sheet of every icon."""
    cellw, cellh, pad, icon = 100, 86, 14, 56
    scale = icon / float(CANVAS)
    rows = (len(icons) + _SHEET_COLS - 1) // _SHEET_COLS
    width = pad * 2 + _SHEET_COLS * cellw
    height = pad * 2 + rows * cellh
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
        'viewBox="0 0 %d %d">' % (width, height, width, height),
        '<rect x="0" y="0" width="%d" height="%d" fill="%s"/>' % (
            width, height, _hex(_SHEET_BG)),
        "<!-- generated by tools/generate_icons.py - icon preview sheet -->",
    ]
    for idx, (name, _section, shapes) in enumerate(icons):
        col, row = idx % _SHEET_COLS, idx // _SHEET_COLS
        ix = pad + col * cellw + (cellw - icon) / 2.0
        iy = pad + row * cellh + 6
        parts.append('<g transform="translate(%g,%g) scale(%g)">' % (ix, iy, scale))
        parts += [_svg_shape(s) for s in shapes]
        parts.append('</g>')
        parts.append(
            '<text x="%g" y="%g" text-anchor="middle" font-family="monospace" '
            'font-size="9" fill="#C8C8CC">%s</text>' % (
                pad + col * cellw + cellw / 2.0, iy + icon + 14,
                name.replace("icon_", "")))
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def render_sheet_png(icons):
    """Composite every icon (64px) onto a dark grid. Returns ``(w, h, rgba)``."""
    cell, pad, icon = 80, 12, 64
    rows = (len(icons) + _SHEET_COLS - 1) // _SHEET_COLS
    width = pad * 2 + _SHEET_COLS * cell
    height = pad * 2 + rows * cell
    buf = bytearray(width * height * 4)
    for i in range(0, len(buf), 4):
        buf[i:i + 4] = bytes(_SHEET_BG)
    for idx, (_name, _section, shapes) in enumerate(icons):
        col, row = idx % _SHEET_COLS, idx // _SHEET_COLS
        rgba = render_png_bytes(shapes, icon)
        ox = pad + col * cell + (cell - icon) // 2
        oy = pad + row * cell + (cell - icon) // 2
        for y in range(icon):
            for x in range(icon):
                si = (y * icon + x) * 4
                sa = rgba[si + 3] / 255.0
                if sa <= 0:
                    continue
                di = ((oy + y) * width + (ox + x)) * 4
                for ch in range(3):
                    buf[di + ch] = int(rgba[si + ch] * sa + buf[di + ch] * (1.0 - sa) + 0.5)
                buf[di + 3] = 255
    return width, height, bytes(buf)


def main(argv):
    icons = _icons()
    if "--list" in argv:
        for name, section, _ in icons:
            print("%-26s %s" % (name, section))
        return 0

    os.makedirs(SRC_DIR, exist_ok=True)
    os.makedirs(PNG_DIR, exist_ok=True)

    print("Generating %d icons -> %s" % (len(icons), os.path.relpath(ICON_DIR, REPO_ROOT)))
    for name, section, shapes in icons:
        with open(os.path.join(SRC_DIR, name + ".svg"), "w") as fh:
            fh.write(render_svg(shapes))
        for size in PNG_SIZES:
            suffix = "" if size == CANVAS else "_%d" % size
            png_path = os.path.join(PNG_DIR, "%s%s.png" % (name, suffix))
            write_png(png_path, size, size, render_png_bytes(shapes, size))
        png32 = os.path.join(PNG_DIR, name + ".png")
        print("  %-26s [%-11s] svg + png(%s)  %d B" % (
            name, section, "/".join(str(s) for s in PNG_SIZES),
            os.path.getsize(png32)))

    with open(os.path.join(ICON_DIR, "icon_sheet.svg"), "w") as fh:
        fh.write(render_sheet_svg(icons))
    sheet_w, sheet_h, sheet_rgba = render_sheet_png(icons)
    write_png(os.path.join(ICON_DIR, "icon_sheet.png"), sheet_w, sheet_h, sheet_rgba)
    print("Wrote preview sheet: icon_sheet.svg + icon_sheet.png (%dx%d)." % (
        sheet_w, sheet_h))
    print("Done. SVG sources in src/, PNG rasters in png/, sheet in icons/.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
