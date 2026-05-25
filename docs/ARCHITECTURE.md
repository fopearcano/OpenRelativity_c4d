# Architecture — OpenRelativity for Cinema 4D

This document describes *how* the prototype is structured. For *why*, see
[`PROJECT_CHARTER.md`](PROJECT_CHARTER.md); for *when*, see
[`ROADMAP.md`](ROADMAP.md); for the upstream concept mapping, see
[`ORIGINAL_OPENRELATIVITY_REFERENCE.md`](ORIGINAL_OPENRELATIVITY_REFERENCE.md).

## 1. Guiding principles

1. **Separate the science from the host.** All physics/math lives in a pure
   Python package, `relativity_core`, that **never imports `c4d`**. It could run
   in a plain Python interpreter, a unit test, a web service, or — eventually —
   be reimplemented in C++ behind the same interface.
2. **Keep Cinema 4D code thin.** The `c4d_plugin` layer is glue: it reads scene
   state, calls `relativity_core`, and writes results back to objects and
   materials. It contains as little arithmetic as possible.
3. **Isolate Octane completely.** Nothing outside `adapters/octane` may
   `import` an Octane module. The adapter is soft-loaded; its absence is normal.
4. **Prefer real data over magic.** Because we cannot bind a live viewport
   shader, geometric effects are applied to **actual mesh points**, and color
   effects to **actual material parameters**. What you see is what will render.
5. **No required third-party dependencies.** Standard library + `c4d` only.

## 2. Layered structure

```
            ┌─────────────────────────────────────────────┐
            │                 Cinema 4D host               │
            │   (scene, objects, materials, timeline)      │
            └───────────────▲───────────────┬──────────────┘
                            │ reads/writes   │ optional
                            │                ▼
   ┌────────────────────────┴───────┐   ┌─────────────────────────┐
   │           c4d_plugin            │   │     adapters/octane      │
   │  Scene Controller (SceneHook/   │──▶│  soft import, capability │
   │     CommandData)                │   │  detection, node mapping │
   │  Relativistic Camera Tag        │   │  (stubs in Phase 1)      │
   │  Relativistic Object Tag        │   └─────────────────────────┘
   │  Lorentz Deformer / bake util   │
   │  Doppler material adjustment    │
   └────────────────────────┬────────┘
                            │ calls (numbers in, numbers out)
                            ▼
   ┌────────────────────────────────────────────────────────────┐
   │                       relativity_core                        │
   │  constants · lorentz · velocity · doppler · spectrum ·       │
   │  aberration                (PURE PYTHON, no `import c4d`)     │
   └────────────────────────────────────────────────────────────┘
```

**Import rules (enforced by convention and review):**

| Layer | May import | May **not** import |
|---|---|---|
| `relativity_core` | Python stdlib | `c4d`, Octane, anything host-specific |
| `c4d_plugin` | `c4d`, `relativity_core`, `adapters.octane` (soft) | Octane modules directly |
| `adapters/octane` | `c4d`, Octane modules (soft), `relativity_core` | — |
| `tests` | `relativity_core`, stdlib | `c4d` (tests must run without Cinema 4D) |

## 3. `relativity_core` — the portable physics layer

A small set of dependency-free modules. All functions take and return plain
numbers / tuples / lists so the API is trivially portable to C++.

| Module | Responsibility | Representative concepts |
|---|---|---|
| `constants` | Shared constants & defaults | default `c`, small-epsilon guards |
| `lorentz` | Time dilation & length contraction | `gamma(beta)`, `inv_gamma(beta)`, `contract_length(L0, beta)` |
| `velocity` | Relativistic velocity addition | `add_velocity(v, u, c)` (parallel + perpendicular split) |
| `doppler` | Doppler & beaming factors | `doppler_shift(beta_rel, cos_theta)`, `searchlight_intensity(shift)` |
| `spectrum` | Color ↔ spectrum helpers | `rgb_to_xyz`, `xyz_to_rgb`, approximate wavelength-shift recolor |
| `aberration` | Apparent position via light travel time | retarded-time quadratic solve → apparent offset |

