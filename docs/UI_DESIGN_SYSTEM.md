# UI Design System

> **Design system - no behavior change.** This defines the visual and structural
> language for the plugin's UI (menu, Control Panel, dialogs, icons). It changes
> **no** command behavior, depends on **no** external icon library, and adds no
> feature logic. Icons are **flat, simple, locally generated** prototype assets
> (see [§4](#4-icon-style) and [§8](#8-generation--replacement)).
>
> Builds on [`UI_UX_AUDIT.md`](UI_UX_AUDIT.md). **Canonical icon location:**
> `openrelativity_c4d/resources/icons/` (this supersedes the tentative
> `res/icons/` mentioned in the audit).

## 1. General UI principles

1. **Compact layout.** Favour density over whitespace. Two-column button grids,
   short labels, tight group borders. Target laptop screens first.
2. **No huge vertical panels.** Never a single tall scroll of every control. When
   content exceeds ~8-10 rows, split into **tabs** (one per section, §2) so the
   window stays short. The Control Panel should open without forcing a resize.
3. **Grouped controls.** Every control lives in a labelled section group; nothing
   floats ungrouped. Groups map 1:1 to the section model (§2) and share the
   section's accent colour (§3).
4. **Clear workflow order.** Sections and the controls within them are ordered to
   match the real task flow: **Setup → Preview → Octane → Export**, with
   **Diagnostics** and **Help** last. Within Preview: apply actions before
   *Clear*; within Lorentz: *Create* before *Remove*.
5. **Safe status feedback.** A persistent, read-only status read-out (controller /
   camera / objects / Octane / preview state) is always visible in the Control
   Panel; result dialogs state exactly what happened and how many items were
   affected. Read-only commands (*About*, *Octane Status*, *Octane Diagnostics*,
   *Show AOV Plan*) are visually marked as non-mutating and never block.
6. **No destructive action without clear labelling.** Removal/clear actions
   (*Clear Material Preview*, *Remove Lorentz Preview Copies*) use an explicit
   "Clear"/"Remove" verb, a **red/error accent** (§3) on their icon/label, and a
   result dialog that confirms what was removed **and that original user data is
   untouched**. No silent or one-click-irreversible deletes; these commands only
   ever remove ORC-generated `ORC_*` content, never user geometry/materials.

> Cross-cutting: the menu, the Control Panel tabs, and (future) icons are all
> **driven from one command registry** so they cannot drift (see the audit's
> implementation plan). Icons are always **additive** - the UI is fully usable
> with them absent.

## 2. Section model

Six sections, in workflow order. Every command belongs to exactly one section
(mapping from [`UI_UX_AUDIT.md`](UI_UX_AUDIT.md) §7):

| Order | Section | Purpose | Commands |
|--:|---|---|---|
| 1 | **Setup** | Build/identify the relativistic scene | Create Relativity Controller · Setup Relativistic Camera · Setup Selected Relativistic Objects · Select Relativistic Objects · Create Test Scene |
| 2 | **Preview** | Apply/clear the approximate look | Apply Doppler Material Preview · Apply Searchlight Preview · Apply Relativity Material Preview · Apply All Previews · Create Lorentz Preview Copies · Remove Lorentz Preview Copies · Clear Material Preview |
| 3 | **Octane** | Octane availability & Octane-targeted output | Octane Status · Apply Octane-Compatible Material Preview · Show AOV Plan |
| 4 | **Export** | Write data/assets for downstream use | Export Relativity Metadata JSON · Export Experimental OSL Camera |
| 5 | **Diagnostics** | Read-only introspection / troubleshooting | Octane Diagnostics |
| 6 | **Help** | Identity, status, docs | About *(and the Control Panel launcher itself)* |

## 3. Color language

Each section has one **accent** colour used for its group border/header, its
icons (§4), and any section chrome. Two cross-cutting roles - **warning/error**
and **help/docs neutral** - apply across sections. Values are flat (no gradients)
and chosen for legibility on Cinema 4D's dark UI.

| Role | Colour | Accent hex | Use |
|---|---|---|---|
| **Setup** | blue | `#3E86E0` | Setup group + icons |
| **Preview** | violet | `#8E6FE0` | Preview group + icons |
| **Octane** | orange | `#F0883C` | Octane group + icons |
| **Export** | green | `#3FB36B` | Export group + icons |
| **Diagnostics** | gray | `#9AA0A6` | Diagnostics group + icons |
| **Warning / error** | red | `#E5484D` | Destructive/clear actions, error dialogs, failed status |
| **Help / docs** | neutral cyan (alt. light gray) | `#46C6DE` (alt `#C4C8CC`) | About / Control Panel / docs links |

Supporting tones (for icon tiles and panel chrome on the dark UI):

| Token | Hex | Use |
|---|---|---|
| Icon tile (dark) | `#232323` | Solid-background icon tile, if a tile is needed for menu legibility |
| Panel text | `#E6E6E6` | Status/labels |
| Muted text | `#9AA0A6` | Secondary/hint text (same as Diagnostics gray) |

Semantic exception: a few **physics-meaningful** icons may add red/blue accents
where the meaning is essential (e.g. *Doppler* red-shift/blue-shift), layered on
top of the section accent - see §5.

## 4. Icon style

- **Flat colour only.** Solid fills, **no gradients**, no shadows, no bevels.
- **Simple geometric shapes.** Circles, rounded rectangles, triangles, lines,
  arrows. One clear idea per icon; readable as a silhouette.
- **Background:** prefer **transparent** (RGBA alpha) so icons sit on any C4D
  toolbar/menu shade. Where a menu needs a solid tile for contrast, use the dark
  tile `#232323` with the accent glyph on top (decide per integration need).
- **Sizes:** **32×32 primary** (the size C4D command icons display at). Optional
  **64×64 source** for HiDPI / future redraws. No other sizes required.
- **Construction rules** (for legibility at 32 px):
  - keep a ~3 px transparent margin; draw within the inner ~26×26;
  - minimum stroke/feature ~2 px at 32 (avoid 1 px hairlines);
  - 1-2 colours per icon: the section accent + optional white/`#E6E6E6` for a
    cut-out highlight (and red/blue only for the semantic icons in §5);
  - **no text/letters inside icons unless unavoidable** (the *About* "i" mark is
    the one allowed glyph-letter).
- **Format:** **PNG, 8-bit RGBA** only - widely supported by
  `c4d.bitmaps.BaseBitmap`. **No SVG, no multi-layer TIFF/PSD, no animated or
  exotic formats** (avoids anything that may fail to load in Cinema 4D).

## 5. Proposed icon set

The 16 prototype icons, each with its section/colour and a simple-shape glyph.
File names use the bare `<name>` (see §6). "Serves" lists the command(s) the icon
is used for; a few commands reuse the nearest icon until dedicated ones exist.

| Icon name | Section / colour | Glyph (simple shapes) | Serves command(s) |
|---|---|---|---|
| `about` | Help / cyan-neutral | circle outline + dot + short bar ("i" info mark) | About |
| `control_panel` | Help / neutral | 2×2 grid of rounded squares (panel) | Control Panel (launcher/hub) |
| `setup_controller` | Setup / blue | small disc/hub with an orbit ring + centre dot | Create Relativity Controller |
| `setup_camera` | Setup / blue | camera body rectangle + lens circle | Setup Relativistic Camera |
| `setup_objects` | Setup / blue | cube with a small selection-corner marquee | Setup Selected Relativistic Objects · Select Relativistic Objects *(reuse; future marquee variant)* |
| `create_test_scene` | Setup / blue | frame rectangle + sphere + motion arrow | Create Test Scene |
| `doppler_preview` | Preview / violet (+blue/red) | circle split into a blue-shift arc and a red-shift arc | Apply Doppler Material Preview |
| `searchlight_preview` | Preview / violet | sphere with a forward beam cone (radiating lines) | Apply Searchlight Preview |
| `all_previews` | Preview / violet | three overlapping layers (colour + beam + brackets) | Apply All Previews · Apply Relativity Material Preview *(combined)* |
| `lorentz_create` | Preview / violet | cube compressed on one axis, inward arrows `→‖←` | Create Lorentz Preview Copies |
| `lorentz_remove` | Preview / violet | same contracted cube with outward/restore arrows `←‖→` | Remove Lorentz Preview Copies |
| `octane_status` | Octane / orange | octagon outline + centre status dot | Octane Status · Apply Octane-Compatible Material Preview *(reuse; future material variant)* |
| `aov_plan` | Octane / orange | stacked channel sheets (3 offset rectangles) | Show AOV Plan |
| `export_metadata` | Export / green | page/file outline + downward export arrow | Export Relativity Metadata JSON |
| `export_osl` | Export / green | page/file outline + small node-graph dots/ray | Export Experimental OSL Camera |
| `diagnostics` | Diagnostics / gray | magnifying glass (circle + handle) | Octane Diagnostics |

**Coverage notes (honest gaps, resolved by reuse for now):**
- *Select Relativistic Objects* reuses `setup_objects`.
- *Apply Relativity Material Preview* reuses `all_previews` (both denote a
  combined apply); a dedicated composite can be added later.
- *Clear Material Preview* has **no** dedicated icon yet: render `all_previews`
  with the **red/error accent** (§3, principle 6) until a `clear_preview` icon is
  added - the destructive-labelling rule still applies.
- *Apply Octane-Compatible Material Preview* reuses `octane_status` until an
  octane-material variant exists.

## 6. File layout & naming

```
openrelativity_c4d/resources/icons/
  README.md                 # what these assets are (see that file)
  <name>.png                # 32x32 RGBA, the delivered icon
  <name>_64.png             # optional 64x64 RGBA source (HiDPI / re-export)
```

- `<name>` is exactly the icon name from §5 (e.g. `setup_camera.png`,
  `doppler_preview.png`).
- Lowercase, `snake_case`, no spaces. ASCII only.
- Keep each PNG small (a flat 32×32 icon is well under a few KB).

## 7. How icons are consumed

Icons are **optional and additive** - they must never be required for a command
to work (no behavior change). Consumption (future implementation, per the audit's
plan):

- A small safe loader resolves `<name>.png` relative to the plugin folder and
  returns a `c4d.bitmaps.BaseBitmap`, or **`None`** on any failure (missing/
  unreadable file) - so a missing icon silently falls back to today's text-only
  command. Loaded bitmaps are cached.
- The bitmap is passed as the `icon=` argument in `RegisterCommandPlugin(...)`
  (currently `icon=None` for all 20 commands) and may be shown as a small section
  header image in the Control Panel via `AddImage`.
- Section accent colours (§3) drive group borders/headers; icons carry the same
  accent so menu and panel read consistently.

## 8. Generation & replacement

- **Locally generated, never downloaded.** Icons are produced by a local script
  in this repo (e.g. a future `tools/generate_icons.py`) using **only the Python
  standard library** (`zlib` + `struct` to emit PNG) - **no Pillow, no external
  icon library, no network**. This keeps the repo dependency-free (matching the
  core's no-third-party rule) and reproducible.
- **Prototype, replaceable.** These are intentionally minimal placeholders so the
  UI feels intentional now; they can be swapped for professionally designed icons
  later **without code changes** by replacing the PNGs in place (same names).
- **Lightweight.** Flat 32×32 PNGs only (+ optional 64×64 sources); no heavy or
  exotic formats.

## 9. Control Panel layout (implemented)

`c4d/control_panel.py` implements this system as a compact, non-modal
`GeDialog` (`ControlPanelDialog`), built from small helper methods
(`build_status_area`, `build_setup_tab`, `build_preview_tab`, `build_octane_tab`,
`build_export_tab`, `build_diagnostics_tab`, `refresh_status`):

- **Persistent status area** at the top: Controller, Camera, ORC objects, Octane,
  and the **Last action** message - refreshed after every button and via
  **Refresh**.
- **Workflow tabs** (`TabGroupBegin`) so only one section's buttons show at once,
  keeping the window short: **Setup · Preview · Octane · Export · Help**. Every
  command stays reachable (the previously-omitted ones - Select Objects, Apply All
  Previews, Apply Octane Material, Export OSL - are now included).
- **Buttons** call the registered commands via `c4d.CallCommand` (no behavior
  change). Each row is `[icon] [text button]`: the icon comes from
  `icon_loader.safe_icon(...)` via a guarded bitmap-button and **degrades to a
  plain text button** if the icon or the bitmap-button GUI is unavailable - the
  text button is always the reliable click target.
- **Help tab** adds read-only conveniences that need no Octane: *UI Diagnostics*
  (scene status + which command icons loaded) and *Open Docs Folder* (best-effort,
  falls back to showing the path).
- **Button/widget IDs** are defined centrally as class constants, with dynamic
  command-row gadget IDs allocated from a single `_GADGET_BASE`.

Destructive/clear actions (*Clear Material Preview*, *Remove Lorentz Copies*) use
the red-accented icon per principle 6.

### Screenshots

_Placeholder - capture in Cinema 4D and add under `docs/images/` (none included
yet)._ Suggested: the **Setup** and **Preview** tabs, and the status area with a
scene loaded.

## 10. Remaining follow-ups

- Optional: group the **Extensions** menu entries into a grouped submenu
  (`C4DPL_BUILDMENU`), driven from the same section model.
- Optional: section header images in the Control Panel tabs.

---

*See also:* [`UI_UX_AUDIT.md`](UI_UX_AUDIT.md) (command inventory + section
mapping + implementation plan) and
[`../openrelativity_c4d/resources/icons/README.md`](../openrelativity_c4d/resources/icons/README.md).
