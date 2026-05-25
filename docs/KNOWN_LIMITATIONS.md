# Known Limitations

OpenRelativity_c4d is an **artist-facing approximation** of special-relativistic
appearance, not a physics-grade renderer. This page lists, plainly, what it does
**not** do, so results are interpreted correctly. These are **by design / not yet
implemented**, not bugs. See also [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) (scope)
and [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Rendering & physics

### Not full ray-traced relativistic rendering
The plugin does **not** trace light along relativistic paths or solve the
observed image physically. It approximates the *look* by adjusting standard
material parameters and by scaling duplicate geometry. There is no custom
renderer and no relativistic light transport.

### Doppler colour is an approximate RGB shift, not spectral
The Doppler effect is a simple, art-directable **RGB tint** (toward blue when
approaching, red when receding), scaled by a strength. It does **not** shift a
spectral power distribution through wavelength space and does not fold in
IR/UV bands the way a spectral pipeline (or the original OpenRelativity shader)
would. Treat it as a believable look, not a measured colour.

### Searchlight is an artistic intensity multiplier
The searchlight / beaming effect is an **artistic brightness multiplier**
(with a small emission "glow" when strongly approaching), clamped to safe
ranges. It is not calibrated radiometric intensity, and the exponent/clamps are
chosen for a usable preview, not physical accuracy.

### Lorentz deformation is simplified - NOT Terrell rotation
Length contraction is shown by **scaling a duplicate object** along its
**dominant local X/Y/Z velocity axis** - an axis-aligned approximation. It does
**not** implement the true apparent shape (the **Terrell–Penrose rotation** /
apparent-position distortion from light-travel-time), and it does not edit the
original geometry's points. Diagonal motion and rotated objects are approximate.

### Time-delay / light-cone sampling not implemented yet
The previews are **instantaneous**: they do not account for light-travel-time, so
objects are not shown at their *retarded* (apparent) positions, and there is no
causal "appear/disappear when the light arrives" gating. (A retarded-time solver
exists in `core.transforms.apparent_position` but is **not** wired into the
previews yet.)

## Approximation scope

- **Per-object, not per-pixel/per-vertex.** Each object gets one Doppler colour
  and one brightness/contraction; there is no per-surface-point variation.
- **Pivot-based direction.** `cos_theta` uses the object's pivot vs. the camera
  viewing axis / line of sight, not each shading point.
- **Object/global beta.** The relative speed used is the object's own beta (or a
  global override); the **camera's own velocity is not yet combined** into a true
  object↔observer relative beta.
- **Previews are not live.** Re-run the apply commands after moving objects/the
  camera or changing settings - nothing updates automatically.
- **Modelling assumptions** (inherited from special relativity / the original
  project): one freely-moving observer; other objects at constant velocity; no
  relativistic lighting/shadows; no general relativity or gravity.

## Octane

### Octane integration is adapter/scaffolding-first
Octane support is **isolated and optional** and currently provides: safe
**detection/status**, a **material adapter that falls back to Standard
materials** (no native Octane material is created yet), an **AOV plan** that
documents **manual** setup (no automatic AOV creation), and the experimental OSL
export below. Native Octane material/AOV creation needs verified Octane IDs/API
data (enumerated in the code and [`OCTANE_INTEGRATION.md`](OCTANE_INTEGRATION.md)
/ [`AOV_PIPELINE.md`](AOV_PIPELINE.md)). There is **no guarantee of full physical
relativistic ray tracing inside Octane.**

### OSL camera is experimental
The exported OSL camera shader
([`OSL_CAMERA_EXPERIMENTS.md`](OSL_CAMERA_EXPERIMENTS.md)) is a **clearly-marked
placeholder**: not physically complete, not wired into Octane, with unverified
ray I/O bindings, no ray-origin output, and no light-travel-time. It is a
look-dev experiment, not a feature.

## Engineering / distribution

- **C4D-side behaviour is manual-tested only.** Anything touching `c4d`
  (materials, geometry, dialogs, undo, save dialogs, render) is verified by hand
  inside Cinema 4D (see [`TEST_PLAN_C4D.md`](TEST_PLAN_C4D.md) and
  [`TEST_PLAN_OCTANE.md`](TEST_PLAN_OCTANE.md)); only the pure math and
  import-safe helpers are unit-tested.
- **Metadata export is single-frame.** Export per frame for sequences; values are
  the same approximations described above (noted in each file's
  `approximation_notes`).
- **Version coverage.** Targets Cinema 4D 2023+; not validated across every C4D /
  Octane version, and several Cinema 4D APIs used by the `c4d/` layer have not
  been exercised in this environment.

### Plugin IDs

Cinema 4D requires every plugin element to have a **globally unique** integer ID;
if two plugins claim the same ID, only one of them loads at startup. So a
duplicate ID can make this plugin **block another plugin** (or be blocked).

- All IDs are centralized in `openrelativity_c4d/ids.py` and every registration
  uses a named `ids.ID_ORC_*` constant.
- They are **temporary private prototype IDs** (derived from a single
  `ORC_ID_BASE`), **not** registered with Maxon and **not** guaranteed unique -
  they only avoid the reused `1000001–1000010` test range.
- **Before public distribution**, replace them with official IDs from the Maxon
  Plugin Café (https://plugincafe.maxon.net/). See
  [`DEVELOPER_NOTES.md`](DEVELOPER_NOTES.md) → "Plugin IDs".
- **If another local plugin is blocked**, change `ORC_ID_BASE` in `ids.py` and
  restart Cinema 4D; verify with `python tools/audit_plugin_ids.py`.