### 3.1 Physical relationships (reference, as realized in upstream)

These are the relationships the modules encode; the upstream Unity expressions
are cited in
[`ORIGINAL_OPENRELATIVITY_REFERENCE.md`](ORIGINAL_OPENRELATIVITY_REFERENCE.md).

- **Lorentz factor:** `gamma = 1 / sqrt(1 - (v/c)^2)`. Upstream caches the
  reciprocal `sqrt(1 - v^2/c^2)`.
- **Length contraction:** lengths along the motion scale by `1/gamma`.
- **Velocity addition:** `v_new = (v + u_parallel + u_perp/gamma) / (1 + v·u/c^2)`.
- **Relativistic Doppler factor:**
  `shift = (1 - (v/c)·cosθ) / sqrt(1 - (v/c)^2)`, where `θ` is the angle between
  the relative velocity and the line of sight. `shift > 1` ⇒ redshift
  (receding); `shift < 1` ⇒ blueshift (approaching).
- **Searchlight / beaming:** observed intensity scales by roughly
  `(1/shift)^3` (the exponent applied to the tristimulus values upstream).
- **Apparent position (aberration / Terrell rotation):** solve
  `a·t² + b·t + c = 0` with `a = c² - |v|²`, `b = -2(r·v)`, `c = -|r|²`, for the
  light-travel-time `t`, then offset the point by `v·t` and apply contraction
  along the motion. This is what makes fast objects look rotated rather than
  merely squashed.

> The Doppler/spectrum path is an **approximation** (a few Gaussian color
> primaries plus IR/UV channels, as upstream does), not a spectrally accurate
> renderer. This is a deliberate scope choice.

## 4. `c4d_plugin` — the Cinema 4D integration layer

### 4.1 Component mapping to Cinema 4D plugin types

Cinema 4D does not have Unity's `MonoBehaviour`. The natural C4D types are:

| This project | C4D plugin base | Why |
|---|---|---|
| **Relativity Scene Controller** | `SceneHookData` and/or `CommandData` | Scene-global state and a place to run per-scene updates; a command can create/sync it. |
| **Relativistic Camera Tag** | `TagData` on a camera object | Per-camera data (observer velocity) and an update hook. |
| **Relativistic Object Tag** | `TagData` on scene objects | Per-object velocity, visibility, and deformation flags. |
| **Lorentz Deformer / bake** | `ObjectData` (deformer) and/or a `CommandData` bake tool | Move real points; a deformer for live preview, a bake for permanence/Octane. |
| **Doppler material adjustment** | logic invoked from the tags/controller | Writes standard material color/luminance; mirrored to Octane via the adapter. |

Parameters and labels are described with C4D **resource files** under
`src/c4d_plugin/res/` (`.res` descriptions + localized `.str` strings).

### 4.2 Why geometry is deformed (not shaded)

OpenRelativity computes apparent vertex positions **in the camera's vertex
shader every frame**. Cinema 4D's Python API has no equivalent live
per-vertex viewport program, and writing a renderer is out of scope. We
therefore realize the geometric transform by **modifying mesh points** — either
live in a deformer's `ModifyObject`, or baked into a cached copy of the mesh for
rendering. Consequences:

- The transform depends on the observer ⇒ the deformer/bake reads the Scene
  Controller + Camera Tag state.
- Smoothness depends on tessellation ⇒ an optional **mesh density / subdivision**
  utility (the analogue of upstream `ObjectMeshDensity`) can pre-subdivide large
  faces.
- Because we move real points, frustum-culling concerns from the GPU approach
  (upstream inflates mesh bounds to defeat culling) become a non-issue for the
  baked workflow.

### 4.3 Why color is a material approximation

OpenRelativity's Doppler/searchlight is **per-pixel** in a fragment shader. With
no live fragment hook and no custom renderer, Phase 1 computes a **per-object**
(uniform) Doppler factor from the object's relative velocity and an
average line-of-sight, then adjusts the material's base color and luminance
accordingly. This is coarser than per-pixel but renders correctly in both the
standard renderer and Octane. Finer (per-point / per-UV) approximations are a
later-phase option (see [`ROADMAP.md`](ROADMAP.md)).

