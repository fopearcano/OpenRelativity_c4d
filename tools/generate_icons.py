#!/usr/bin/env python3
"""Generate the plugin's flat command icons - reproducibly, with NO dependencies.

Each icon is defined as a tiny list of flat geometric primitives (rect, disc,
ring, line, polygon) in a 32x32 coordinate space. From that single description we
emit:

  * an **SVG** vector source  -> openrelativity_c4d/resources/icons/src/<name>.svg
  * a **PNG** raster (32 + 64) -> openrelativity_c4d/resources/icons/png/<name>.png
                                  openrelativity_c4d/resources/icons/png/<name>_64.png

PNG is written by hand using only the standard library (``zlib`` + ``struct``):
no Pillow, no external icon library, nothing downloaded. Raster edges are
anti-aliased by rendering at an integer supersample and box-averaging down
(premultiplied alpha, so transparent backgrounds get no dark halo). Output is
deterministic, so re-running reproduces the same assets.

Usage:
    python tools/generate_icons.py            # write all SVG + PNG assets
    python tools/generate_icons.py --list     # just print the icon names

Colours and the section model follow docs/UI_DESIGN_SYSTEM.md. These are
intentionally simple prototype assets (see docs/ICONS.md); they are NOT wired
into command registration here (no behavior change).
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

# --- palette (RGBA), from docs/UI_DESIGN_SYSTEM.md --------------------------
BLUE = (62, 134, 224, 255)
BLUE_D = (44, 104, 184, 255)
VIOLET = (142, 111, 224, 255)
VIOLET_L = (176, 150, 238, 255)
VIOLET_D = (110, 84, 182, 255)
ORANGE = (240, 136, 60, 255)
ORANGE_D = (198, 104, 40, 255)
ORANGE_L = (248, 170, 108, 255)
GREEN = (63, 179, 107, 255)
GREEN_D = (44, 140, 84, 255)
GRAY = (154, 160, 166, 255)
RED = (229, 72, 77, 255)
CYAN = (70, 198, 222, 255)
WHITE = (238, 240, 242, 255)
BLUE_DOP = (74, 144, 226, 255)


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


# --- icon definitions: (name, section, [shapes]) ---------------------------
def _icons():
    return [
        ("icon_about", "Help", [
            D(16, 16, 12.5, CYAN),
            D(16, 10, 1.9, WHITE),
            R(14.4, 13.2, 3.2, 9.4, WHITE, r=1.4),
        ]),
        ("icon_control_panel", "Help", [
            R(6, 8.5, 20, 2.6, CYAN, r=1.3),
            R(6, 15.5, 20, 2.6, CYAN, r=1.3),
            R(6, 22.5, 20, 2.6, CYAN, r=1.3),
            D(12, 9.8, 2.7, WHITE),
            D(20, 16.8, 2.7, WHITE),
            D(9, 23.8, 2.7, WHITE),
        ]),
        ("icon_setup_controller", "Setup", [
            L(16, 3.5, 16, 28.5, 2.2, BLUE),
            L(3.5, 16, 28.5, 16, 2.2, BLUE),
            RING(16, 16, 10.5, 2.0, BLUE),
            D(16, 16, 4.2, BLUE),
            D(16, 16, 1.8, WHITE),
        ]),
        ("icon_setup_camera", "Setup", [
            R(7, 8, 5.5, 3.4, BLUE, r=1.0),
            R(5, 11, 18, 11, BLUE, r=2.0),
            D(14, 16.5, 4.6, WHITE),
            D(14, 16.5, 2.7, BLUE),
            D(20, 14, 1.2, WHITE),
        ]),
        ("icon_setup_objects", "Setup", [
            R(4.5, 5, 9, 9, BLUE, r=1.6),
            R(18.5, 5, 9, 9, BLUE_D, r=1.6),
            R(11.5, 17, 9, 9, BLUE, r=1.6),
        ]),
        ("icon_create_test_scene", "Setup", [
            L(4, 27, 28, 27, 1.6, BLUE),
            L(6, 22, 26, 22, 1.4, BLUE),
            L(9, 27, 10.5, 22, 1.3, BLUE),
            L(16, 27, 16, 22, 1.3, BLUE),
            L(23, 27, 21.5, 22, 1.3, BLUE),
            D(16, 14, 6.0, BLUE),
            D(13.8, 11.8, 1.8, WHITE),
        ]),
        ("icon_doppler_preview", "Preview", [
            RING(16, 16, 12.5, 2.0, VIOLET),
            L(15, 16, 9.5, 16, 2.6, BLUE_DOP),
            P([(9.5, 11.5), (4.7, 16), (9.5, 20.5)], BLUE_DOP),
            L(17, 16, 22.5, 16, 2.6, RED),
            P([(22.5, 11.5), (27.3, 16), (22.5, 20.5)], RED),
        ]),
        ("icon_searchlight_preview", "Preview", [
            P([(9, 16), (27, 6.5), (27, 25.5)], VIOLET),
            P([(9, 16), (25.5, 9.8), (25.5, 22.2)], VIOLET_L),
            D(8.5, 16, 2.7, WHITE),
        ]),
        ("icon_all_previews", "Preview", [
            R(9.5, 12.5, 15, 11, VIOLET_D, r=2.0),
            R(6.0, 8.5, 15, 11, VIOLET, r=2.0),
            P([(22, 18.2), (23.2, 20.8), (26, 22), (23.2, 23.2),
               (22, 26), (20.8, 23.2), (18, 22), (20.8, 20.8)], WHITE),
        ]),
        ("icon_lorentz_create", "Preview", [
            R(14, 7, 4, 18, VIOLET, r=1.0),
            L(3.5, 16, 8.5, 16, 2.2, VIOLET),
            P([(8, 12.5), (12, 16), (8, 19.5)], VIOLET),
            L(28.5, 16, 23.5, 16, 2.2, VIOLET),
            P([(24, 12.5), (20, 16), (24, 19.5)], VIOLET),
        ]),
        ("icon_lorentz_remove", "Preview", [
            R(14, 7, 4, 18, VIOLET, r=1.0),
            L(6.5, 6.5, 25.5, 25.5, 2.6, RED),
            L(25.5, 6.5, 6.5, 25.5, 2.6, RED),
        ]),
        ("icon_octane_status", "Octane", [
            RING(16, 16, 12.0, 3.0, ORANGE),
            D(16, 16, 3.4, ORANGE),
        ]),
        ("icon_aov_plan", "Octane", [
            R(6, 8, 15, 11, ORANGE_D, r=1.5),
            R(8.5, 11, 15, 11, ORANGE, r=1.5),
            R(11, 14, 15, 11, ORANGE_L, r=1.5),
        ]),
        ("icon_export_metadata", "Export", [
            R(7, 5, 13, 18, GREEN, r=1.2),
            R(9.5, 8.5, 8, 1.5, WHITE, r=0.7),
            R(9.5, 11.5, 8, 1.5, WHITE, r=0.7),
            R(9.5, 14.5, 5, 1.5, WHITE, r=0.7),
            R(15.0, 15.5, 2.2, 6.0, WHITE),
            P([(12.8, 21.0), (19.2, 21.0), (16.0, 25.5)], WHITE),
        ]),
        ("icon_export_osl", "Export", [
            R(24.3, 7, 2.2, 18, GREEN_D, r=1.0),
            L(7, 16, 24.3, 8, 1.8, GREEN),
            L(7, 16, 24.3, 16, 1.8, GREEN),
            L(7, 16, 24.3, 24, 1.8, GREEN),
            D(7, 16, 2.8, GREEN),
        ]),
        ("icon_diagnostics", "Diagnostics", [
            L(4, 16, 11, 16, 2.4, GRAY),
            L(11, 16, 14, 8, 2.4, GRAY),
            L(14, 8, 18, 24, 2.4, GRAY),
            L(18, 24, 21, 16, 2.4, GRAY),
            L(21, 16, 28, 16, 2.4, GRAY),
        ]),
    ]


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


def write_png(path, size, rgba):
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)  # 8-bit RGBA
    stride = size * 4
    raw = bytearray()
    for y in range(size):
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
        svg_path = os.path.join(SRC_DIR, name + ".svg")
        with open(svg_path, "w") as fh:
            fh.write(render_svg(shapes))
        for size in PNG_SIZES:
            suffix = "" if size == CANVAS else "_%d" % size
            png_path = os.path.join(PNG_DIR, "%s%s.png" % (name, suffix))
            write_png(png_path, size, render_png_bytes(shapes, size))
        png32 = os.path.join(PNG_DIR, name + ".png")
        print("  %-26s [%-11s] svg + png(%s)  %d B" % (
            name, section, "/".join(str(s) for s in PNG_SIZES),
            os.path.getsize(png32)))
    print("Done. SVG sources in src/, PNG rasters in png/.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
