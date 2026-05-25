# TODO - Prioritized Next Steps

Prioritized roadmap of the next work, highest first. See
[`docs/ROADMAP.md`](docs/ROADMAP.md) for the phased plan and
[`docs/KNOWN_LIMITATIONS.md`](docs/KNOWN_LIMITATIONS.md) for what is intentionally
approximate today.

## 1. Registered plugin IDs (blocker for distribution)
Replace the **temporary private prototype IDs** in `openrelativity_c4d/ids.py`
(derived from `ORC_ID_BASE`) with **registered Plugin Café IDs**
(https://plugincafe.maxon.net/). They are off Maxon's `1000001-1000010` test
range but are unregistered guesses, so they can still collide with other plugins.
- One unique ID per command/dialog (or register a contiguous block and set
  `ORC_ID_BASE` to its first ID).
- Keep `ids.all_ids()` and run `python tools/audit_plugin_ids.py` for the
  collision/usage self-check.
- This must be done before the plugin is shipped or run alongside third-party
  plugins.

## 2. Real Cinema 4D `TagData` / `ObjectData` implementation
Move from "Null + User Data" to proper plugin types. **Plan + staged steps:**
[`docs/C4D_PLUGIN_TYPE_MIGRATION.md`](docs/C4D_PLUGIN_TYPE_MIGRATION.md) (Step 1,
the canonical `field_specs` schema, is done).
- Controller as `SceneHookData`/`ObjectData`; camera & object settings as
  `TagData`; Lorentz contraction as an `ObjectData` **deformer** (live).
- Author description resources (`.res`/`.h`/`.str`) under
  `openrelativity_c4d/c4d/descriptions/`.
- Keep the field-name-based accessors working (or migrate to description IDs).
- Benefit: proper Attribute Manager UI, live evaluation, cleaner undo.

## 3. Better velocity-direction handling
Improve `cos_theta` / relative motion beyond the current pivot-based,
object/global approximation:
- Combine the **camera's own velocity** into a true object↔observer **relative
  beta** (use `core.transforms.add_velocity`).
- Optionally per-point / per-UV direction instead of one value per object.
- Handle arbitrary world-space velocity for Lorentz (not just the dominant local
  axis), and consider the retarded-time apparent position
  (`core.transforms.apparent_position`) in the previews.

## 4. Better material restoration
Make the material preview even safer/cleaner:
- Snapshot and restore the object's exact original material assignment (incl.
  per-polygon selections) instead of only layering + clearing.
- Preserve more of the base material (specular/roughness) under the Doppler tint.
- Consider a single managed "preview" state per object with explicit save/restore.

## 5. Octane node-graph (material) support
Implement native Octane materials in `octane/material_adapter.py`:
- Resolve the verified Octane material type/ID and the node-graph vs. legacy
  parameter model for the installed version (see
  `required_octane_material_info()`).
- Map Doppler colour -> diffuse/albedo and searchlight -> emission colour/power.
- Keep the Standard fallback when Octane/the mapping is unavailable.

## 6. AOV automation
Turn `octane/aov_adapter.py` from a *plan* into real passes:
- Verify the Octane render-settings/AOV Python API (see
  `REQUIRED_OCTANE_AOV_INFO`).
- Auto-create `ORC_DopplerFactor`, `ORC_Beta`, `ORC_Searchlight`,
  `ORC_ObjectVelocity`, `ORC_RelativityMask`.
- Bake per-object values into the passes; flip `automatic_creation_supported`.

## 7. OSL camera research
De-risk the experimental OSL camera
([`docs/OSL_CAMERA_EXPERIMENTS.md`](docs/OSL_CAMERA_EXPERIMENTS.md)):
- Determine the actual Octane OSL-**camera** ray I/O contract (origin + direction
  globals) for the target Octane version.
- Implement a correct ray-generation model; only then make any physical claims.
- Decide feasibility per Octane/C4D version before promoting beyond experimental.

## 8. C++ migration plan
Prepare the path to the Cinema 4D C++ SDK (see
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) §7):
- Reimplement `core/` (numeric, dependency-free API) in C++ with parity tests
  against the Python core.
- Re-author the `c4d/` plugin classes against the C++ SDK (`TagData`/`ObjectData`/
  `SceneHookData`/`CommandData`); reuse the `descriptions/` resources.
- Keep the Octane adapter boundary unchanged.

## Cross-cutting / smaller
- Wire `tools/verify_repo.py` into CI / a pre-commit hook.
- **Time-delay / light-cone** (Phase 2): implement the retarded-time solver +
  C4D history sampler/baker on top of `core.history`. Design:
  [`docs/TIME_DELAY_LIGHT_CONE_DESIGN.md`](docs/TIME_DELAY_LIGHT_CONE_DESIGN.md).
- Time-dilation across the animation timeline; causal appear/disappear gating.
- Mesh subdivision utility (smooth contraction on coarse meshes).
- Example scenes under `examples/`.
- Per-frame metadata export across a frame range.
