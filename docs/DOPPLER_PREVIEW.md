# Doppler Material Preview

The first **visible** effect in OpenRelativity_c4d. It tints each relativistic
object toward blue (approaching) or red (receding) using a generated Cinema 4D
material, so you can see an approximate relativistic Doppler shift in the
Standard/Physical renderer.

> ⚠️ **This is an artistic approximation, not spectral rendering.**
> Real relativistic Doppler shifting moves a full spectral power distribution
> through wavelength space (and folds in IR/UV). Here we simply nudge an RGB
> colour warmer or cooler, scaled by an art-directable strength. It is meant to
> *read* correctly and be controllable, not to be physically exact. See
> [`ARCHITECTURE.md`](ARCHITECTURE.md) and
> [`ORIGINAL_OPENRELATIVITY_REFERENCE.md`](ORIGINAL_OPENRELATIVITY_REFERENCE.md)
> for the difference.

## Commands

- **Extensions > “OpenRelativity C4D: Apply Doppler Material Preview”** — computes
  and applies the preview to every eligible relativistic object.
- **Extensions > “OpenRelativity C4D: Clear Doppler Material Preview”** — removes
  everything the preview created.

It is **not live**: re-run *Apply* after you move objects/the camera or change
any beta/velocity/strength setting. The **About** dialog shows how many preview
materials currently exist.

## What it does, step by step

For each object that has relativistic User Data with both **ORC Object Enabled**
and **Doppler Material Preview** on:

1. **Effective beta** (`v/c`), in priority order:
   1. the controller's **Global Beta Override**, if > 0;
   2. otherwise the object's **Object Beta**, if > 0;
   3. otherwise `|Object Velocity| / c`, where `c` is the controller's
      **Artificial Speed of Light** (or the core default if there is no controller).

   The result is clamped to ≤ `99.9%` of `c`.

2. **Direction** (`cos_theta`, where `+1` = approaching, `-1` = receding) from
   [`core.transforms.cos_theta_towards_observer`](../openrelativity_c4d/core/transforms.py):
   it compares the object's velocity direction to the line of sight to the
   observer.
   - **Use Camera Relative Direction** on (and a relativistic camera exists):
     line of sight = `camera_position − object_position` (true geometry).
   - Off (but a camera exists): line of sight = the camera's forward axis
     (object assumed in front of the camera).
   - No camera: line of sight defaults to world `−Z`.
   - If the object has no velocity direction (e.g. you set *Object Beta* directly
     with zero velocity), `cos_theta = 0` → the **transverse** case, which is a
     mild redshift (`factor = gamma`).

3. **Doppler factor** = `doppler_factor(beta, cos_theta)` — `< 1` blueshift,
   `> 1` redshift.

4. **Colour** = `approximate_rgb_doppler_shift(base_colour, factor, strength)`,
   where `strength` is the controller's **Doppler Strength**. The base colour is
   read from the object's existing (non-ORC) material if it has one, otherwise a
   neutral grey `(0.8, 0.8, 0.8)`. The output is always clamped to `0..1`.

5. The colour is written to a generated **Standard** material named
   `ORC_Doppler_<object name>` and applied to the object (see below).

## How materials are applied (non-destructive)

The preview **never deletes or rewrites your existing materials**. Instead:

- It creates/updates one Standard material per object, `ORC_Doppler_<name>`.
- It adds (or reuses) a single **Texture tag** on the object that links that
  material. Because later texture tags override earlier ones for the whole
  object, the preview overrides the look without modifying the originals.
- **Clear** removes only the ORC texture tags and the `ORC_Doppler_*` materials.
  Your original tags/materials are left exactly as they were.

This is why no "original material backup" is needed: the originals are never
touched. (If you had per-polygon material selections, note the limitation below.)

## Compatibility

- Uses the **Standard material** (`Mmaterial`), rendered by both the **Standard**
  and **Physical** renderers. Try those first.
- **Octane is not required and not used here.** The object's *Octane Material
  Sync* flag is a separate, not-yet-implemented stub; this preview is pure C4D.

## Limitations (by design, for now)

- **Per-object, uniform colour** — one shift for the whole object, not per-pixel
  or per-vertex as the original OpenRelativity shader does.
- **Pivot-based direction** — `cos_theta` uses the object's pivot position, not
  each surface point.
- **Beta is object/global**, not yet the true relative speed between object and
  observer (the camera's own velocity is not yet combined in).
- **Last-tag-wins** — the preview overrides the whole object; per-polygon
  material selections are not preserved in the preview, and the base colour is
  read from the last non-ORC texture tag.
- **Not live** — re-run *Apply* after changes.
- **Searchlight/beaming and Lorentz deformation are not part of this preview**
  yet (separate later steps).

## Quick workflow

1. *Create Relativity Controller* (sets the speed of light, global beta, Doppler
   strength).
2. *Setup Relativistic Camera* (the observer).
3. Select objects and *Setup Selected Relativistic Objects*; give them an
   *Object Beta* or *Velocity X/Y/Z*.
4. *Apply Doppler Material Preview*.
5. Render with **Standard** or **Physical**.
6. Adjust settings and re-apply; *Clear Doppler Material Preview* to remove.

## For developers

The math is pure and unit-tested
([`core/doppler.py`](../openrelativity_c4d/core/doppler.py),
[`core/transforms.py`](../openrelativity_c4d/core/transforms.py)); the Cinema 4D
side lives in
[`c4d/doppler_material.py`](../openrelativity_c4d/c4d/doppler_material.py)
(`apply_preview`, `clear_preview`, `count_preview_materials`). The C4D material
behaviour is **manual-tested** - there are no automated tests for it, since it
requires a running Cinema 4D.
