# OpenRelativity for Cinema 4D (`OpenRelativity_c4d`)

A **Cinema 4D 2023+ native** prototype for **artist-facing relativistic
visualization** — simulating how objects look when they (or the observer) move
at an appreciable fraction of the speed of light: length contraction, the
relativistic Doppler color shift, the searchlight (beaming) effect, and the
apparent geometric distortion caused by light travel time.

This project is **inspired by** the MIT Game Lab's
[OpenRelativity](https://github.com/MITGameLab/OpenRelativity) (Unity/C#), but
it is **not a port**. It re-expresses the *physics ideas* of OpenRelativity in
terms that fit a Digital Content Creation (DCC) application and an offline,
physically-based renderer (Octane), rather than a real-time game engine. See
[`docs/PROJECT_CHARTER.md`](docs/PROJECT_CHARTER.md) for the rationale and
[`docs/ORIGINAL_OPENRELATIVITY_REFERENCE.md`](docs/ORIGINAL_OPENRELATIVITY_REFERENCE.md)
for the concept-by-concept mapping.

> **Status: Phase 1 — in progress.**
> The plugin loads in Cinema 4D 2023+ and registers *Extensions* commands to set
> up the relativity **controller**, an observer **camera**, and per-**object**
> settings (plus an **About** dialog). All three carry organized User Data; the
> pure-Python physics core (`openrelativity_c4d.core`) is implemented and
> unit-tested. The effects those settings drive (deformation, materials, Octane)
> are placeholders for later phases. See [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md)
> to get started and [`docs/ROADMAP.md`](docs/ROADMAP.md) for the plan.

---

## Why not just port the Unity project?

| | OpenRelativity (Unity) | OpenRelativity_c4d (this project) |
|---|---|---|
| Host | Real-time game engine | Cinema 4D — a scene-authoring & offline-rendering DCC |
| Interaction | First-person WASD/mouse "player" | Camera object + tags + animation timeline |
| Relativistic visuals | Live GPU vertex + fragment shaders | Geometry deformation/bake + approximate material adjustments |
| Renderer | Unity's built-in pipeline | C4D Standard/Physical now; **Octane** later (optional) |
| Extension model | `MonoBehaviour` components | C4D `TagData` / `ObjectData` / `SceneHook` plugins |
| Language | C# + CG/HLSL shaders | Python first, architected for later C++ migration |

Cinema 4D has no equivalent of Unity's per-frame camera-bound vertex/fragment
shader that OpenRelativity relies on for *all* of its visuals. So instead of
copying that architecture, we split the problem into a portable **physics core**
and a thin **C4D integration layer**, and we realize the visuals as real
geometry changes plus material-parameter approximations. Full details in
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Features

Implemented now (Phase 1):

- **`openrelativity_c4d.core`** — a dependency-free Python math library: Lorentz
  factor, length contraction, time dilation, relativistic velocity addition,
  relativistic Doppler & searchlight factors, and the apparent-position
  (retarded-time) solve. **Never imports `c4d`**; covered by unit tests that run
  in plain Python.
- **About command** — registers under *Extensions* and opens a minimal dialog
  showing the plugin version, target/running Cinema 4D version, Octane
  detection, whether a Relativity Controller exists, and status.
- **Relativity Controller** — *Extensions > Create Relativity Controller* adds an
  `ORC_Relativity_Controller` Null with organized User Data (speed of light,
  global beta, effect strengths, preview mode, Octane/bake toggles) and clean
  read/write helpers. Stores settings now; drives effects in later phases. See
  [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md).
- **Relativistic Camera** — *Extensions > Setup Relativistic Camera* configures
  the selected camera (or creates `ORC_Relativistic_Camera`) with observer beta,
  velocity, preview toggles, and Octane/OSL placeholders, plus a
  `compute_observer_beta` helper that resolves `beta` from the camera and
  controller.
- **Relativistic Objects** — *Extensions > Setup Selected Relativistic Objects*
  adds per-object User Data (object beta, velocity X/Y/Z, preview toggles, bake /
  Octane flags) to the selection (skipping the controller and cameras), and
  *Select Relativistic Objects* re-selects them all.
- **Material previews (first visible effects)** — Doppler colour shift
  (blue/red) and searchlight beaming (brighter/dimmer + emission), via *Apply
  Doppler Material Preview*, *Apply Searchlight Preview*, and the combined *Apply
  Relativity Material Preview*; *Clear Material Preview* removes them. One shared
  generated Standard material per object, applied non-destructively
  (Standard/Physical compatible, Octane not required). Artistic approximations,
  not spectral — see [`docs/DOPPLER_PREVIEW.md`](docs/DOPPLER_PREVIEW.md) and
  [`docs/SEARCHLIGHT_PREVIEW.md`](docs/SEARCHLIGHT_PREVIEW.md).
- **Lorentz geometry preview** — *Create Lorentz Preview Copies* makes a
  non-destructive contracted duplicate (`ORC_LorentzPreview_<name>`) of each
  object, scaled along its velocity axis, and hides the original (restored by
  *Remove Lorentz Preview Copies*). Axis-aligned length contraction only — no
  Terrell rotation yet. See [`docs/LORENTZ_PREVIEW.md`](docs/LORENTZ_PREVIEW.md).
- **Octane adapter (optional, isolated)** — soft-detects Octane; the plugin
  imports and runs **without Octane installed**. Mapping is stubbed.

Planned (later phases — see [`docs/ROADMAP.md`](docs/ROADMAP.md)):

- **Terrell rotation / true apparent geometry** and a **point-level bake**.
- **Real Octane material/camera/AOV mapping.**

## What is explicitly out of scope (Phase 1)

- A custom renderer or full physical relativistic ray tracing.
- Per-pixel relativistic Doppler in the live C4D viewport.
- Real-time, interactive first-person controls.
- Relativistic lighting/shadows/reflections, general relativity, gravity.
- Requiring Octane, or Octane-accurate relativistic shading.

See [`docs/PROJECT_CHARTER.md`](docs/PROJECT_CHARTER.md) for the full
in-scope / out-of-scope lists.

## Repository layout

```
OpenRelativity_c4d/
├── openrelativity_c4d.pyp          # Cinema 4D plugin entry point (loads the package)
├── openrelativity_c4d/             # the importable plugin package
│   ├── __init__.py                 # safe to import outside C4D (no `import c4d`)
│   ├── constants.py                # version, target, status metadata
│   ├── ids.py                      # PLACEHOLDER plugin IDs (replace before release)
│   ├── logging_utils.py            # stdlib-only logging helpers
│   ├── bootstrap.py                # register() entry called by the .pyp
│   ├── core/                       # PURE PYTHON physics/math — never imports c4d
│   │   ├── relativity_math.py      # gamma, contraction, time dilation, velocity add
│   │   ├── doppler.py              # relativistic Doppler shift factor
│   │   ├── searchlight.py          # beaming / searchlight intensity factor
│   │   └── transforms.py           # vectors, 3D velocity add, apparent position
│   ├── c4d/                        # Cinema 4D integration (imports c4d)
│   │   ├── plugin_register.py      # registers plugin elements
│   │   ├── commands.py             # About command + dialog (functional)
│   │   ├── scene_controller.py     # placeholder (later phase)
│   │   ├── camera_tools.py         # placeholder (later phase)
│   │   ├── object_tools.py         # placeholder (later phase)
│   │   └── descriptions/           # C4D resource files (later phases)
│   ├── octane/                     # optional, isolated Octane adapter (stubs)
│   │   ├── detection.py            # soft Octane detection (never raises)
│   │   ├── adapter.py              # stable facade used by the rest of the plugin
│   │   ├── camera_adapter.py       # placeholder (Phase 3)
│   │   ├── material_adapter.py     # placeholder (Phase 3)
│   │   └── aov_adapter.py          # placeholder (Phase 3)
│   └── tests/
│       └── test_core_math.py       # unit tests for core/ (no Cinema 4D)
├── docs/                           # charter, architecture, roadmap, upstream reference
├── tools/
│   └── run_core_tests.py           # run the core tests without Cinema 4D
└── MITLicense.md                   # upstream MIT license (attribution)
```

> `import c4d` inside `openrelativity_c4d/c4d/*` resolves to **Cinema 4D's**
> top-level module (Python 3 absolute import), not to the `openrelativity_c4d.c4d`
> sub-package.

## Requirements

- **Cinema 4D 2023 or newer**, using its bundled Python 3 runtime.
- **No external Python packages** (standard library + the `c4d` module only).
  Octane support is optional and isolated.

## Installation

1. **Locate your Cinema 4D user plugins folder.** In Cinema 4D, open
   *Edit > Preferences* and click **Open Preferences Folder…**; the `plugins`
   sub-folder there is your user plugins folder. (You can also point Cinema 4D at
   a custom plugins folder via the *Plugins* preferences.)
2. **Copy the plugin in.** Create a folder such as `OpenRelativity_c4d` inside
   that `plugins` folder and copy **both**:
   - `openrelativity_c4d.pyp`
   - the `openrelativity_c4d/` package folder

   into it, keeping them side by side:

   ```
   <C4D user folder>/plugins/OpenRelativity_c4d/
   ├── openrelativity_c4d.pyp
   └── openrelativity_c4d/   (the package)
   ```

   (Copying the whole repository works too; Cinema 4D only executes the `.pyp`.)
3. **Restart Cinema 4D.**
4. **Open the** *Extensions* **menu** and choose **“OpenRelativity C4D: About”**.
   A dialog reports the plugin version, the target and running Cinema 4D
   versions, whether Octane was detected, and the current status. If you don't
   see it, open the *Extensions > Console* and check for `[OpenRelativity C4D]`
   log lines.

> The bundled plugin IDs in `openrelativity_c4d/ids.py` are **development
> placeholders**. Obtain unique IDs from the Maxon Plugin Café and replace them
> before distributing the plugin.

## Development & tests

The physics core runs without Cinema 4D. From the repository root:

```
python -m unittest                       # discover & run all core tests
# or
python tools/run_core_tests.py           # same, with verbose output
```

The core (`openrelativity_c4d/core/`) must never `import c4d`; a unit test
enforces this so the math stays portable (and migratable to C++ later).

## Attribution & license

This project is conceptually inspired by **MIT Game Lab — OpenRelativity**
(© 2013 Massachusetts Institute of Technology, MIT License). The upstream
license is preserved in [`MITLicense.md`](MITLicense.md). The original Unity/C#
source is **not** included here; this is an independent Cinema 4D-native work.
Licensing for this repository is to be confirmed by the maintainer; the MIT
License is the natural default given the lineage.
