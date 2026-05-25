# Time-Delay (Light-Cone) System — Design

> **Status: DESIGN ONLY.** No light-travel-time physics is implemented yet. This
> document specifies *how* a future time-delay system would work and what it must
> account for. The only code that exists today is the **data structures** for
> object history samples in
> [`openrelativity_c4d/core/history.py`](../openrelativity_c4d/core/history.py)
> (pure Python, no `c4d`); see [§8](#8-data-structures-implemented-now).
>
> This is **Phase 2** work in [`ROADMAP.md`](ROADMAP.md) ("Animation, causality,
> and better visuals"). It builds on the existing single-point, constant-velocity
> retarded-time solver in `core.transforms` and generalises it to animated scenes.

## 0. The problem: what an observer *sees* is the past

Because light travels at a finite speed `c`, an observer at observer-time
`t_obs` does **not** see an object where it *is* at `t_obs`; they see it where it
*was* at an earlier **retarded time** `t_ret`, when the light now arriving was
emitted. For an object whose world position is `X(t)` and an observer at `O(t)`:

```
t_obs  =  t_ret  +  |O(t_obs) − X(t_ret)| / c
```

This implicit equation (the basis of the Liénard–Wiechert / retarded-time
picture) is what produces **apparent position lag** and, for fast objects,
**Terrell–Penrose rotation** — effects distinct from, and additional to, the
Doppler/searchlight colour shifts the plugin already previews.

`core.transforms.apparent_time_offset` / `apparent_position` already solve this
in closed form for **one point moving at constant velocity** with a static
observer (a quadratic in `t`). The hard, general case — **objects that
accelerate, follow rigs, or are driven by expressions/MoGraph/dynamics, viewed
by a possibly moving camera** — has no closed form. We must instead **sample each
object's motion over time** and search/interpolate those samples. That sampled
motion is the "object history"; everything below is the machinery to capture,
cache, query, and bake it.

> **Scope honesty.** This is a *visualization* approximation in flat spacetime
> with a single global `c`: per-object (pivot-level) retardation, not per-vertex;
> no general relativity, no gravitational lensing. Per-vertex/Terrell refinement
> is noted as future work, not promised here.

## 1. Object history sampling

**Goal:** for each relativistic object, record enough of its recent worldline
that the retarded-time solver can find `X(t_ret)` for any `t_ret` the light cone
asks for.

- **What is sampled.** Per object, per sampled scene time: the world transform —
  `position`, `rotation` (HPB), `scale`. (Velocity is *derived* by finite
  differences of neighbouring samples, so it need not be stored separately;
  storing it is an optional optimisation.)
- **Sample record.** One sample is a
  [`TransformSample`](../openrelativity_c4d/core/history.py): `(scene_time,
  position, rotation, scale)`. A per-object ordered buffer of these is an
  `ObjectHistory`.
- **How far back (window length).** The maximum delay any object needs is
  `max |O − X| / c` (the most distant object sets it). The history window must
  reach back **at least** that far before the earliest observer time being
  rendered. A practical rule: `window_seconds ≈ scene_radius / c` plus a margin.
- **How densely (sample step).** Sampling at the document frame rate (one sample
  per frame) is the natural default. Denser sub-frame sampling improves accuracy
  for fast/accelerating motion near the observer; sparser adaptive sampling
  (more samples where curvature/velocity is high) saves memory. The data
  structure is **frame-rate independent** (times are in seconds), so either
  policy works without changing it.
- **Interpolation.** Between samples the solver asks for `sample_at(t)`, which
  linearly interpolates position/scale/rotation. Linear HPB interpolation is a
  deliberate placeholder; a future quaternion slerp + Catmull–Rom position spline
  is the obvious accuracy upgrade and lives in the physics phase, not in the
  buffer.

## 2. Frame cache strategy

Sampling is **expensive** (see [§4](#4-sampling-cinema-4d-animation-curves):
evaluating the scene at an arbitrary time can mean moving the document clock and
re-running the scene's passes). It must be cached and reused.

- **Structure.** A per-document `HistoryCache` maps a stable object key
  (GUID/marker string) → `ObjectHistory`. `ObjectHistory` keeps its samples
  **sorted by time** and de-duplicates samples at the same time, so re-sampling a
  frame is idempotent.
- **Bounded memory (sliding window).** `ObjectHistory(max_samples=N)` keeps only
  the most recent `N` samples, dropping the oldest — a ring/sliding window sized
  to the delay window from [§1](#1-object-history-sampling). This caps memory at
  `objects × N × sizeof(sample)` regardless of timeline length.
- **Lazy population.** Sample a frame only when first needed (when the solver
  asks for a `t_ret` not yet covered), then keep it. Rendering a sequence walks
  observer time forward, so each frame's samples are reused by neighbouring
  frames' light cones.
- **Invalidation.** The cache carries a monotonically increasing `version` token;
  the host bumps it via `invalidate()` whenever something that affects motion
  changes — object add/remove/reparent, animation edits, controller `c` or
  strength changes, frame-rate change. Consumers compare the token they sampled
  against to detect a stale cache and re-sample. *The core only carries the
  token; deciding **when** to invalidate is the C4D layer's job* (it can watch
  document dirty checksums / `EVMSG_CHANGE`).
- **Keying.** Use the object's stable GUID/marker (not its name or pointer):
  names change and pointers are not stable across rebuilds, but the marker
  survives, so histories stay attached to the right object.

## 3. Observer time vs scene time

These are deliberately separate clocks and conflating them is the classic bug.

- **Scene time** (a.k.a. world / coordinate time): the single Cinema 4D document
  timeline `t`. The document has exactly **one** current time at any instant.
- **Observer time `t_obs`**: the camera's clock — effectively "the frame being
  rendered." When the camera shutter for output frame `f` opens, that is `t_obs`.
- **The key consequence.** A single rendered frame at `t_obs` is composed of
  objects sampled at **different scene times** `t_ret(object) ≤ t_obs`, each
  earlier by that object's own light delay (a near object is nearly "live"; a
  distant one lags more). You therefore **cannot** realise this by simply setting
  the document time to one value and rendering — that gives every object the same
  instant. You must place each object at *its* retarded transform. Hence history
  buffers + baked copies (below), not a single global time scrub.
- **Moving observer.** `O` is evaluated at `t_obs` (the observer's own clock)
  while each `X` is evaluated at that object's `t_ret`. The camera's own velocity
  also feeds the relative-beta colour math (already tracked in
  [`TODO.md`](../TODO.md) item 3) — the geometry delay and the colour shift share
  inputs but are computed independently.
- **Time dilation (related, separate).** A future option is to additionally
  *re-time* an object's internal animation by its `gamma` (a moving clock ticks
  slow). That is a remap of which `scene_time` an object's animation is read at;
  it composes with — but is not the same as — the light-travel delay. Listed
  under Phase 2 in the roadmap.

## 4. Sampling Cinema 4D animation curves

Two mechanisms, with a clear recommendation. Both feed the same
`TransformSample` buffer.

**(a) Track/curve evaluation — fast, side-effect-free, limited.**
Read an object's animation tracks directly:

```
for track in obj.GetCTracks():            # position/rotation/scale .x/.y/.z tracks
    curve = track.GetCurve()
    value = curve.GetValue(c4d.BaseTime(frame, fps))
```

- *Pros:* no document-state mutation, cheap, trivially parallel/pure.
- *Cons:* sees **only** keyframed PSR on that object. It misses expressions,
  MoGraph, dynamics/simulation, XPresso, and **parent-hierarchy** motion (a
  keyframed parent moving a static child). It is correct only for directly
  keyframed objects with no animated ancestor.

**(b) Document-time evaluation — accurate, slower, mutating.**
Move the document clock and read the resulting global matrix:

```
saved = doc.GetTime()
doc.SetTime(c4d.BaseTime(frame, fps))
doc.ExecutePasses(None, animation=True, expressions=True, caches=True, flags=...)
mg = obj.GetMg()                          # world transform incl. parents/rigs/sim
# ... record TransformSample(seconds, mg.off, matrix→HPB, scale) ...
doc.SetTime(saved); doc.ExecutePasses(...)  # ALWAYS restore
```

- *Pros:* captures the **fully evaluated** world transform — parents, expressions,
  MoGraph, and (for cached/baked sims) dynamics.
- *Cons:* mutates global document state (must save/restore the time and
  re-evaluate), is much slower, and is **not** safe to call from arbitrary
  threads. Best done as a one-time, main-thread **bake pass** over the needed
  frame range, writing into the cache.

**Recommendation.** Use **(b) `ExecutePasses` + `GetMg`** for correctness during
the bake (it is the only path that respects hierarchy and procedural motion), and
offer **(a) track sampling** as an opt-in fast path for the common case of a
single keyframed object with no animated ancestors. Read `fps` from
`doc.GetFps()` and the frame range from the render settings / `doc.GetMinTime()`
… `GetMaxTime()`; convert frames↔seconds at this boundary so the core stays
frame-rate independent.

## 5. Generating baked preview transforms

The renderer (standard **or** Octane) cannot ask "where was this object at its
retarded time?" on its own. We pre-compute the answer and bake it into ordinary,
renderable animation — exactly the non-destructive philosophy already used by the
Lorentz preview ([`LORENTZ_PREVIEW.md`](LORENTZ_PREVIEW.md)).

Per observer frame `f` (= `t_obs`), for each relativistic object:

1. **Solve** the retarded time `t_ret` from the light-cone equation in
   [§0](#0-the-problem-what-an-observer-sees-is-the-past). With a *sampled*
   worldline the closed form does not apply; use a robust 1-D root find on
   `g(t) = t_obs − t − |O(t_obs) − X(t)| / c` (monotonically decreasing in `t`
   for sub-luminal motion), e.g. a few bisection/fixed-point iterations, each
   evaluating `X(t)` via `ObjectHistory.sample_at(t)`. *(Future physics — not
   implemented now.)*
2. **Fetch** the retarded transform `sample_at(t_ret)` (interpolated).
3. **Optionally** apply the existing Lorentz contraction along the velocity
   direction (velocity ≈ finite difference of neighbouring samples), and later
   the Terrell apparent-position offset.
4. **Write** that transform onto a **non-destructive preview copy** of the object
   (e.g. an `ORC_LightDelay_<name>` duplicate, mirroring `ORC_LorentzPreview_`),
   as a **keyframe at frame `f`**. Never modify the original object's points or
   tracks.

Baking the whole frame range yields preview copies whose **own PSR animation
already encodes the light delay**. The scene then renders normally — in the
viewport, the standard renderer, or Octane — with no per-ray support required,
and a *Remove* command deletes the copies and restores originals. This is the
geometry analogue of the existing material previews and the natural feed for the
Phase 3 per-frame bake workflow.

## 6. How this differs from ordinary motion blur

Motion blur and light-travel delay are **orthogonal** and compose; they are not
substitutes.

| | Ordinary motion blur | Light-travel-time delay |
|---|---|---|
| What it does | Integrates appearance over the **shutter interval** around a single instant `t` — a *smear* of one moment. | **Displaces (and rotates)** the apparent transform to the **retarded** moment `t_ret` — a *shift*, not a smear. |
| Driven by | Shutter angle / exposure time. | Distance to observer and `c`. |
| With an instant shutter | Vanishes (nothing to integrate). | **Still present** — it is a position offset, not an integration. |
| Same for all objects? | Roughly, per shutter setting. | **No** — each object (and ultimately each surface point) lags by its own distance-dependent amount. |
| Produces Terrell rotation / apparent lag? | No. | Yes (that is the point). |

In short: blur answers "how far did it move *during the exposure*?"; the light
cone answers "where was it *when the light I'm now seeing left it*?" You can — and
often want to — have **both**: bake the retarded transforms (this system), then
let the renderer add ordinary motion blur on top of the baked motion.

## 7. Why Octane motion blur alone is insufficient

Octane's (and any path tracer's) motion blur samples object/camera transforms
**within the shutter window** around the current scene time and integrates them.
It fundamentally cannot stand in for the light cone because:

- **No notion of `c` or distance.** Motion blur has no speed-of-light parameter
  and no per-object distance term, so it cannot produce a **distance-dependent
  retardation** — the very mechanism of apparent lag and Terrell rotation.
- **Anchored to "now."** It blurs *around the current frame's* transform; it
  never places an object where it was *N frames ago*. The needed delay can be far
  larger than any plausible shutter interval (it scales with scene size / `c`),
  while shutters are sub-frame.
- **Uniform, not per-object.** A single shutter setting blurs the whole frame;
  the light cone needs a **different** time offset per object (and per surface
  point) by distance.
- **Integration, not displacement.** Even with a perfect shutter, blur yields a
  *smear of the present*, never a *sharp image of the retarded past* (which is
  what a short-exposure relativistic photograph actually is).

Therefore the plugin must **supply the retarded transforms itself** (the bake in
[§5](#5-generating-baked-preview-transforms)); Octane motion blur is then a
legitimate, additive finishing effect on top of that baked motion — not a
replacement for it.

## 8. Data structures (implemented now)

Only the **storage/query** layer exists today, in
[`openrelativity_c4d/core/history.py`](../openrelativity_c4d/core/history.py)
(pure Python, no `c4d`, unit-tested). It performs **no physics** — it is the
buffer a future retarded-time solver will fill (§4) and query (§5).

| Type | Role | Key API |
|---|---|---|
| `TransformSample` | One sampled world transform at a scene time (POD-style namedtuple). | `(scene_time, position, rotation, scale)`; `lerp_sample(a, b, f)` |
| `ObjectHistory` | Per-object, time-sorted sample buffer with an optional sliding window. | `add` / `extend`, `time_span`, `earliest` / `latest`, `bracket(t)`, `nearest(t)`, `sample_at(t)` (interpolated, endpoint-clamped) |
| `HistoryCache` | Per-document map of object key → `ObjectHistory`, with an invalidation `version`. | `get_or_create(key)`, `get`, `remove`, `clear`, `invalidate()`, `in` / `len` / iteration |

Design properties (kept deliberately minimal):

- **Pure & portable.** Plain tuples and numbers only — each type maps cleanly to a
  C++ struct + `std::vector` / `std::map`, preserving the
  [C++-migration path](ARCHITECTURE.md#7-path-to-c) for the core.
- **Frame-rate independent.** Times are seconds; the C4D layer converts
  frames↔seconds at the boundary.
- **Idempotent & bounded.** Re-sampling a time replaces (not duplicates) the
  sample; `max_samples` caps memory.
- **Physics-free by intent.** No `c`, no retarded-time solve, no Lorentz logic
  here. The solver (§5 step 1) and the C4D sampler/baker (§4–§5) are future work.

## 9. Open questions & non-goals

- **Per-vertex vs per-object.** This design retards the object pivot. True
  Terrell rotation and silhouette deformation are per-vertex; a per-vertex bake is
  a heavier future option (intersects with the mesh-density utility in the
  roadmap).
- **Accelerating / superluminal-apparent edge cases.** Root-finding must stay
  robust when an object's apparent motion is extreme; clamping (as the core's
  `MAX_BETA` already does for colour/contraction) will apply.
- **Sampling procedural motion.** Dynamics/MoGraph only sample correctly via the
  `ExecutePasses` path (§4b) and may need the sim baked first.
- **Non-goals:** general relativity, gravitational lensing, accelerating-frame
  metrics, and any claim of a physically exact render. This remains an
  **art-directable approximation**, consistent with
  [`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md).

---

*See also:* [`ARCHITECTURE.md`](ARCHITECTURE.md) (layering & C++ path),
[`ROADMAP.md`](ROADMAP.md) (Phase 2), [`LORENTZ_PREVIEW.md`](LORENTZ_PREVIEW.md)
(the non-destructive preview-copy pattern this reuses), and
`core/transforms.py` (`apparent_position`, the constant-velocity solver this
generalises).
