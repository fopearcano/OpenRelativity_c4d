# Octane Integration

How OpenRelativity_c4d relates to **Octane for Cinema 4D** - today (detection
only) and the planned phases.

> **Core guarantee.** The plugin has **no dependency on Octane**. It imports and
> runs fully with Octane absent; nothing here is required for the controller,
> camera, objects, or the Standard/Physical previews. All Octane code is isolated
> in the `openrelativity_c4d/octane/` package and is reached only through the
> adapter facade - the rest of the plugin never imports an Octane module.

## What exists today: detection & status only

There is **no Octane modification** yet. The plugin can only *detect* Octane and
report status.

- **Extensions > “OpenRelativity C4D: Octane Status”** opens a dialog with the
  current report.
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

The active-renderer check identifies Octane by the active engine's **plugin
name** (again ID-independent), falling back to `unknown` when it cannot be
determined.

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

### Phase B - Octane material / node adapter
`octane/material_adapter.py` maps the per-object Doppler colour and searchlight
intensity onto **Octane material nodes** (e.g. diffuse/emission colour and power)
when Octane is present, mirroring what the Standard preview does. Driven through
`adapter.apply_doppler_to_material(...)`; a no-op stub today.

### Phase C - AOV / render pass setup
`octane/aov_adapter.py` optionally exposes relativistic quantities (e.g. the
per-object Doppler shift or beaming factor) as Octane **AOVs/passes** for
compositing. Stub today.

### Phase D - Optional OSL camera shader generation (experimental)
Investigate generating an **OSL camera** that bends/retimes rays for true
apparent-position effects. Clearly experimental, version-dependent, and **not
promised**; `octane/camera_adapter.py` is the intended home.

### Phase E - External renderer bridge
For pipelines that render Octane outside the C4D UI, define a bridge that exports
the prepared scene/material state to an external Octane process. Speculative;
lowest priority.

## Architecture & isolation

```
plugin code  ──▶  octane/adapter.py  ──▶  octane/detection.py        (safe checks)
(never imports        (facade)            octane/material_adapter.py  (Phase B stub)
 an Octane module)                        octane/camera_adapter.py    (Phase D stub)
                                          octane/aov_adapter.py       (Phase C stub)
```

Only modules inside `octane/` may import an Octane module, always guarded. See
[`ARCHITECTURE.md`](ARCHITECTURE.md) §6 and the roadmap
([`ROADMAP.md`](ROADMAP.md), Phase 3) for where this sits in the overall plan.

## For developers

`detection.py` is import-safe (no top-level `import c4d`) and unit-tested in plain
Python (`openrelativity_c4d/tests/test_octane_detection.py`) to guarantee the
"works without Octane" promise. The adapter facade
(`octane/adapter.py`: `is_available()`, `status_report(doc)`,
`apply_doppler_to_material(...)`, `sync_camera(...)`) is the only surface the rest
of the plugin should call.
