# Lorentz Geometry Preview

Shows relativistic **length contraction** as a non-destructive, **scaled
duplicate** of each relativistic object. Each eligible object gets a copy named
`ORC_LorentzPreview_<original name>`, scaled shorter along its direction of
motion; the original is left unedited and (optionally) hidden.

> ⚠️ **Limitations - read this first.**
> - **Axis-aligned approximation only.** The copy is scaled along its **dominant
>   local X/Y/Z axis** (the largest component of the velocity), *not* an arbitrary
>   world-space velocity direction. Diagonal motion and rotated objects are
>   approximate.
> - **No Terrell rotation / apparent geometry.** Real relativistic appearance
>   includes apparent rotation/shear from light-travel-time (the
>   Terrell–Penrose effect). That is **not implemented**; this is a plain length
>   contraction look.
> - **No point-level editing.** Geometry points are never modified - only the
>   duplicate's object scale. This keeps it fast and fully reversible, but it is
>   a transform, not a true deformation.

## Commands

- **Extensions > “OpenRelativity C4D: Create Lorentz Preview Copies”** — creates
  the contracted duplicates.
- **Extensions > “OpenRelativity C4D: Remove Lorentz Preview Copies”** — deletes
  the duplicates and restores the originals' visibility.

Targets the **selected** relativistic objects, or **all** of them if none are
selected. Safe to run repeatedly: an existing copy for a source is replaced. The
**About** dialog shows how many copies exist.

## What it does, step by step

For each relativistic object with **ORC Object Enabled** and **Lorentz
Deformation Preview** on:

1. **beta** is resolved as for the material preview (global override → *Object
   Beta* → `|velocity| / c`), clamped to ≤ `99.9%`.
2. **Contraction scale** = `lorentz_contraction_scale(beta, strength)` from the
   math core, where `strength` is the controller's *Lorentz Deformation
   Strength*. At `beta = 0` (or strength 0) this is `1.0` (no change); it shrinks
   toward `0` as beta rises.
3. **Axis** = the dominant component of the object's velocity vector
   (`transforms.dominant_axis`). If the object has **no velocity** (e.g. you set
   *Object Beta* directly), the copy is contracted along the object's **local Z**
   axis as an assumed direction of motion.
4. The object is **cloned**, renamed `ORC_LorentzPreview_<name>`, and its scale on
   that one axis is multiplied by the contraction factor. The clone keeps the
   original's materials/tags, so it looks like the original - just shorter.

## Originals: hidden, then restored

By default the source object is **hidden** (editor + render) while its preview
copy is shown, controlled by the controller's **Hide Originals (Lorentz
Preview)** toggle (default on). Turn it off to keep originals visible.

Hiding is **non-destructive**: each copy stores the source's original visibility
in its own User Data (*ORC Lorentz Source* link, plus the editor/render
visibility values). *Remove Lorentz Preview Copies* reads those back and restores
exactly what was there. The whole operation is also a single undo step.

## Combining with the material preview

The preview copies are clones, so they inherit whatever materials the source had
**at the moment of cloning** - including the Doppler/searchlight preview material
if it was already applied. For a combined look:

1. Apply the material preview(s) **first** (so the source carries the
   `ORC_Preview_<name>` material), **then** create the Lorentz copies; or
2. If you change materials afterward, re-run *Create Lorentz Preview Copies* to
   refresh the clones.

Lorentz preview copies are **not** themselves treated as authored relativistic
objects (they are excluded from the ORC object collection), so the material and
selection commands act on your real objects, not the generated copies.

## Compatibility & non-destructive guarantees

- Pure object **transform** (scale) on a **duplicate**; your original geometry,
  materials, and tags are never modified.
- The only change to an original is its **visibility** (when hiding is on), and
  that is restored on removal.
- Renderer-agnostic (it is just scene geometry) - works in Standard/Physical;
  **Octane is not required**.

## Quick workflow

1. *Create Relativity Controller* (set *Lorentz Deformation Strength* and, if you
   like, *Hide Originals (Lorentz Preview)*).
2. Select objects, *Setup Selected Relativistic Objects*, and give them a
   *Velocity X/Y/Z* (the dominant axis sets the contraction direction).
3. *(Optional)* apply a material preview first for combined colour + contraction.
4. *Create Lorentz Preview Copies*; render with Standard/Physical.
5. *Remove Lorentz Preview Copies* to restore.

## For developers

Pure math: [`core/relativity_math.py`](../openrelativity_c4d/core/relativity_math.py)
(`lorentz_contraction_scale`) and
[`core/transforms.py`](../openrelativity_c4d/core/transforms.py)
(`dominant_axis`) - both unit-tested. Cinema 4D side:
[`c4d/lorentz_preview.py`](../openrelativity_c4d/c4d/lorentz_preview.py)
(`create_preview`, `remove_preview`, `count_preview_copies`). The C4D behaviour
is **manual-tested** (no automated C4D tests).
