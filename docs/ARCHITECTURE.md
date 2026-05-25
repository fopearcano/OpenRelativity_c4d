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

> **Logical layers → packages.** The names used below map to the implemented
> package as follows: the `relativity_core` layer is `openrelativity_c4d.core`;
> the `c4d_plugin` layer is `openrelativity_c4d.c4d`; the `adapters/octane` layer
> is `openrelativity_c4d.octane`. The package root (`openrelativity_c4d/`) also
> holds `constants`, `ids`, `logging_utils`, and `bootstrap`; the Cinema 4D entry
> point is the top-level `openrelativity_c4d.pyp`. (`import c4d` inside the
> `openrelativity_c4d.c4d` sub-package resolves to Cinema 4D's module, not the
> sub-package — Python 3 absolute import.)

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

## 3. `relativity_core` (`openrelativity_c4d.core`) — the portable physics layer

**Role.** This is the renderer-agnostic math core: every relativistic quantity
the plugin needs is computed here and nowhere else. The Cinema 4D layer and the
Octane adapter are thin consumers that feed it numbers (speeds, directions,
colors) and apply what comes back to scene geometry and materials. Keeping the
math here — with no `c4d`, no Octane, and no third-party imports — is what makes
it testable in plain Python and migratable to C++ behind the same signatures.

**Prototype, not physics-grade.** The functions are *approximate, stable, and
art-directable* by design (this is a visualization prototype, not a spectral
renderer). Two conventions hold throughout:

- **`beta = v/c` is a clamped magnitude** in `[0, MAX_BETA]` (`MAX_BETA = 0.999`).
  Reaching/exceeding `c` clamps rather than raising, so geometry/color never blow
  up. Direction is carried by `cos_theta`, not by the sign of `beta`.
- **`cos_theta = +1` means approaching, `-1` means receding** (used by both
  `doppler` and `searchlight`). `strength` parameters in `[0, 1]` blend an effect
  from off (`0`, identity) to full (`1`).

| Module | Responsibility | Representative API |
|---|---|---|
| `relativity_math` | Clamping, Lorentz factor, contraction scale | `clamp_beta`, `beta_from_speed(speed, c)`, `gamma_from_beta`, `inverse_gamma_from_beta`, `lorentz_contraction_scale(beta, strength)`, `clamp`/`clamp01` |
| `doppler` | Doppler factor + art-directable recolor | `doppler_factor(beta, cos_theta)`, `approximate_rgb_doppler_shift(rgb, factor, strength)`, `is_blueshift`, `is_redshift` |
| `searchlight` | Beaming / searchlight intensity (clamped) | `searchlight_intensity_multiplier(beta, cos_theta, strength)` |
| `transforms` | Safe vector helpers, 3D velocity addition, apparent position | `safe_normalize`, `dot`/`add`/`sub`/`scale`/`length`, `add_velocity(v, u, c)`, `apparent_position` |

> A `spectrum` module (RGB↔XYZ + wavelength-shift recolor) is planned for a later
> phase; for now `approximate_rgb_doppler_shift` is a simple red/blue tint, not a
> spectral transform. Tests live in `openrelativity_c4d/tests/test_core_math.py`.

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
`openrelativity_c4d/c4d/descriptions/` (`.res` descriptions + localized `.str`
strings).

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
openrelativity_c4d.pyp        # Cinema 4D entry point; calls bootstrap.register()
openrelativity_c4d/           # importable package (safe to import outside C4D)
  __init__.py                 # metadata + is_c4d_available(); no `import c4d`
  constants.py                # version / target / status metadata
  ids.py                      # PLACEHOLDER plugin IDs (replace before release)
  logging_utils.py            # stdlib-only logging helpers
  bootstrap.py                # register() — lazy c4d import, guarded

  core/                       # pure Python; no `import c4d`; future C++ target
    relativity_math.py        # gamma, inverse gamma, contraction, dilation, vel-add
    doppler.py                # relativistic Doppler shift factor
    searchlight.py            # beaming / searchlight intensity factor
    transforms.py             # vectors, 3D velocity add, apparent position

  c4d/                        # imports c4d; thin glue
    plugin_register.py        # registers plugin elements (About now; more later)
    commands.py               # About command + dialog (functional)
    scene_controller.py       # placeholder — global c / observer velocity / time
    camera_tools.py           # placeholder — observer frame (TagData)
    object_tools.py           # placeholder — per-object velocity & flags (TagData)
    descriptions/             # .res descriptions + localized strings (later)

  octane/                     # optional, soft-imported; stubs in Phase 1
    detection.py              # never-raising Octane detection
    adapter.py                # stable facade used by the rest of the plugin
    camera_adapter.py         # placeholder (Phase 3)
    material_adapter.py       # placeholder (Phase 3)
    aov_adapter.py            # placeholder (Phase 3)

  tests/
    test_core_math.py         # pure-Python unit tests for core/ (no Cinema 4D)

docs/                          # charter, architecture, roadmap, upstream reference
tools/
  run_core_tests.py            # run the core tests without Cinema 4D
```

In Phase 1 the `core/` modules, the About `command`, the Octane `detection`, and
the package plumbing are implemented; `scene_controller`, `camera_tools`,
`object_tools`, the Octane mapping adapters, and `descriptions/` are placeholders.
