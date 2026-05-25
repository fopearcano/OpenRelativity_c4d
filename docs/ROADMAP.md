# Roadmap — OpenRelativity for Cinema 4D

Phased delivery. Each phase is a usable checkpoint, not a big-bang. Scope rules
from [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) §6 apply to every phase
(Cinema 4D 2023+, Python first, Octane optional/isolated, no custom renderer, no
external deps, physics separate from `c4d`).

Status legend: ✅ done · 🔜 next · ⬜ planned · 💡 exploratory (not committed)

---

## Phase 0 — Documentation & structure ✅

**Goal:** establish intent and a clean, C++-ready layout before any code.

- ✅ `README.md`, `PROJECT_CHARTER.md`, `ARCHITECTURE.md`, `ROADMAP.md`,
  `ORIGINAL_OPENRELATIVITY_REFERENCE.md`.
- ✅ Remove the upstream Unity project from the working tree; preserve the MIT
  license for attribution.
- ✅ Propose a clean, C++-ready layout (realized in Phase 1 as the
  `openrelativity_c4d` package; the initial `src/` scaffold was reorganized).
- ✅ Python/C4D-appropriate `.gitignore`.

**Exit criteria:** the repository explains itself and proposes a structure; no
plugin code exists yet.

---

## Phase 1 — Physics core + minimal plugin skeleton 🟡 (in progress)

**Goal:** a portable, tested math core and a plugin that *loads* in Cinema 4D
2023+ (with Octane absent), with the relativistic tags/deformer to follow.

Done:

- ✅ `openrelativity_c4d.core`: `relativity_math` (gamma, inverse gamma, length
  contraction, time dilation, collinear velocity addition), `doppler`,
  `searchlight`, `transforms` (vectors, 3D velocity addition, retarded-time
  apparent-position solve). `spectrum` (RGB↔XYZ recolor) deferred to a later phase.
- ✅ Unit tests under plain Python (`python -m unittest`), **no `c4d`**, including
  a guard that the core never imports `c4d`.
- ✅ Plugin package + `openrelativity_c4d.pyp` entry point with defensive imports
  and logging; registers the *Extensions > OpenRelativity C4D: About* command
  (version, target/running C4D version, Octane status, controller presence).
- ✅ **Relativity Scene Controller (v1)** — *Create Relativity Controller* command
  builds an `ORC_Relativity_Controller` Null with organized User Data (speed of
  light, global beta, effect strengths, preview mode, Octane/bake toggles) and
  safe defaults; clean name-based read/write helpers in `scene_controller`.
  (A future `ObjectData`/SceneHook version may replace the Null.)
- ✅ **Relativistic Camera (v1)** — *Setup Relativistic Camera* command uses the
  selected camera or creates `ORC_Relativistic_Camera`, with organized User Data
  (ORC enabled, observer beta, observer velocity, use-controller-global-beta,
  preview toggles, Octane/OSL placeholders) and `compute_observer_beta` resolving
  `beta` from the camera + controller via the math core. Shared User Data plumbing
  factored into `c4d/userdata.py`. Octane/OSL remain stubs.
- ✅ **Relativistic Objects (v1)** — *Setup Selected Relativistic Objects* adds
  per-object User Data (ORC object enabled, object beta, velocity X/Y/Z,
  use-camera-relative-direction, material preview toggles, bake-eligible, Octane
  material sync) to the selection, skipping the controller and cameras;
  *Select Relativistic Objects* re-selects them. `object_tools` provides
  `is_orc_object` / `add_orc_object_data` / `read_orc_object_settings` /
  `collect_orc_objects`. Metadata only - no geometry/material change yet.
- ✅ **Material previews (first visible effects)** — Doppler colour shift and
  searchlight beaming brightness/emission, sharing one generated Standard
  material per object (`ORC_Preview_<name>`), applied non-destructively (layered
  Texture tag). Commands: *Apply Doppler Material Preview*, *Apply Searchlight
  Preview*, *Apply Relativity Material Preview* (combined), *Clear Material
  Preview*. Uses `core.doppler`, `core.searchlight`, and
  `core.transforms.cos_theta_towards_observer`. Standard/Physical compatible;
  Octane not required. See `docs/DOPPLER_PREVIEW.md` and
  `docs/SEARCHLIGHT_PREVIEW.md`.
- ✅ **Lorentz geometry preview** — *Create / Remove Lorentz Preview Copies*
  build non-destructive contracted duplicates (`ORC_LorentzPreview_<name>`),
  scaling along the dominant velocity axis via
  `core.relativity_math.lorentz_contraction_scale` and
  `core.transforms.dominant_axis`; originals are optionally hidden and restored.
  Axis-aligned approximation only (no Terrell rotation). See
  `docs/LORENTZ_PREVIEW.md`.
- ✅ **Test scene & one-click preview** — *Create Test Scene* (controller +
  camera + light + approaching/receding/lateral/static objects; re-runnable with
  uniquely-named sets) and *Apply All Previews* (material + Lorentz together).
  See `docs/QUICKSTART.md`.
- ✅ **Octane detection & status** — `detect_octane_available()` (ID-independent,
  never raises) + `get_octane_status_report(doc)`, surfaced by the *Octane Status*
  command; no-op adapter facade. Verified import/run with Octane **absent**
  (unit-tested). Material/camera/AOV mapping remains stubbed. See
  `docs/OCTANE_INTEGRATION.md`.

**Exit criteria (met):** plugin loads without Octane; core tests pass in plain
Python; *Create Test Scene* + *Apply All Previews* visibly contracts and
recolours the moving objects in Standard/Physical; the Octane adapter is a safe
no-op.

Remaining (rolls into Phase 2):

- 🔜 **Combine the camera's velocity** into the object↔observer relative beta
  (currently beta is object/global only).
- 🔜 **Arbitrary-axis / point-level Lorentz** and **Terrell rotation** (true
  apparent geometry), plus a bake.
- 🔜 Description resources under `c4d/descriptions/` if/when these move to tags.

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

**Goal:** turn the adapter stubs into genuine Octane output. The detailed,
phased plan (A: scene/material prep, B: material/node adapter, C: AOVs, D:
experimental OSL camera, E: external bridge) lives in
[`OCTANE_INTEGRATION.md`](OCTANE_INTEGRATION.md). Detection/status (Phase 1) is
done; the rest below is unstarted.

- 🟡 Map per-object Doppler color + searchlight intensity onto **Octane material
  nodes** (e.g. diffuse/emission color and power) through the adapter only.
  *Started:* `octane/material_adapter.py` + the *Apply Octane-Compatible Material
  Preview* command exist with a safe Standard fallback; native Octane material
  creation is pending a verified parameter mapping (see `OCTANE_INTEGRATION.md`).
- 🟡 **Relativity AOVs / render passes** for compositing. *Started:*
  `octane/aov_adapter.py` defines the desired AOVs (Doppler/beta/searchlight/
  velocity/mask), the *Show AOV Plan* command, and render-settings detection;
  automatic Octane AOV creation is honestly unsupported (manual setup documented
  in `AOV_PIPELINE.md`).
- 🟡 **Experimental OSL camera** (Phase D, may not be feasible). *Started:*
  `octane/osl_camera.py` + the *Export Experimental OSL Camera* command write a
  clearly-marked placeholder shader; it is **not wired into Octane** (ray I/O
  binding unverified). See `OSL_CAMERA_EXPERIMENTS.md`.
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
