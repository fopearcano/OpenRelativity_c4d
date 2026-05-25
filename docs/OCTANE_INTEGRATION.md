# Octane Integration

How OpenRelativity_c4d relates to **Octane for Cinema 4D** - today (detection,
diagnostics, and an experimental native-material attempt with Standard fallback)
and the planned phases.

> **Core guarantee.** The plugin has **no dependency on Octane**. It imports and
> runs fully with Octane absent; nothing here is required for the controller,
> camera, objects, or the Standard/Physical previews. All Octane code is isolated
> in the `openrelativity_c4d/octane/` package and is reached only through the
> adapter facade - the rest of the plugin never imports an Octane module.

## What exists today: detection, status & diagnostics

The plugin can *detect* Octane, report status, and **diagnose** the installed
Octane build (its plugin IDs/classes and material parameters). It does **not**
yet modify Octane render settings or build Octane node graphs.

- **Extensions > “OpenRelativity C4D: Octane Status”** opens a dialog with the
  current report.
- **Extensions > “OpenRelativity C4D: Octane Diagnostics”** opens a read-only
  report of the detected Octane IDs/classes and material parameters (see
  [Octane Diagnostics](#octane-diagnostics-capture-the-real-ids) below).
- `octane/detection.py`:
  - `detect_octane_available()` - best-effort boolean; **never raises**. It
    combines a guarded import of the Octane Python module (`c4doctane`) with an
    **ID-independent name scan** of the registered video-post / material / shader
    plugins (looking for "octane"). Known Octane plugin IDs are used only as
    optional hints, so unknown or changed IDs cannot hard-fail anything.
  - `get_octane_status_report(doc)` - returns a safe dict:
    `octane_detected` (`true`/`false`/`unknown`), `octane_renderer_active`
    (`true`/`false`/`unknown`), `module_importable`, `matched_plugins`, and a
    `warnings` list of current limitations.
  - `octane_plugins()` - returns `[{name, id, type}, ...]` for every registered
    plugin whose name contains "octane", scanning the material / video-post /
    shader / object / tag categories. ID-independent and never raises; returns
    `[]` outside Cinema 4D.

The active-renderer check identifies Octane by the active engine's **plugin
name** (again ID-independent), falling back to `unknown` when it cannot be
determined.

## Octane Diagnostics: capture the real IDs

Because this plugin is built and tested in an environment with **neither Cinema
4D nor Octane installed**, the exact Octane material/object/camera IDs and the
material's colour/emission parameter description IDs **could not be identified
here**. Rather than hardcode guesses, the plugin discovers them **at runtime**
and gives you a command to capture them in *your* Cinema 4D + Octane install.

- **Extensions > “OpenRelativity C4D: Octane Diagnostics”** runs
  `octane/diagnostics.py: collect_diagnostics(doc)` and shows the result. It is
  **read-only** - it changes nothing in the scene or in Octane. The report lists:
  - `octane_module_importable` - whether `c4doctane` imports;
  - `plugins` - every Octane-looking plugin as `[{name, id, type}]` (material,
    video-post/renderer, shader, object, tag) - this is where the **material,
    camera and renderer IDs** appear;
  - `material_type_id` - the resolved Octane material type ID (or "not found");
  - `material_parameters` - the colour/vector/real parameters of a throwaway
    Octane material, each as `{name, descid, dtype}` - this is where the
    **diffuse/albedo and emission parameter IDs** appear;
  - `notes` - read-only reminder + pointer to this document.

If you are extending Octane support, run this command and share the output: it
contains exactly the IDs/parameter names the adapter needs to verify its
runtime discovery against your Octane version.

## Octane-compatible material preview (native attempt + safe fallback)

The **material adapter** now *attempts a native Octane material* using runtime
discovery, and falls back to a Standard material whenever that is not reliably
possible:

- **Extensions > “OpenRelativity C4D: Apply Octane-Compatible Material Preview”**
  applies the combined Doppler + searchlight preview, trying Octane first and
  otherwise using the Standard `ORC_Preview` material (which Octane can also
  render). The result dialog reports how many objects used Octane vs. the
  Standard fallback.
- `octane/material_adapter.py`:
  - `octane_material_type_id()` - resolves the Octane material type ID by **name
    scan** of registered material plugins, then by the candidate ID hint only if
    that plugin is actually registered; `None` otherwise.
  - `find_channel_descid(material, name_tokens, dtypes)` - finds a parameter by
    **introspecting the material's description at runtime** and matching the
    parameter *name* (e.g. "diffuse"/"albedo"/"colour") and dtype - no hardcoded
    IDs.
  - `create_or_update_octane_doppler_material(doc, obj, color, intensity)` -
    attempts a native Octane material; **never raises**. Returns a structured
    result dict: `ok` (bool), `method` (`octane` / `unavailable` / `unsupported`),
    `warnings` (list), `missing` (list of the Octane data that would harden it).
  - `required_octane_material_info()` - the documented list of what would make
    this fully verified.
- `octane/adapter.py`:
  - `apply_octane_or_fallback_material(doc, obj, color, intensity)` - tries the
    Octane material, then falls back to `preview_material.set_preview_material`,
    returning a structured result (`method` = `octane` / `fallback` / `error`).

### How the native attempt stays safe

`create_or_update_octane_doppler_material` is written so it can **never crash and
never leave a half-configured material** behind:

1. If Octane is not detected -> returns `unavailable` immediately; the scene is
   untouched and the caller uses the Standard fallback.
2. If the Octane material type cannot be resolved -> returns `unsupported`.
3. **Feasibility probe (no scene change):** it allocates a *throwaway* Octane
   material, finds the diffuse/colour parameter by description introspection,
   sets the colour, and **reads it back**. Only if the read-back matches does it
   proceed. (Node-graph-based Octane materials, where the diffuse lives in a node
   rather than a material parameter, fail this probe and fall back cleanly.)
4. **Only then** does it touch the scene, reusing the same `ORC_Preview_<name>`
   slot as the Standard preview (so *Clear Material Preview* removes it like any
   other preview material). Emission colour + power are set when those parameters
   are found, to carry the searchlight intensity.

Any failure at any step is caught and reported as `unsupported`, and the caller
falls back to the Standard material.

### Tested behavior (and what is *not* tested)

- **Verified in plain Python (no Octane / no C4D):** importing the adapter and
  diagnostics is safe; with Octane absent the adapter returns `unavailable` and
  the diagnostics report empty IDs/parameters - both **without raising**. This is
  covered by `tests/test_octane_material.py` and `tests/test_octane_diagnostics.py`
  and runs in CI via `tools/verify_repo.py`.
- **Not yet verified inside Cinema 4D + Octane:** the native material path
  (steps 3-4 above) has **not** been exercised against a real Octane build - none
  is available in this build/test environment. The read-back probe is the safety
  net: if the runtime discovery does not match your Octane version (e.g. a
  node-based material), it degrades to the Standard fallback rather than producing
  a wrong or broken material. Please run **Octane Diagnostics** and report back so
  the discovery can be confirmed/hardened.

### What would make native Octane materials fully verified

`required_octane_material_info()` enumerates what to confirm (the adapter already
discovers these at runtime; this is about *verifying* that discovery):

1. The Octane **material type** actually targeted on your install (diffuse /
   universal / standard-surface) and whether it is **node-graph based**.
2. The **diffuse/albedo** colour parameter's description name or ID.
3. The **emission** colour + power parameter names or IDs (searchlight).
4. The exact **Python API** path for the above on the target Octane version.

Run **Octane Diagnostics** to capture all of the above from your environment.

## Hard caveats (please read)

- **No Octane dependency is required** for the core plugin.
- **No guarantee of full physical relativistic ray tracing inside Octane.** The
  relativistic look is and will remain an **approximation** delivered through
  materials and geometry. A truly correct image needs per-ray relativistic
  treatment that a stock path tracer does not provide.
- **OSL camera support is experimental future work** (Phase D) and may not be
  feasible on all Octane/Cinema 4D versions. The object/camera *OSL* toggles are
  placeholders only.

## Planned phases

Each phase is additive and stays behind the adapter; the core never imports
Octane directly.

### Phase A - Scene / material preparation (renderer-agnostic)
Ensure the relativistic results are expressed in a form any renderer can consume:
the existing previews already do this (generated Standard materials, contracted
geometry copies). This phase formalizes a clean, bake-friendly scene state that
Octane can pick up unchanged.

### Phase B - Octane material / node adapter (native attempt + fallback)
`octane/material_adapter.py` maps the per-object Doppler colour and searchlight
intensity onto a **native Octane material** (diffuse/emission colour and power),
mirroring the Standard preview, using runtime description introspection with a
read-back probe. **Working with caveats**: the adapter and the *Apply
Octane-Compatible Material Preview* command exist; the native path is attempted
when feasible and otherwise falls back safely to the Standard material (see
"Tested behavior" above - the native path is unverified outside Cinema 4D and
degrades cleanly on node-based materials). Driven through
`adapter.apply_octane_or_fallback_material(doc, obj, color, intensity)`.

### Phase C - AOV / render pass setup (scaffolding started)
`octane/aov_adapter.py` exposes relativistic quantities (Doppler factor, beta,
searchlight, object velocity, relativity mask) as Octane **AOVs/passes** for
compositing. **Scaffolding done:** the desired-AOV data model, the *Show AOV
Plan* command, and best-effort render-settings detection exist; automatic AOV
creation is honestly reported as **not supported** (manual setup for now). Full
workflow and the TODO list are in [`AOV_PIPELINE.md`](AOV_PIPELINE.md).

### Phase D - Optional OSL camera shader generation (Phase 3, experimental)
Investigate generating an **OSL camera** that bends/retimes rays for true
apparent-position effects. Clearly experimental, version-dependent, and **not
promised**. **Started:** `octane/osl_camera.py` generates a clearly-marked
placeholder shader and the *Export Experimental OSL Camera* command writes it to
a user-chosen file (committed reference:
`examples/osl/relativity_camera_experimental.osl`). It is **not wired into
Octane** - the Octane OSL-camera ray I/O binding is unverified. Full notes in
[`OSL_CAMERA_EXPERIMENTS.md`](OSL_CAMERA_EXPERIMENTS.md).

### Phase E - External renderer bridge
For pipelines that render Octane outside the C4D UI, define a bridge that exports
the prepared scene/material state to an external Octane process. Speculative;
lowest priority.

## Architecture & isolation

```
plugin code  ──▶  octane/adapter.py  ──▶  octane/detection.py        (safe checks + plugin scan)
(never imports        (facade)            octane/diagnostics.py       (read-only ID/param report)
 an Octane module)                        octane/material_adapter.py  (Phase B native attempt + fallback)
                                          octane/camera_adapter.py    (Phase D stub)
                                          octane/aov_adapter.py       (Phase C scaffold)
                                          octane/osl_camera.py        (Phase D experimental)
```

Only modules inside `octane/` may import an Octane module, always guarded. See
[`ARCHITECTURE.md`](ARCHITECTURE.md) §6 and the roadmap
([`ROADMAP.md`](ROADMAP.md), Phase 3) for where this sits in the overall plan.

## For developers

`detection.py`, `diagnostics.py`, and `material_adapter.py` are all import-safe
(no top-level `import c4d`) and unit-tested in plain Python
(`tests/test_octane_detection.py`, `tests/test_octane_diagnostics.py`,
`tests/test_octane_material.py`) to guarantee the "works without Octane" promise;
the suite is run by `tools/verify_repo.py`. The adapter facade
(`octane/adapter.py`: `is_available()`, `status_report(doc)`,
`apply_doppler_to_material(...)`, `sync_camera(...)`) is the only surface the rest
of the plugin should call.
