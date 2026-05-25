# Icons

The plugin's command icons are **simple, flat, locally generated** prototype
assets - produced by a script in this repo using only the Python standard
library. **Nothing is downloaded**, there is **no external dependency**, and no
copyrighted icon pack is used. They follow [`UI_DESIGN_SYSTEM.md`](UI_DESIGN_SYSTEM.md).

## How to regenerate

```sh
python tools/generate_icons.py          # write all SVG sources + PNG rasters
python tools/generate_icons.py --list   # just list the icon names + sections
```

The generator (`tools/generate_icons.py`) defines each icon as a few flat
primitives (rect / disc / ring / line / polygon) in a 32×32 space, then writes
**both** an SVG vector source and PNG rasters from that single description. PNGs
are encoded by hand with `zlib` + `struct` (8-bit RGBA), anti-aliased by rendering
at an integer supersample and box-averaging down with premultiplied alpha (so the
transparent background gets no dark halo). Output is **deterministic** - re-running
reproduces byte-identical assets.

## Where they live

```
openrelativity_c4d/resources/icons/
  README.md
  src/<name>.svg          # editable vector source (viewBox 0 0 32)
  png/<name>.png          # 32x32 RGBA - the primary, C4D-loadable icon
  png/<name>_64.png       # 64x64 RGBA - optional HiDPI raster
```

`<name>` is the `icon_*` name from the table below (e.g. `icon_setup_camera`).

## Icon set

16 icons, each in its section colour (see [`UI_DESIGN_SYSTEM.md`](UI_DESIGN_SYSTEM.md) §3)
with a simple-shape glyph. "Command(s)" is the user command each is intended for
(some commands reuse the nearest icon until a dedicated one exists - mirroring the
audit's mapping).

| Icon | Section / colour | Glyph | Command(s) served |
|---|---|---|---|
| `icon_about` | Help / cyan | info "i" in a disc | About |
| `icon_control_panel` | Help / cyan | three sliders | Control Panel |
| `icon_setup_controller` | Setup / blue | crosshair + centre node + orbit ring | Create Relativity Controller |
| `icon_setup_camera` | Setup / blue | camera body + lens + viewfinder | Setup Relativistic Camera |
| `icon_setup_objects` | Setup / blue | three cubes | Setup Selected Relativistic Objects · Select Relativistic Objects *(reuse)* |
| `icon_create_test_scene` | Setup / blue | ground grid + sphere | Create Test Scene |
| `icon_doppler_preview` | Preview / violet (+blue/red) | violet ring with opposing blue-shift/red-shift arrows | Apply Doppler Material Preview |
| `icon_searchlight_preview` | Preview / violet | beam cone from a source | Apply Searchlight Preview |
| `icon_all_previews` | Preview / violet | stacked tiles + spark | Apply All Previews · Apply Relativity Material Preview *(reuse)* |
| `icon_lorentz_create` | Preview / violet | narrow bar with inward arrows | Create Lorentz Preview Copies |
| `icon_lorentz_remove` | Preview / violet + red | narrow bar with a red X | Remove Lorentz Preview Copies · Clear Material Preview *(reuse, red accent)* |
| `icon_octane_status` | Octane / orange | orange ring + centre dot | Octane Status · Apply Octane-Compatible Material Preview *(reuse)* |
| `icon_aov_plan` | Octane / orange | layered pass sheets | Show AOV Plan |
| `icon_export_metadata` | Export / green | document + down/export arrow | Export Relativity Metadata JSON |
| `icon_export_osl` | Export / green | camera rays to an image plane | Export Experimental OSL Camera |
| `icon_diagnostics` | Diagnostics / gray | pulse / heartbeat line | Octane Diagnostics |

## Style rules

- Flat colour only - **no gradients**, shadows, or bevels.
- Simple geometric shapes; **no text** inside icons (the About "i" mark is the one
  allowed glyph-letter).
- **32×32** is the primary size (the size C4D command icons display at); 64×64 is
  an optional HiDPI raster. SVG is resolution-independent.
- **PNG, 8-bit RGBA**, transparent background - no SVG/TIFF/PSD or exotic formats
  for the C4D-loaded asset (avoids anything that may fail to load in Cinema 4D).
- One or two colours per icon (the section accent + white), plus red/blue only on
  the physics-/destructive-meaning icons (Doppler, Lorentz remove).

## How Cinema 4D will use them (not wired yet)

There is **no behavior change in this commit**: all 20 commands still register
with `icon=None`. Wiring is a separate, later step (per the audit's plan):

- A small safe loader will resolve `png/<name>.png` relative to the plugin folder
  and return a `c4d.bitmaps.BaseBitmap`, or **`None`** on any failure, so a
  missing/unreadable icon silently falls back to today's text-only command.
- The bitmap is then passed as the `icon=` argument of `RegisterCommandPlugin(...)`.

Cinema 4D's `BaseBitmap` reads standard PNG, so no special bitmap format is
required; there is no existing icon-loading code to conform to (verified: the
codebase currently passes `icon=None` everywhere).

## Reproducibility

The generator uses no randomness and writes no timestamps, so regenerating yields
identical files (verified by hashing before/after a re-run). Byte output could
differ only if a very different `zlib` build changes compression - the **image
content** is unchanged regardless.

## Known limitations

- These are **prototype "programmer-art" icons**: clear and consistent, but not a
  professional set. They are **replaceable without any code change** - drop in new
  PNGs with the same names.
- Anti-aliasing is supersample-and-average (no hinting), so very thin features are
  intentionally kept ≥ ~2 px at 32 px.
- SVG and PNG are generated from the same shapes but rendered by different
  rasterizers (a browser vs. this script), so sub-pixel edges may differ slightly;
  the PNGs are the assets Cinema 4D loads.
- Icons are **not yet referenced** by command registration (see above); doing so
  is tracked as a follow-up.
