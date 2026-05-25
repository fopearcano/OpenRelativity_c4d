# AOV / Compositing Pipeline (Octane)

The plan for exporting **Relativity AOVs** (render passes) so the relativistic
look can be finished and controlled in compositing, rather than baked into the
beauty render.

> ⚠️ **Scaffolding only - no automatic AOV creation yet.**
> This page describes the *intended* workflow and the AOVs we want. The plugin
> does **not** create Octane AOVs automatically: there is no verified Octane AOV
> Python API/ID mapping yet, so setup is **manual** for now. The AOVs are
> **approximations** (per-object, pivot-based - see limitations below), not
> physically exact passes. Nothing here requires Octane to be installed.

## The "Show AOV Plan" command

**Extensions > “OpenRelativity C4D: Show AOV Plan”** lists the desired AOVs and
reports whether automatic Octane AOV creation is currently supported (it is not)
plus the detected Octane/renderer status. It is read-only - it changes nothing.

Programmatic access: `octane/aov_adapter.py` →
`get_relativity_aov_plan()` (static plan), `detect_render_settings(doc)`
(best-effort), `create_relativity_aovs(doc)` (safe no-op today),
`aov_creation_supported(doc)`.

## Desired Relativity AOVs

| AOV | Kind | Meaning | Source | Compositing use |
|---|---|---|---|---|
| `ORC_DopplerFactor` | scalar | Doppler factor (`<1` blue, `>1` red) | `core.doppler.doppler_factor` (approx, per-object) | Gradient/colour remap to retint or correct the beauty pass |
| `ORC_Beta` | scalar | Speed as `v/c` | `object_tools.effective_beta` | Mask/modulate effects by speed |
| `ORC_Searchlight` | scalar | Beaming intensity multiplier | `core.searchlight.searchlight_intensity_multiplier` | Multiply/screen to brighten/dim by motion |
| `ORC_ObjectVelocity` | vector | Object world velocity | object User Data (Velocity X/Y/Z) | Direction-aware grades; motion vectors |
| `ORC_RelativityMask` | mask | Coverage of relativistic objects | object/material ID buffer | Constrain all relativity comp ops to these objects |

## Intended Octane AOV workflow

### 1. Beauty render from Octane
Render the shot normally with Octane. The relativistic *look* may already be in
the beauty (via the material/Lorentz previews), but for flexibility you usually
want it (or part of it) as separate passes.

### 2. Relativity AOVs / masks / material IDs (manual today)
Until automatic creation lands, build the passes by hand:

- **`ORC_RelativityMask`** - add an Octane **Object ID / Material ID** (or
  render-layer) pass and assign the relativistic objects to it. This is the
  cleanest, most reliable pass and the anchor for everything else.
- **`ORC_Beta` / `ORC_DopplerFactor` / `ORC_Searchlight`** - read the per-object
  values from the plugin (the object User Data + the pure `core` math), bake them
  into a **greyscale material** (or vertex colour) on a copy, and output that as a
  **material AOV**. One value per object today (uniform across the surface).
- **`ORC_ObjectVelocity`** - encode the velocity vector as RGB in a material AOV.

### 3. Post-compositing (Fusion / Nuke / After Effects)
- Use `ORC_RelativityMask` to **limit** all relativity operations to the
  relativistic objects.
- Drive a **gradient/lookup** from `ORC_DopplerFactor` (or `ORC_Beta`) to push
  colour toward blue/red - artist-controllable, re-gradable without re-rendering.
- **Multiply/screen** `ORC_Searchlight` onto the beauty to add the beaming
  brightness; clamp to taste.
- Use `ORC_ObjectVelocity` for direction-aware tweaks or to build motion vectors.

This keeps the relativistic grade **fully in the comp**, so it can be tuned after
the (expensive) render.

### 4. Limitations of the approximated AOVs
- **Per-object, uniform** - one value per object (pivot-based), not per-pixel or
  per-surface-point. Curved/large objects won't have a smooth gradient.
- **Object/global beta** - the camera's own velocity is not yet folded into the
  relative beta.
- **Approximate, not radiometric** - `ORC_Searchlight` and `ORC_DopplerFactor`
  are art-directable approximations, not calibrated physical quantities.
- **Manual baking** - values must be baked into materials/passes by hand until
  the automatic path exists; expect to redo it when settings change.
- **No guarantee of full physical relativistic ray tracing** inside Octane.

## TODO - to make automatic AOV creation work

`aov_adapter.REQUIRED_OCTANE_AOV_INFO` lists what must be verified first:

1. The Octane **render-settings / video-post** container layout in the Python API
   (where AOVs/passes live) for the installed version.
2. The Octane API call(s) to **add and name** a custom AOV / render pass.
3. Which Octane AOV types can carry custom **scalar/vector** data (render-AOV
   nodes, material AOVs, object/material ID buffers).
4. How to **bind per-object data** (Doppler/beta/searchlight) into a pass.

Once confirmed, implement them inside `create_relativity_aovs(doc)` and flip
`automatic_creation_supported` to `True`; until then the plugin stays honest and
points here for manual setup.

See [`OCTANE_INTEGRATION.md`](OCTANE_INTEGRATION.md) for the overall Octane plan
(Phase C is this AOV work) and the isolation guarantees.
