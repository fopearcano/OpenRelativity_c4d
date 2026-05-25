# Roadmap — OpenRelativity for Cinema 4D

Phased delivery. Each phase is a usable checkpoint, not a big-bang. Scope rules
from [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) §6 apply to every phase
(Cinema 4D 2023+, Python first, Octane optional/isolated, no custom renderer, no
external deps, physics separate from `c4d`).

Status legend: ✅ done · 🔜 next · ⬜ planned · 💡 exploratory (not committed)

---

## Phase 0 — Documentation & structure ✅ (this commit)

**Goal:** establish intent and a clean, C++-ready layout before any code.

- ✅ `README.md`, `PROJECT_CHARTER.md`, `ARCHITECTURE.md`, `ROADMAP.md`,
  `ORIGINAL_OPENRELATIVITY_REFERENCE.md`.
- ✅ Remove the upstream Unity project from the working tree; preserve the MIT
  license for attribution.
- ✅ Scaffold `src/relativity_core`, `src/c4d_plugin` (+ `res/`),
  `src/adapters/octane`, `tests/`, `examples/` with intent-only `README` stubs.
- ✅ Python/C4D-appropriate `.gitignore`.

**Exit criteria:** the repository explains itself and proposes a structure; no
plugin code exists yet.

---

## Phase 1 — Physics core + minimal plugin skeleton 🔜

**Goal:** a portable, tested math core and plugins that *load* in Cinema 4D
2023+ (with Octane absent) and demonstrably contract & recolor an object.

- 🔜 `relativity_core`:
  - `constants`, `lorentz` (gamma, length contraction),
    `velocity` (relativistic addition), `doppler` (Doppler + searchlight),
    `spectrum` (RGB↔XYZ + approximate recolor), `aberration` (retarded-time
    apparent-position solve).
  - Unit tests that run under plain Python (`unittest`/`pytest`), **no `c4d`**.
- 🔜 `c4d_plugin` skeletons that register cleanly in C4D 2023+:
  - **Relativity Scene Controller** — owns `c`, observer velocity, time;
    distributes state.
  - **Relativistic Camera Tag** — observer velocity (via `relativity_core`),
    exposes FOV/aspect.
  - **Relativistic Object Tag** — per-object world velocity + flags.
  - Resource files under `res/` for parameters and labels.
- 🔜 **Lorentz Deformer / bake utility** — applies the geometric transform to
  real mesh points (live deformer + a bake command).
- 🔜 **Approximate Doppler/searchlight material adjustment** — per-object color
  & luminance on standard C4D materials.
- 🔜 **Octane adapter stubs** — `is_available()` + no-op mapping; verified that
  the plugin imports with Octane **not** installed.

**Exit criteria:** plugins load without Octane; `relativity_core` tests pass in
plain Python; lowering `c` (or raising velocity) visibly contracts and recolors
a tagged object; the Octane adapter is a safe no-op.

---

## Phase 2 — Animation, causality, and better visuals ⬜

**Goal:** make it behave well across the timeline and look closer to upstream.

- ⬜ **Time-dilation on the timeline** — observer vs. world clock; animated
  processes slowed per `gamma`.
- ⬜ **Causal visibility gating** — an object isn't shown before its light could
  reach the observer (upstream `_strtTime`/`draw` logic), and a death-time
  analogue — expressed via visibility tracks/keys.
- ⬜ **Mesh density / subdivision utility** — the analogue of upstream
  `ObjectMeshDensity`, so contraction/aberration stay smooth on coarse meshes.
- ⬜ **Finer Doppler** — move from per-object uniform color toward per-point /
  per-UV approximation; improve the spectrum/IR-UV handling.
- ⬜ **Example scenes** in `examples/` demonstrating each effect.

**Exit criteria:** a short animation shows contraction, Doppler, beaming, and
time dilation consistently, with smooth geometry and correct appear/disappear
timing.

---

## Phase 3 — Octane integration (real) ⬜

**Goal:** turn the adapter stubs into genuine Octane output.

- ⬜ Map per-object Doppler color + searchlight intensity onto **Octane material
  nodes** (e.g. diffuse/emission color and power) through the adapter only.
- ⬜ **Per-frame bake workflow** for deformed geometry so Octane renders the
  apparent shapes.
- ⬜ Presets and artist-facing UX (sensible defaults, unit handling, helpful
  parameter ranges).
- ⬜ Verify the core plugin still imports and runs with Octane **absent**
  (regression guard for the isolation rule).

**Exit criteria:** an artist can render a relativistic shot in Octane; removing
Octane degrades gracefully to the standard-material path.

---

## Phase 4 — Performance & C++ migration ⬜

**Goal:** speed and the planned language transition.

- ⬜ Profile deformation/bake on dense meshes; cache and vectorize hot paths.
- ⬜ Reimplement `relativity_core` in **C++** (Cinema 4D C++ SDK) behind the
  same numeric API; keep Python parity for testing.
- ⬜ Optionally re-author `c4d_plugin` classes against the **C++ SDK**
  (`TagData`/`ObjectData`/`SceneHookData`/`CommandData`).

**Exit criteria:** measurable speedups on representative scenes; the C++ core
passes the same numerical tests as the Python core.

---

## Exploratory / not committed 💡

Tracked so they aren't mistaken for plans:

- 💡 Spectrally accurate (SPD-based) Doppler color.
- 💡 Sky/environment Doppler (the upstream `skybox.shader` analogue).
- 💡 True relativistic path tracing via custom camera-ray generation (would
  require renderer-level work explicitly **out of scope** here).
- 💡 General-relativistic effects, gravitational lensing, accelerating frames.
- 💡 Relativistic lighting/shadows/reflections.

---

## Cross-cutting, every phase

- Keep `relativity_core` free of `c4d` and of third-party deps.
- Keep Octane imports confined to `adapters/octane`.
- Keep tests runnable without Cinema 4D.
- Update docs alongside code; keep this roadmap's status markers current.
