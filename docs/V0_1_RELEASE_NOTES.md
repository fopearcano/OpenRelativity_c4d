# v0.1 Release Notes

**v0.1 prototype — C4D-native relativistic visualization scaffold with
Octane-ready adapter architecture.**

An independent, unofficial Cinema 4D 2023+ Python plugin for **artist-facing,
approximate** special-relativistic visualization. Inspired by the MIT Game Lab's
OpenRelativity; **not affiliated** with MIT, OTOY (Octane), or Maxon (see the
[README disclaimer](../README.md#disclaimer-not-affiliated)). **No physical
correctness is claimed**, and this is **not** a full Octane integration.

## What v0.1 is

A working scaffold and front-end you can install and drive end-to-end:

- **Pure-Python physics core** (`openrelativity_c4d.core`) — Lorentz factor /
  contraction, relativistic velocity addition, an approximate Doppler factor, a
  searchlight (beaming) multiplier, and retarded-time / direction helpers.
  Dependency-free and unit-tested **without Cinema 4D**.
- **Scene controls** — *Create Relativity Controller*, *Setup Relativistic
  Camera*, *Setup Selected Relativistic Objects* / *Select Relativistic Objects*,
  using organized **User Data** (no resource files needed yet).
- **Material previews** (Standard/Physical) — *Apply Doppler Material Preview*,
  *Apply Searchlight Preview*, *Apply Relativity Material Preview*, *Clear
  Material Preview*. One shared `ORC_Preview_<name>` material per object, applied
  **non-destructively** (a layered Texture tag).
- **Lorentz geometry preview** — *Create / Remove Lorentz Preview Copies*:
  contracted, non-destructive duplicates; originals optionally hidden and
  restored.
- **One-click demo** — *Create Test Scene* (approaching/receding/lateral/static;
  safe to run repeatedly) and *Apply All Previews*.
- **Control Panel** — a compact dialog with a button per command and a live
  status read-out.
- **Octane adapter (scaffolding)** — *Octane Status*, *Apply Octane-Compatible
  Material Preview* (Standard fallback today), *Show AOV Plan* (manual), and
  *Export Experimental OSL Camera* (placeholder).
- **Metadata export** — *Export Relativity Metadata JSON* (documented schema).
- **Tooling** — `tools/verify_repo.py`, `tools/make_plugin_zip.py`,
  `tools/run_core_tests.py`.

## Install & try it

See [`INSTALLATION.md`](INSTALLATION.md) (copy into the C4D user `plugins` folder,
restart, open the Control Panel) and the 5-minute [`QUICKSTART.md`](QUICKSTART.md).
Full reference: [`USER_GUIDE.md`](USER_GUIDE.md).

## What is NOT in v0.1

- **Not** full ray-traced or physically-correct relativistic rendering.
- **Not** a full Octane integration — the Octane material/AOV/OSL paths are
  detection + **Standard-material fallback** + **manual** AOV plan + an
  **experimental** OSL placeholder. Octane is optional; the plugin runs without
  it. See [`OCTANE_INTEGRATION.md`](OCTANE_INTEGRATION.md).
- **Not** spectral Doppler (it is an approximate RGB tint), not radiometric
  searchlight, and the Lorentz preview is an axis-aligned scale, **not** Terrell
  rotation. No light-travel-time sampling in the previews.

Full list: [`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md).

## Known issues / caveats

- **Plugin IDs are development placeholders** (some past Maxon's test range) and
  **must be replaced** with registered Plugin Café IDs before public
  distribution.
- **No license is chosen yet** — see [`LICENSE_DECISION_NEEDED.md`](LICENSE_DECISION_NEEDED.md);
  add a `LICENSE` before release.
- The Cinema 4D-side behaviour is **manual-tested** (see
  [`TEST_PLAN_C4D.md`](TEST_PLAN_C4D.md) and [`TEST_PLAN_OCTANE.md`](TEST_PLAN_OCTANE.md));
  only the pure math and import-safe helpers are unit-tested. Not validated across
  every C4D/Octane version.

## Verifying this build

From the repository root, with a plain Python 3 (no Cinema 4D):

```
python tools/verify_repo.py        # files / no-c4d-in-core / pure tests / docs / entrypoint
python tools/make_plugin_zip.py    # build build/OpenRelativity_c4d_v0.1.0.zip
```

## Next steps

Prioritized in [`TODO.md`](../TODO.md): registered plugin IDs, real
`TagData`/`ObjectData` plugins, better velocity-direction handling, better
material restoration, native Octane node-graph materials, AOV automation, OSL
camera research, and a C++ migration plan. Plan: [`ROADMAP.md`](ROADMAP.md);
history: [`../CHANGELOG.md`](../CHANGELOG.md).
