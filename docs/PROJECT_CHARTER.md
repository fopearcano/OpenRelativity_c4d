# Project Charter — OpenRelativity for Cinema 4D

## 1. Purpose

Build a **Cinema 4D 2023+ native** prototype that lets artists and educators
**visualize special-relativistic effects** on scenes they author in Cinema 4D,
and that is structured to grow toward **Octane** rendering and an eventual
**C++** implementation.

The effects we care about are the ones a fast-moving observer would actually
see:

- **Length (Lorentz) contraction** — objects shorten along their direction of
  relative motion.
- **Relativistic Doppler shift** — colors shift blue when approaching, red when
  receding; the visible spectrum slides so that infrared/ultraviolet content can
  move into view.
- **Searchlight / beaming effect** — apparent brightness increases in the
  direction of motion and decreases behind.
- **Apparent geometric distortion (relativistic aberration / Terrell–Penrose
  rotation)** — because light from different parts of an object reaches the
  observer at different times, a fast object looks *rotated/sheared*, not merely
  contracted.
- **Time dilation** — moving clocks (and animated processes) run slow relative
  to the observer.

## 2. Inspiration vs. independence — why this is NOT a Unity port

This project is **inspired by** the MIT Game Lab's
[OpenRelativity](https://github.com/MITGameLab/OpenRelativity), an excellent
Unity/C# toolkit. We deliberately **do not** copy its architecture, for reasons
that are fundamental rather than cosmetic:

1. **Different kind of application.** Unity is a real-time game engine; the
   artist *plays* a first-person simulation. Cinema 4D is a Digital Content
   Creation tool: the artist *composes* scenes and animations and then *renders*
   frames, usually offline. The whole interaction and timing model is different.

2. **Different rendering reality.** OpenRelativity does essentially *all* of its
   relativistic work inside a custom GPU shader (a CG/HLSL vertex + fragment
   program) bound to the camera every frame. Cinema 4D's Python API does not
   expose an equivalent "replace the camera's per-vertex/per-fragment program
   live in the viewport" hook, and one of our hard constraints is that we do
   **not** write a custom renderer. So the same architecture is simply not
   available to us — and copying it would be a dead end.

3. **Different extension model.** Unity attaches behavior via `MonoBehaviour`
   components with `Update()` callbacks. Cinema 4D extends via plugin classes —
   `TagData` (tags on objects), `ObjectData` (generators/deformers),
   `CommandData`/`SceneHookData` (scene-level tools). A faithful translation maps
   OpenRelativity's components onto *tags and deformers*, not onto a fictional
   C4D `MonoBehaviour`.

4. **Different target renderer.** We are aiming at **Octane**, a
   physically-based GPU path tracer, not Unity's rasterizer. Octane shades via
   its own node materials and camera model. Relativistic visuals therefore have
   to be expressed as (a) real geometry changes and (b) material-parameter
   approximations that Octane can consume — not as a bespoke rasterization
   shader.

5. **Different language/lifecycle goal.** OpenRelativity is C# + shaders. We
   start in **Python** for rapid iteration but keep the physics/math in a
   portable, dependency-free core so it can be **migrated to C++** (the Cinema 4D
   C++ SDK) later without rewriting the science.

The conclusion: we **keep the physics**, and **re-invent the plumbing** to fit
Cinema 4D. The concept-by-concept correspondence is documented in
[`ORIGINAL_OPENRELATIVITY_REFERENCE.md`](ORIGINAL_OPENRELATIVITY_REFERENCE.md).

## 3. What conceptually matters from OpenRelativity

These are the ideas worth carrying over (the *what*), independent of Unity's
*how*:

- A single **global relativistic state**: an adjustable speed of light `c`, the
  observer's velocity, and a clock — OpenRelativity's `GameState`.
- An **observer/camera** whose motion is combined with input using
  **relativistic velocity addition**, and which exposes field-of-view / aspect
  so screen-space directions can be turned into world directions —
  OpenRelativity's `MovementScripts`.
- **Per-object world velocity** plus the bookkeeping that decides when an object
  becomes visible (you cannot see an object's light before it was emitted) —
  OpenRelativity's `RelativisticObject`.
- The **two visual transforms**: a geometric one (length contraction + apparent
  position via light-travel-time) and a color one (Doppler shift + searchlight
  intensity + spectrum handling) — OpenRelativity's `relativity.shader`.
- The practical detail that **smooth geometric distortion needs enough
  vertices** — OpenRelativity's `ObjectMeshDensity`.

## 4. Cinema 4D-native equivalents (summary)

| OpenRelativity concept | Cinema 4D-native equivalent in this project |
|---|---|
| `GameState` (global brain) | **Relativity Scene Controller** (scene-level plugin holding `c`, observer velocity, time) |
| `MovementScripts` (observer) | **Relativistic Camera Tag** (velocity addition, camera params) |
| `RelativisticObject` (per object) | **Relativistic Object Tag** (per-object velocity, visibility, deformation flags) |
| Vertex shader (contraction + apparent position) | **Lorentz Deformer / bake utility** (moves real mesh points) |
| Fragment shader (Doppler + searchlight) | **Doppler/Searchlight material adjustment** (approximate, per-object) |
| `ObjectMeshDensity` | **Mesh density / subdivision utility** (optional pre-bake) |
| (math embedded in shader/scripts) | **`relativity_core`** pure-Python math library |
| (none — Unity rasterizer) | **`adapters/octane`** optional Octane material mapping |

Details and the full design are in [`ARCHITECTURE.md`](ARCHITECTURE.md).

## 5. Scope

### 5.1 In scope (prototype / Phase 1)

- `relativity_core`: Lorentz factor & contraction, relativistic velocity
  addition, relativistic Doppler factor, searchlight/beaming intensity factor,
  RGB↔XYZ and approximate wavelength-shift helpers, and the retarded-time
  apparent-position solve — all pure Python, fully unit-tested without C4D.
- Cinema 4D plugin skeletons that **register and load in C4D 2023+ without
  Octane**: Relativity Scene Controller, Relativistic Camera Tag, Relativistic
  Object Tag, with parameters and wiring.
- A **Lorentz deformation / bake utility** that applies the geometric transform
  to actual mesh points.
- An **approximate Doppler/searchlight material adjustment** (per-object, uniform
  approximation) on standard Cinema 4D materials.
- **Octane adapter stubs**: soft import, capability detection, and a stable
  interface — no behavior required when Octane is absent.
- Documentation and **test scaffolding**.

### 5.2 Out of scope (Phase 1, explicit)

- A **custom renderer** or full **physical relativistic ray tracing**.
- **Per-pixel** relativistic Doppler in the **live viewport** (we have no live
  shader-replacement hook; we approximate per object and/or bake).
- **Real-time interactive** first-person controls (Unity-style). Motion is driven
  by parameters and the animation timeline instead.
- **Relativistic lighting, shadows, reflections, refraction.**
- **General relativity**, gravity, accelerating reference frames beyond the
  single-observer model.
- **Spectrally accurate** physically-based color (we use tractable
  approximations).
- **Requiring Octane**, or producing Octane-*accurate* relativistic shading.
- Audio Doppler, particles, collisions, gameplay machinery (the upstream
  Sender/Receiver/Firework demo objects).

### 5.3 Simulation assumptions (inherited from special relativity & upstream)

For results to be meaningful, the prototype assumes the OpenRelativity
modelling rules:

- A single observer (the camera) may move freely; **other objects move at
  constant velocity** (straight lines, "from infinity to infinity") or stay
  still.
- The observer's speed never reaches `c`.
- Lighting/shadows are treated as baked into textures; dynamic relativistic
  lighting is not modelled.

## 6. Hard constraints (design rules)

These are non-negotiable and are enforced throughout the architecture:

1. Target **Cinema 4D 2023+**.
2. **Python first**, but keep the architecture ready for **C++ migration**.
3. The **core plugin must import without Octane installed**.
4. **Octane support is optional and isolated behind an adapter layer.**
5. **No full physical ray tracing** in Phase 1.
6. **No custom renderer** in this repository.
7. **Physics/math stays separate from Cinema 4D API code**
   (`relativity_core` never imports `c4d`).
8. **No external Python dependencies** unless absolutely necessary.

## 7. Audience & success criteria

- **Audience:** technical artists, motion designers, and educators who want a
  scientifically-motivated (if approximate) relativistic look inside C4D, plus
  developers who will extend toward Octane and C++.
- **Phase 1 success:** the plugins load in C4D 2023+ with Octane absent;
  `relativity_core` passes its unit tests under plain Python; an object with a
  Relativistic Object Tag visibly contracts and shifts color when the Scene
  Controller's `c` is lowered or velocities are raised; and the Octane adapter
  is a no-op stub that does not break import.

## 8. Non-goals for *this* document

This charter states *why* and *what*. The *how* (module boundaries, data flow,
C4D plugin types, C++ migration plan) lives in [`ARCHITECTURE.md`](ARCHITECTURE.md);
the *when* lives in [`ROADMAP.md`](ROADMAP.md).
