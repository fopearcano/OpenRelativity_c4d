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

> **Status: Phase 0 — documentation & structure only.**
> This commit contains documentation and a proposed project layout. There is
> **no plugin code yet**. See [`docs/ROADMAP.md`](docs/ROADMAP.md).

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

## What this prototype will provide

- **Relativity Scene Controller** — owns the global relativistic state
  (speed of light `c`, the observer's velocity, simulation time / time-dilation
  mode) and distributes it to the rest of the scene.
- **Relativistic Camera Tag** — the observer's frame: velocity (with
  relativistic velocity addition), and the camera parameters the math needs.
- **Relativistic Object Tag** — per-object world velocity and the flags that
  drive its deformation, color adjustment, and causal visibility.
- **`relativity_core`** — a dependency-free Python math library: Lorentz factor,
  length contraction, velocity addition, relativistic Doppler & searchlight
  factors, RGB↔spectrum helpers, and the apparent-position (retarded-time)
  solve. **Never imports `c4d`.**
- **Lorentz deformation / bake utility** — moves real mesh points to show
  length contraction and apparent distortion (since we can't bind a live
  viewport vertex shader the way Unity does).
- **Approximate Doppler / searchlight material adjustment** — per-object color
  and luminance shifts on standard C4D materials.
- **Octane-aware adapter (optional, isolated)** — soft-detects Octane and, when
  present, mirrors the color/intensity results onto Octane material nodes. The
  core plugin imports and runs **without Octane installed**.
- **Docs & test scaffolding** — unit tests for `relativity_core` that run with
  plain Python, no Cinema 4D required.

## What is explicitly out of scope (Phase 1)

- A custom renderer or full physical relativistic ray tracing.
- Per-pixel relativistic Doppler in the live C4D viewport.
- Real-time, interactive first-person controls.
- Relativistic lighting/shadows/reflections, general relativity, gravity.
- Requiring Octane, or Octane-accurate relativistic shading.

See [`docs/PROJECT_CHARTER.md`](docs/PROJECT_CHARTER.md) for the full
in-scope / out-of-scope lists.

## Proposed repository layout

```
OpenRelativity_c4d/
├── README.md
├── MITLicense.md                  # upstream MIT license (attribution)
├── docs/
│   ├── PROJECT_CHARTER.md         # why, goals, scope
│   ├── ARCHITECTURE.md            # layering, data flow, C4D plugin design, C++ path
│   ├── ROADMAP.md                 # phased delivery plan
│   └── ORIGINAL_OPENRELATIVITY_REFERENCE.md   # upstream analysis + concept mapping
├── src/
│   ├── relativity_core/           # PURE PYTHON physics/math — no `import c4d`
│   ├── c4d_plugin/                # C4D-facing plugins (Scene Controller, Tags, Deformer)
│   │   └── res/                   # C4D resource/description files
│   └── adapters/
│       └── octane/                # optional, soft-imported Octane adapter (stubs)
├── tests/                         # pure-Python unit tests for relativity_core
└── examples/                      # sample scenes & usage notes (later phases)
```

The directory tree in this commit is a scaffold: each folder contains a short
`README.md` describing its intent, and **no plugin logic yet**.

## Requirements (target)

- **Cinema 4D 2023 or newer**, using its bundled Python 3 runtime.
- **No external Python packages** for the core (standard library + the `c4d`
  module only). Octane support is optional and isolated.

## Attribution & license

This project is conceptually inspired by **MIT Game Lab — OpenRelativity**
(© 2013 Massachusetts Institute of Technology, MIT License). The upstream
license is preserved in [`MITLicense.md`](MITLicense.md). The original Unity/C#
source is **not** included here; this is an independent Cinema 4D-native work.
Licensing for this repository is to be confirmed by the maintainer; the MIT
License is the natural default given the lineage.
