# `c4d_plugin` — Cinema 4D integration layer

The **glue layer**. Imports `c4d` and `relativity_core`, reads scene state, calls
the math core, and writes results back to objects and materials. Keep arithmetic
here to a minimum — it belongs in `relativity_core`. Octane is reached **only**
through `adapters/octane` (never imported directly here).

Planned components (see [`../../docs/ARCHITECTURE.md`](../../docs/ARCHITECTURE.md) §4):

- `scene_controller` — global `c`, observer velocity, time (`SceneHookData`/`CommandData`).
- `camera_tag` — observer frame; relativistic velocity addition (`TagData`).
- `object_tag` — per-object world velocity and flags (`TagData`).
- `lorentz_deformer` — geometry transform on real points (`ObjectData` deformer + bake command).
- `doppler_material` — per-object color/luminance adjustment.
- `res/` — Cinema 4D resource/description files.

Targets the Python 3 runtime bundled with **Cinema 4D 2023+**.

> **No code yet (Phase 0).** This stub documents intent only.