## 5. Data flow (per evaluation)

```
Relativity Scene Controller
   ├─ c (speed of light), simulation time, time-dilation mode
   │
   ├──▶ Relativistic Camera Tag ──▶ observer velocity (relativistic addition),
   │                                 FOV / aspect for line-of-sight math
   │
   └──▶ Relativistic Object Tag(s) ──▶ object world velocity, visibility window
                 │
                 ▼
         relativity_core
           gamma · contraction · doppler · searchlight · apparent position
                 │
        ┌────────┴─────────┐
        ▼                  ▼
  Lorentz Deformer   Doppler material adjustment
  (moves points)     (color + luminance)
        │                  │
        ▼                  ▼
     C4D mesh         C4D material ──▶ adapters/octane (optional) ──▶ Octane nodes
```

## 6. `adapters/octane` — optional integration

- **Soft detection.** The adapter attempts to import the Octane integration
  (e.g. its Python module / known plugin IDs) inside a `try/except`. If it is
  not present, the adapter reports "unavailable" and every operation is a no-op.
  Nothing else in the codebase imports Octane.
- **Stable interface.** The rest of the plugin talks to a small adapter API
  (e.g. `is_available()`, `apply_doppler(material, color, intensity)`), never to
  Octane directly. This keeps Octane swappable and keeps the core importable.
- **Phase 1 = stubs.** The interface exists and is exercised by the
  Doppler material adjustment, but the Octane-specific mapping is a stub. Real
  node mapping arrives in a later phase (see [`ROADMAP.md`](ROADMAP.md)).

## 7. Path to C++

Migration is intended to be incremental and low-risk because of the layering:

1. `relativity_core` has a **numeric, dependency-free API** (numbers/arrays in,
   numbers/arrays out, no Python-only idioms in the contract). It can be
   reimplemented in C++ and exposed to the existing Python plugin (or replaced
   wholesale) behind the same function signatures.
2. The `c4d_plugin` classes map 1:1 onto the **Cinema 4D C++ SDK** equivalents
   (`TagData`, `ObjectData`, `SceneHookData`, `CommandData`), so the plugin shell
   can be re-authored in C++ without rethinking the design.
3. Resource files (`res/`) are already in the C++-SDK-compatible format.
4. The Octane adapter boundary stays the same; only its implementation language
   changes.

To preserve this path, `relativity_core` avoids returning rich Python objects
across its public boundary and avoids any dependency that has no C++ analogue.

## 8. Dependency policy

- **Runtime:** Cinema 4D's bundled Python 3 and the `c4d` module only. The math
  core uses just the standard library (`math`). We **do not require `numpy`** —
  it may not be present in every C4D install, and avoiding it keeps the core
  portable and C++-friendly.
- **Development/testing:** a test runner (e.g. `pytest`) may be used for
  `relativity_core`, but tests must also be runnable with `python -m unittest`
  so no dependency is mandatory.

## 9. Directory structure (detailed)

```
src/
  relativity_core/        # pure Python; no `import c4d`; future C++ target
    constants            # default c, epsilons
    lorentz              # gamma, inverse gamma, length contraction
    velocity             # relativistic velocity addition
    doppler              # Doppler factor, searchlight/beaming factor
    spectrum             # RGB<->XYZ, approximate wavelength-shift recolor
    aberration           # retarded-time apparent-position solve

  c4d_plugin/             # imports c4d; thin glue
    scene_controller     # global c / observer velocity / time  (SceneHook+Command)
    camera_tag           # observer frame (TagData on camera)
    object_tag           # per-object velocity & flags (TagData)
    lorentz_deformer     # geometry transform (ObjectData deformer + bake command)
    doppler_material     # per-object color/luminance adjustment
    res/                 # .res descriptions + localized strings

  adapters/
    octane/              # optional, soft-imported; stubs in Phase 1

tests/                    # pure-Python unit tests for relativity_core
examples/                 # sample scenes & usage notes (later phases)
```

In the current commit these directories are **scaffolds**: each holds a short
`README.md` describing its intent and **no plugin logic**.
