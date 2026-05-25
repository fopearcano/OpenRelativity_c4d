# OpenRelativity C4D - icon assets

This folder holds the plugin's command/section icons.

## What these are

- **Simple, locally generated prototype assets.** The icons are intentionally
  minimal flat shapes, produced by a local script in this repo using only the
  Python standard library - **never downloaded** and with **no external icon
  library or dependency**.
- **Replaceable.** They are placeholders to make the UI feel intentional now.
  Professionally designed icons can replace them later **without any code change**
  - just drop in PNGs with the **same file names**.
- **Lightweight, by rule.** Flat **32×32 RGBA PNG** (optional **64×64** source),
  no gradients, no shadows, no text, no SVG/TIFF/PSD or other formats that may not
  load reliably in Cinema 4D. Each icon is only a few KB.

## Naming & format

```
<name>.png        # 32x32 RGBA, the delivered icon
<name>_64.png     # optional 64x64 RGBA source (HiDPI / re-export)
```

`<name>` is the lowercase `snake_case` icon name from the design system (e.g.
`setup_camera.png`, `doppler_preview.png`). ASCII only, no spaces.

The full icon list, per-icon glyph descriptions, section/colour mapping, and the
generation approach are defined in
[`docs/UI_DESIGN_SYSTEM.md`](../../../docs/UI_DESIGN_SYSTEM.md).

## Usage

Icons are **optional and additive**: a future safe loader returns a
`c4d.bitmaps.BaseBitmap` for `<name>.png` or `None` if the file is missing, so the
plugin keeps working (text-only commands) when an icon is absent. Adding or
replacing icons never changes command behavior.
