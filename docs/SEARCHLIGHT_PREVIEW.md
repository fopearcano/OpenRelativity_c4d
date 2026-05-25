# Searchlight (Beaming) Material Preview

The relativistic **searchlight / beaming** effect: a surface moving **toward** the
observer looks **brighter** and one moving **away** looks **dimmer**. This preview
approximates it by driving a generated Cinema 4D material's **brightness** (and a
little **luminance/emission** for strong approach), so you can see it in the
Standard/Physical renderer.

> ⚠️ **This is an artistic approximation, not radiometric rendering.**
> Real beaming changes specific intensity by a factor related to the Doppler
> shift (`~(1/shift)^3`) across the whole image. Here we map that factor onto a
> single material's diffuse brightness plus an emission glow, **clamped to safe
> artistic ranges**. It is meant to *read* correctly and stay controllable, not
> to be physically accurate. The Doppler colour side is documented in
> [`DOPPLER_PREVIEW.md`](DOPPLER_PREVIEW.md).

## Commands

- **Extensions > “OpenRelativity C4D: Apply Searchlight Preview”** — brightness
  only (no colour shift).
- **Extensions > “OpenRelativity C4D: Apply Relativity Material Preview”** — the
  **combined** preview: Doppler tint **and** searchlight brightness together.
- **Extensions > “OpenRelativity C4D: Clear Material Preview”** — removes every
  ORC-generated preview material/tag (shared with the Doppler preview).

These are **not live** — re-run after moving objects/the camera or changing any
setting.

## What it does, step by step

For each relativistic object with **ORC Object Enabled** and **Searchlight
Material Preview** on:

1. **beta** and **cos_theta** are resolved exactly as for the Doppler preview
   (see [`DOPPLER_PREVIEW.md`](DOPPLER_PREVIEW.md)): beta from the global override,
   the object's *Object Beta*, or `|velocity|/c`; `cos_theta` from the object's
   velocity vs. the line of sight to the camera (`+1` approaching, `-1` receding).
2. **Multiplier** `M = searchlight.searchlight_intensity_multiplier(beta,
   cos_theta, searchlight_strength)` from the math core, where
   `searchlight_strength` is the controller's *Searchlight Strength*. Internally
   `M ≈ (1/doppler_factor)^3`, blended by strength and clamped.
3. The multiplier is mapped to the material:
   - **Colour brightness** = `clamp(M, 0.05, 4.0)` — never fully black, capped at
     400 %. This dims (`M < 1`) or brightens (`M > 1`) the diffuse colour.
   - **Luminance (emission)**, only when `M > 1`:
     brightness `= clamp((M − 1) × 0.5, 0, 1.0)`, tinted by the (possibly
     Doppler-shifted) colour, so strongly approaching surfaces "glow".

`beta = 0` (a static object) gives `M = 1` → no change.

## Composition with Doppler

Both effects write to **one shared material per object**,
`ORC_Preview_<object name>`:

- *Apply Doppler Material Preview* → sets the **colour**, brightness neutral.
- *Apply Searchlight Preview* → sets **brightness/luminance**, colour = the
  object's base (un-shifted).
- *Apply Relativity Material Preview* → sets **both** (shifted colour **and**
  brightness/luminance).

Each command rewrites the material to a fully defined state, so they're
predictable. Running a single-effect command does **not** accumulate on top of
the other — use the **combined** command to see both at once.

## Compatibility & limitations

- Uses the **Standard material** (`Mmaterial`); renders in **Standard** and
  **Physical**. **Octane is not required or used** here (the object's *Octane
  Material Sync* flag is a separate, not-yet-implemented stub).
- **Non-destructive**: your materials are never modified. A single extra Texture
  tag links the generated material and overrides the look; *Clear* removes only
  the ORC tags and `ORC_Preview_*` materials.
- **Per-object, uniform** — one brightness for the whole object, not per-pixel.
- **Pivot-based direction**, **object/global beta** (the camera's own velocity is
  not yet combined in), **last-tag-wins** for the base look — same caveats as the
  Doppler preview.
- The brightness/emission numbers are **artistic, clamped approximations**, not
  calibrated luminance. Treat them as a look, not a measurement.

## Quick workflow

1. *Create Relativity Controller* (set *Searchlight Strength*).
2. *Setup Relativistic Camera*.
3. Select objects, *Setup Selected Relativistic Objects*, give them an
   *Object Beta* or *Velocity X/Y/Z* and a direction (toward/away from camera).
4. *Apply Searchlight Preview* (brightness only) or *Apply Relativity Material
   Preview* (with Doppler colour).
5. Render with **Standard** or **Physical**; *Clear Material Preview* to remove.

## For developers

Pure math: [`core/searchlight.py`](../openrelativity_c4d/core/searchlight.py)
(`searchlight_intensity_multiplier`) and
[`core/transforms.py`](../openrelativity_c4d/core/transforms.py)
(`cos_theta_towards_observer`) — both unit-tested. Cinema 4D side:
[`c4d/preview_material.py`](../openrelativity_c4d/c4d/preview_material.py)
(`apply_preview(doc, do_doppler, do_searchlight)`, `clear_preview`). The C4D
material behaviour is **manual-tested** (no automated C4D tests).
