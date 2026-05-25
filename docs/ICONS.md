# Icons

The plugin's command icons are **simple, flat, locally generated** prototype
assets - produced by a script in this repo using only the Python standard
library. **Nothing is downloaded**, there is **no external dependency**, and no
copyrighted icon pack is used. They follow [`UI_DESIGN_SYSTEM.md`](UI_DESIGN_SYSTEM.md).

They are a **coherent family**: every icon is a section-coloured **rounded-square
tile** with a flat **white glyph** on top (a translucent white is used for
secondary marks, and the tile colour is reused to "cut" holes in white shapes).
Consistent 32×32 canvas, tile inset/corner radius, padding, and stroke widths give
them one look; the section colour comes entirely from the tile - see the
[preview sheet](#preview-sheet).

## How to regenerate

```sh
python tools/generate_icons.py          # write all SVG sources + PNG rasters
python tools/generate_icons.py --list   # just list the icon names + sections
```

The generator (`tools/generate_icons.py`) defines each icon as a section tile
plus a few flat primitives (rect / disc / ring / line / polygon) in a 32×32 space,
then writes **an SVG vector source, PNG rasters, and a preview sheet** from that
single description. PNGs are encoded by hand with `zlib` + `struct` (8-bit RGBA),
anti-aliased by rendering at an integer supersample and box-averaging down with
premultiplied alpha (so the transparent corners around the tile get no dark halo).
Output is **deterministic** - re-running reproduces byte-identical assets.

## Where they live

```
openrelativity_c4d/resources/icons/
  README.md
  icon_sheet.png          # preview contact sheet (raster)
  icon_sheet.svg          # preview contact sheet (labelled vector)
  src/<name>.svg          # editable vector source (viewBox 0 0 32)
  png/<name>.png          # 32x32 RGBA - the primary, C4D-loadable icon
  png/<name>_64.png       # 64x64 RGBA - optional HiDPI raster
```

`<name>` is the `icon_*` name from the table below (e.g. `icon_setup_camera`).

## Preview sheet

`tools/generate_icons.py` also writes a contact sheet of the whole set so the
family can be eyeballed at a glance:

- **`resources/icons/icon_sheet.png`** - all icons (64 px each) on a dark grid,
  grouped by section so the colour coding is obvious.
- **`resources/icons/icon_sheet.svg`** - the same, labelled with each icon name
  (resolution-independent).

Regenerate both with `python tools/generate_icons.py`.

## Icon set

16 icons. The **tile** carries the section colour (see
[`UI_DESIGN_SYSTEM.md`](UI_DESIGN_SYSTEM.md) §3); the **glyph** is white. "Command(s)"
is the user command each is intended for (some commands reuse the nearest icon -
mirroring the registry in `c4d/ui_assets.py`).

| Icon | Tile (section colour) | White glyph | Command(s) served |
|---|---|---|---|
| `icon_setup_controller` | Setup / blue | crosshair + node + orbit ring | Create Controller |
| `icon_setup_camera` | Setup / blue | camera body + lens + viewfinder | Setup Camera |
| `icon_setup_objects` | Setup / blue | three squares | Setup Selected Objects · Select Objects *(reuse)* |
| `icon_create_test_scene` | Setup / blue | ground grid + sphere | Create Test Scene |
| `icon_doppler_preview` | Preview / violet | opposing shift arrows in a ring | Apply Doppler |
| `icon_searchlight_preview` | Preview / violet | beam cone from a source | Apply Searchlight |
| `icon_all_previews` | Preview / violet | stacked sheets + spark | Apply All Materials · Apply All *(reuse)* |
| `icon_lorentz_create` | Preview / violet | narrow bar + inward arrows | Create Lorentz Copies |
| `icon_lorentz_remove` | Preview / violet | trash / delete bin | Remove Lorentz Copies · Clear Generated Materials *(reuse)* |
| `icon_octane_status` | Octane / orange | ring + centre dot | Octane Status · Apply Compatible Preview *(reuse)* |
| `icon_aov_plan` | Octane / orange | layered pass sheets | Show AOV Plan |
| `icon_export_metadata` | Export / green | document + export arrow | Metadata JSON |
| `icon_export_osl` | Export / green | camera rays to an image plane | Export OSL Camera |
| `icon_diagnostics` | Diagnostics / gray | pulse / heartbeat line | Octane Diagnostics · UI Diagnostics *(reuse)* |
| `icon_about` | Help / cyan | info "i" mark | About |
| `icon_control_panel` | Help / cyan | three sliders | Control Panel |

## Style rules

- **One coherent family:** section-coloured rounded tile + flat white glyph, the
  same tile inset (1.5 px) and corner radius (~6.5 px) and consistent padding on
  every icon.
- Flat colour only - **no gradients**, shadows, or bevels.
- Glyph palette is just **white** (`INK`) + a **translucent white** (`INK_DIM`) for
  secondary marks; the tile colour is reused to punch holes (e.g. the camera lens,
  the document's text lines). No per-icon "special" colours, so the set stays
  uniform.
- Simple geometric shapes; **no text** inside icons (the About "i" mark is the one
  allowed glyph-letter).
- **32×32** is the primary size (the size C4D command icons display at); 64×64 is
  an optional HiDPI raster. SVG is resolution-independent.
- **PNG, 8-bit RGBA** (transparent outside the tile) - no SVG/TIFF/PSD or exotic
  formats for the C4D-loaded asset (avoids anything that may fail to load in
  Cinema 4D).

## How Cinema 4D loads them

Loading is centralized in [`openrelativity_c4d/c4d/icon_loader.py`](../openrelativity_c4d/c4d/icon_loader.py)
and is **safe by construction** - a missing or unreadable icon never affects
whether a command works:

- `get_plugin_root()` - the `openrelativity_c4d` package dir, derived from
  `__file__` (no hardcoded absolute path).
- `get_icon_path(name)` - resolves `resources/icons/png/<name>.png` (accepts the
  bare name, a `.png` suffix, or a name without the `icon_` prefix); returns
  `None` if the file is absent. Pure - imports no `c4d`.
- `load_icon_bitmap(name)` - lazily imports `c4d`, loads the PNG via
  `c4d.bitmaps.BaseBitmap().InitWith(path)`, and returns the bitmap or `None`
  (never raises; logs at debug level).
- `safe_icon(name)` - the cached, never-raising entry point used by registration;
  returns a `BaseBitmap` or `None`.

`plugin_register.py` passes `icon=icon_loader.safe_icon("icon_<name>")` for each
command, so **if an icon is missing the command simply registers without one**
(identical to the previous `icon=None` behavior - no behavior change). The
icon→command mapping is the "Command(s) served" column above.

At the end of registration the plugin logs a one-line **icon diagnostic** -
`Command icons: N loaded, M missing.` - and, if any are missing, a warning listing
them (and the loaded set at debug level), via `icon_loader.get_load_summary()` /
`format_load_summary()`. Cinema 4D's `BaseBitmap` reads standard PNG, so no
special bitmap format is required; the SVG sources are not loaded at runtime.

## Reproducibility

The generator uses no randomness and writes no timestamps, so regenerating yields
identical files (verified by hashing before/after a re-run). Byte output could
differ only if a very different `zlib` build changes compression - the **image
content** is unchanged regardless.

## Known limitations

- These are **prototype "programmer-art" icons**: clear and consistent, but not a
  professional set. They are **replaceable without any code change** - drop in new
  PNGs with the same names.
- **Destructive intent** (Remove / Clear) is shown by the **trash glyph** plus the
  command label and help text, not by a red icon - this keeps the family coherent
  (red stays a runtime *warning* colour, per `UI_DESIGN_SYSTEM.md`, rather than
  being baked into a tile).
- Anti-aliasing is supersample-and-average (no hinting), so very thin features are
  intentionally kept ≥ ~2 px at 32 px.
- SVG and PNG are generated from the same shapes but rendered by different
  rasterizers (a browser vs. this script), so sub-pixel edges may differ slightly;
  the PNGs are the assets Cinema 4D loads.
- The icon→command wiring (`icon_loader.safe_icon`) is exercised inside Cinema 4D
  only; the unit tests cover the pure path logic and the safe `None` fallback
  (Cinema 4D absent), not the actual `BaseBitmap` load.
