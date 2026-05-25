# Reference — MIT Game Lab's OpenRelativity (Unity)

This document analyzes the **original** OpenRelativity (Unity/C#) and maps each
of its concepts onto the Cinema 4D-native design of this project. It is a
*reference for implementers*, not a specification of what we will build — the
plan is in [`ROADMAP.md`](ROADMAP.md) and the design is in
[`ARCHITECTURE.md`](ARCHITECTURE.md).

- **Upstream project:** MIT Game Lab — OpenRelativity,
  <https://github.com/MITGameLab/OpenRelativity>
- **Upstream license:** MIT, © 2013 Massachusetts Institute of Technology
  (preserved in [`../MITLicense.md`](../MITLicense.md)).
- **Basis for this analysis:** the Unity/C# snapshot that originally populated
  this repository (now removed from the working tree; history retained in git).
  Formulas below are transcribed from that snapshot for fidelity.

> ⚠️ The original source is **not** included in this repository. This is an
> independent, Cinema 4D-native work that re-implements the *ideas*, not the
> code. The mapping is conceptual.

---

## 1. Upstream component overview

OpenRelativity puts essentially all of its relativistic *visuals* into a single
camera-bound GPU shader, with C# `MonoBehaviour` scripts feeding it state.

| Upstream file | Role |
|---|---|
| `Scripts/GameState.cs` | The "brain". Global relativistic state and shader globals. |
| `Scripts/MovementScripts.cs` | Player + camera controller; relativistic velocity addition; camera→shader params. |
| `Scripts/RelativisticObject.cs` | Per-object velocity, visibility timing, mesh prep, anti-cull. |
| `Scripts/ObjectMeshDensity.cs` | Subdivides large triangles for smooth GPU contraction. |
| `Shaders/relativity.shader` | Vertex (contraction + apparent position) + fragment (Doppler + searchlight). |
| `Shaders/skybox.shader` | Doppler shift applied to the sky. |
| `Example/.../Firework.cs`, `Sender/Receiver*.cs` | Demo machinery (spawning, timers). |
| `Shaders/ColorCorrectionEffect.cs`, `ImageEffectBase.cs`, `desaturateShader.shader` | Post-process color effects. |

### 1.1 `GameState.cs` — global state

Holds and publishes the simulation's relativistic state:

- An adjustable **speed of light** `c` (default `200` world units — kept low so
  effects are visible at human speeds), plus `cSqrd`.
- The **player velocity** vector and its scalar magnitude; a maximum speed clamp.
- **World time vs. player time** and their deltas; the cached factor
  `sqrtOneMinusVSquaredCWDividedByCSquared = sqrt(1 - v²/c²)` (i.e. `1/gamma`),
  used for time dilation: `deltaTimeWorld = deltaTimePlayer / sqrt(1 - v²/c²)`.
- Player **orientation** and a world-rotation matrix.
- Each frame it pushes **global shader uniforms**: `_playerOffset` (player world
  position), `_vpc` (player velocity / c), `_wrldTime`, and a `_colorShift`
  on/off flag.

→ Maps to the **Relativity Scene Controller** (see §3).

### 1.2 `MovementScripts.cs` — observer / camera controller

- Reads keyboard/mouse/controller input and applies **relativistic velocity
  addition** to the player velocity:

  ```
  v_new = (v + u_parallel + u_perpendicular / gamma) / (1 + (v · u)/c²)
  ```

  Implemented by rotating the velocity so the boost is along one axis (the
  formula is stable when the existing velocity is axis-aligned), adding, then
  rotating back.
- Smoothly changes the **speed of light** target (raising/lowering `c`).
- Drives **camera look** (mouse), independent of motion direction.
- Pushes camera-derived shader globals: `_spdOfLight`, `xyr` (pixel aspect
  ratio `width/height`) and `xs = tan(fovY/2)` — used by the fragment shader to
  reconstruct view directions.
- **Disables frustum/occlusion culling** (`layerCullSpherical`,
  `useOcclusionCulling = false`) because the vertex shader moves geometry into
  view that normal culling would discard.

→ Maps to the **Relativistic Camera Tag** (see §3).

### 1.3 `RelativisticObject.cs` — per-object behavior

- Stores the object's **velocity in world**, `viw`, and clamps it below max
  speed.
- Gives each object a **unique material instance** so per-object shader values
  (`_viw`, `_strtTime`, `_strtPos`) don't bleed across objects; updates `_viw`
  every frame.
- Computes a **light-travel-time** `tisw` for the object (same retarded-time
  quadratic as the shader, see §2.3) to decide **when the object should appear
  or disappear** in the observer's view — you must not see an object before its
  first light reaches you (`startTime`) or after its `deathTime`.
- **Defeats frustum culling** by inflating the mesh bounds to a huge box.
- Optional **parent mode** combines child meshes/materials into one mesh for
  performance.

→ Maps to the **Relativistic Object Tag** (see §3).

### 1.4 `ObjectMeshDensity.cs` — adaptive subdivision

Recursively splits any triangle whose world-space area exceeds a constant into
four, so the **vertex-shader** Lorentz contraction and apparent-position shift
look smooth (a coarse mesh would distort in chunky, obviously-wrong ways). Can
revert to the original mesh when the object is far away.

→ Maps to the **Mesh density / subdivision utility** (see §3). Still useful for
us because we move *real* points and want smooth results.

### 1.5 `relativity.shader` — the visual heart

A `Relativity/ColorShift` shader with two stages:

- **Vertex stage** — for each vertex, in a player-centered coordinate system:
  1. rotate so the player velocity lies along `z` (the equations assume motion
     along one axis);
  2. solve the **retarded-time** quadratic for `tisw` (when the light now
     arriving was emitted), see §2.3;
  3. offset the position by `velocity · tisw` and apply the **Lorentz
     contraction** along `z` (`/ sqrt(1 - speed²)`);
  4. rotate back;
  5. set a `draw` flag to 0 if the vertex would be seen *before* the object's
     start time (causality).
- **Fragment stage** — compute the **Doppler factor** from the relative velocity
  and the per-pixel view direction, convert the texture color RGB→XYZ, shift the
  XYZ color curves by that factor (folding in separate **IR** and **UV**
  texture channels so the visible window can slide), scale intensity by the
  **searchlight** factor `(1/shift)³`, then convert XYZ→RGB and clamp.

→ Splits into our **Lorentz Deformer** (geometry) and **Doppler material
adjustment** (color); the math becomes `relativity_core` (see §3).

### 1.6 `skybox.shader`

Applies the Doppler shift to the sky (the low-poly skybox can't use the
vertex-contraction path). → Exploratory in our roadmap (sky Doppler), not Phase 1.

### 1.7 Demo machinery

`Firework.cs`, `SenderScript.cs`, `ReceiverScript.cs`, `Receiver2Script.cs`, the
`Example/` scene and prefabs, and the post-process `ColorCorrectionEffect` are
**demonstration content**, not core physics. → Becomes `examples/` material in
later phases; not part of the prototype core.

---

## 2. Physics, transcribed

The relationships below are taken from the upstream snapshot so future
implementers of `relativity_core` have an exact reference. `β = v/c`.

### 2.1 Time dilation & length contraction

- Lorentz factor `γ = 1 / sqrt(1 - β²)`; upstream caches `1/γ = sqrt(1 - β²)`.
- World vs. player time: `Δt_world = Δt_player / sqrt(1 - β²)`.
- Lengths along the motion are scaled by `1/γ` (upstream divides the
  along-motion coordinate by `sqrt(1 - β²)` in the vertex stage).

### 2.2 Relativistic velocity addition

```
v_new = (v + u_parallel + u_perpendicular / γ) / (1 + (v · u) / c²)
```

Used both for the observer's acceleration (`MovementScripts`) and, in the
shader, to compose the object's velocity with the player's into a **relative
velocity** `vr` used for Doppler.

### 2.3 Apparent position via retarded time (aberration / Terrell rotation)

For a point at relative position `r` moving with velocity `v` (rotated so motion
is along one axis), solve for the light-travel-time `t`:

```
a·t² + b·t + c = 0
  a = c² - |v|²
  b = -2 (r · v)
  c = -|r|²
t = ( -b - sqrt(b² - 4ac) ) / (2a)
```

Then the apparent position is `r + v·t`, after which the along-motion component
is Lorentz-contracted. This light-travel-time treatment is what makes a fast
object appear **rotated/sheared** (the Terrell–Penrose effect), not merely
shortened.

### 2.4 Relativistic Doppler shift

With `θ` the angle between the relative velocity and the line of sight:

```
shift = (1 - β·cosθ) / sqrt(1 - β²)
```

- `shift > 1` → wavelengths stretched → **redshift** (object receding).
- `shift < 1` → wavelengths compressed → **blueshift** (object approaching).

Upstream applies the shift in XYZ color space using a handful of Gaussian color
primaries, with extra **IR** and **UV** texture channels so that, as the visible
window slides, infrared content can redshift *into* view and visible content can
blueshift *out* into ultraviolet.

### 2.5 Searchlight / beaming

Observed intensity is scaled by approximately:

```
intensity ∝ (1 / shift)³
```

so objects ahead (blueshifted) brighten and concentrate, while objects behind
(redshifted) dim. Upstream multiplies the XYZ tristimulus values by `(1/shift)³`.

> **Approximation note.** The color pipeline (a few Gaussian primaries + IR/UV
> channels, fixed exponent for beaming) is a tractable approximation, not a
> spectrally accurate renderer. We intentionally keep this approximation.

---

## 3. Concept → Cinema 4D mapping

| # | OpenRelativity (Unity) | What it does | Cinema 4D-native equivalent (this project) | Layer |
|---|---|---|---|---|
| 1 | `GameState` | Global `c`, observer velocity, world/observer time, gamma; pushes shader globals | **Relativity Scene Controller** (`SceneHookData`/`CommandData`) | `c4d_plugin` |
| 2 | `MovementScripts` | Observer motion (velocity addition), camera params, cull-defeat | **Relativistic Camera Tag** (`TagData` on a camera) | `c4d_plugin` |
| 3 | `RelativisticObject` | Per-object `viw`, appear/disappear timing, per-material values | **Relativistic Object Tag** (`TagData`) | `c4d_plugin` |
| 4 | `relativity.shader` vertex | Length contraction + apparent (retarded) position | **Lorentz Deformer / bake** (`ObjectData` deformer + bake command) — moves real points | `c4d_plugin` |
| 5 | `relativity.shader` fragment | Doppler color + searchlight + IR/UV spectrum | **Doppler/Searchlight material adjustment** (per-object approximation) | `c4d_plugin` |
| 6 | `ObjectMeshDensity` | Subdivide for smooth GPU distortion | **Mesh density / subdivision utility** (optional pre-bake) | `c4d_plugin` |
| 7 | Math embedded in shader/scripts | gamma, velocity addition, Doppler, retarded time | **`relativity_core`** pure-Python modules | `relativity_core` |
| 8 | (n/a — Unity rasterizer) | — | **`adapters/octane`** optional node mapping | `adapters/octane` |
| 9 | `skybox.shader` | Sky Doppler | 💡 Exploratory (sky Doppler) | later |
| 10 | `Firework`/`Sender`/`Receiver`, demo scene, post-FX | Demonstration content | **`examples/`** sample scenes | later |

## 4. Key architectural divergences (and why)

| Topic | Upstream (Unity) | Here (Cinema 4D) | Reason |
|---|---|---|---|
| Where geometry distorts | Camera vertex shader, every frame, on the GPU | A **deformer/bake** that moves real mesh points | No live per-vertex viewport program in C4D Python; no custom renderer allowed |
| Where color shifts | Camera fragment shader, **per pixel** | **Per-object** material color/luminance approximation (finer later) | No live per-fragment hook; must render in Standard/Octane |
| Observer control | Real-time first-person input | **Camera object + tag + timeline** parameters | C4D is authoring/rendering, not a game |
| State distribution | Global shader uniforms via `Shader.SetGlobal*` | **Scene Controller** distributes to tags | No global shader uniform bus; use scene data |
| Culling | Inflate bounds to defeat frustum culling | Non-issue for baked geometry | We move real points, not GPU-only positions |
| Renderer | Unity built-in pipeline | C4D Standard/Physical now; **Octane** later (optional) | Project goal + isolation constraint |
| Language | C# + CG/HLSL | **Python** now, **C++**-ready core | Iteration speed + migration plan |

## 5. What we deliberately drop from upstream

- The **interactive game loop** and FPS controls.
- The **demo gameplay** objects (fireworks, sender/receiver spawning).
- The **post-processing** color-correction image effects.
- Reliance on **GPU-only** position/color (replaced by real geometry +
  materials).
- The assumption of a **single hard-coded shader** doing everything.

What we keep is the **science** and the **practical lessons** (e.g. tessellation
matters; objects must respect light-travel-time causality; `c` should be
adjustable so effects are visible).
