# Migration Plan: User Data → Cinema 4D plugin types

How (and whether) to move from the current **command-created User Data** model to
proper Cinema 4D plugin types — `TagData` for the camera/object settings, and
`ObjectData` (or a robust Null) for the controller. This is a **plan**, not an
implementation; only the safest first step is implemented now (see
[Staged plan](#staged-implementation-plan)).

## Current state

The relativity settings are stored as **User Data** on ordinary objects, created
and edited by commands:

- **Controller** — a `Null` named `ORC_Relativity_Controller` (`scene_controller.py`).
- **Camera** — User Data on a `Camera` object (`camera_tools.py`).
- **Object** — User Data on any scene object (`object_tools.py`).

All fields are addressed **by display name** through the shared `userdata.py`
helpers. The exact field set/defaults are now mirrored declaratively in
`openrelativity_c4d/c4d/field_specs.py` (see the safe first step below).

## Why consider a migration?

User Data is great for a fast prototype but has limits the plugin will hit:

- No **live evaluation** hook (a `TagData` gets `Execute`/`MSG_*`, so a camera or
  object can react when the scene changes/animates; User Data is inert data that
  a command must be re-run to act on).
- Weak **discoverability/UX** (User Data looks generic; a real tag has an icon,
  a name, a proper Attribute Manager page, and shows up in the Tags menu).
- No clean per-type **defaults/validation/Description cycles** beyond what we
  hand-build.

## Comparison

| Aspect | Current: User Data | `TagData` (tag on an object) | `ObjectData` (a generator/null-like object) |
|---|---|---|---|
| Attribute Manager UI | Generic "User Data" | Proper, named page + icon | Proper, named page + icon |
| Live evaluation | None (command re-run) | `Execute`/`Message` per pass | `GetVirtualObjects`/`Execute` |
| Resource/description | None needed | Needed (`.res` **or** programmatic) | Needed (`.res` **or** programmatic) |
| Registered plugin ID | Not required | **Required** | **Required** |
| Plugin-absent behaviour | Degrades gracefully (data stays) | Object shows **"missing plugin"** | Object becomes **"missing plugin"** |
| Undo / persistence | Standard, simple | Standard | Standard |
| Testability (no C4D) | Pure helpers testable | Needs Cinema 4D | Needs Cinema 4D |
| Implementation cost | Low (done) | Medium | Medium–High |
| Best fit here | Controller (scene-global) | **Camera & object settings** | Controller (optional) / deformer |

**Takeaway:** the migration pays off most for the **camera** and **object**
settings (they benefit from a real tag UI + live evaluation). For the
**controller**, a Null/SceneHook is arguably better than `ObjectData` because it
is scene-global and does not need per-frame geometry.

## Target design (proposed)

- **Relativity Controller — keep robust Null-based (recommended), or SceneHook.**
  A controller is scene-global state, not geometry. Options: (a) keep the Null +
  User Data (most robust: no "missing plugin" risk, already works); (b) a
  `SceneHookData` holding the global state; (c) an `ObjectData`. Recommendation:
  (a) for now, optionally (b) later. Avoid (c) — it adds missing-plugin risk for
  little gain.
- **Relativistic Camera — `TagData`** on a camera. Holds observer beta/velocity +
  preview flags; `Message`/`Execute` can keep derived values fresh and (later)
  drive the camera. Replaces `camera_tools`' User Data.
- **Relativistic Object — `TagData`** on scene objects. Holds object beta/velocity
  + preview flags; can trigger the material/deformation update. Replaces
  `object_tools`' User Data. (A separate Lorentz **deformer** would be
  `ObjectData`.)

All three derive their parameter set from the **single schema** in `field_specs`.

## Description / resource files

Two ways to give a `TagData`/`ObjectData` its parameters:

1. **Programmatic description (recommended).** Implement `GetDDescription` and
   build the parameters at runtime by iterating `field_specs`. **No `.res` files**
   to hand-write or keep in sync, and it reuses the schema we already validate and
   test. Best fit for this project.
2. **Resource files (`.res`).** Per plugin, under
   `openrelativity_c4d/c4d/descriptions/`:
   - `T<name>.res` (tag) / `O<name>.res` (object) — the parameter layout;
   - a symbol header (e.g. `c4d_symbols.h` / `<name>.h`) — integer IDs;
   - `strings_xx/<name>.str` — localized labels (e.g. `strings_us/`);
   - registration referencing the description name.
   More boilerplate, must stay in sync with the schema, and the `.res` syntax
   can't be validated outside Cinema 4D.

**Recommendation:** go programmatic (Option 1); keep `descriptions/` only if a
specific feature needs a fixed `.res`.

## Plugin ID requirements

- Each `TagData`/`ObjectData`/`SceneHookData` needs a **globally unique,
  registered** plugin ID (free from the Maxon Plugin Café).
- Reserved constants already exist in `ids.py`: `ID_ORC_RELATIVISTIC_CAMERA_TAG`,
  `ID_ORC_RELATIVISTIC_OBJECT_TAG`, `ID_ORC_LORENTZ_DEFORMER_OBJECT`,
  `ID_ORC_RELATIVITY_SCENEHOOK` (all derived from `ORC_ID_BASE`). These are
  **temporary private prototype IDs and MUST be replaced with registered IDs**
  before the tags ship (see [`TODO.md`](../TODO.md) #1 and `ids.py`).
- Programmatic-description parameter IDs are local to each plugin (small ints),
  so only the top-level plugin IDs need registration.

## Risk analysis

- **Scene compatibility / data migration (high).** Existing scenes use User Data;
  adding tags will not auto-convert them. Need a one-time **migration helper**
  (read User Data → create tag → optionally remove User Data) and a transition
  period where both are understood.
- **Plugin-absent fragility (high).** Objects carrying our **tags** show as
  "missing plugin" if the plugin isn't installed (and may not round-trip), whereas
  User Data persists. Document clearly; keep the controller Null-based to limit
  blast radius.
- **Testability (medium).** `TagData`/`ObjectData` need Cinema 4D to test; only
  the schema + pure helpers are unit-testable. Mitigate by keeping all math/logic
  in `core`/pure helpers and the tag classes thin.
- **Undo / evaluation correctness (medium).** Live `Execute`/messages add timing
  and undo considerations not present with command-driven User Data.
- **Icons & polish (low).** Tags want icons/registration metadata.
- **Surface/maintenance (low–medium).** More plugin types to maintain; mitigate
  via the shared schema + thin classes.

## Staged implementation plan

Each step is independently shippable and keeps the working plugin intact. Tags
land **behind a feature flag (default off)** so the User Data path stays the
default until proven.

- **Step 1 — Canonical field schema (DONE, this commit).**
  `openrelativity_c4d/c4d/field_specs.py`: pure, c4d-free, validated by
  `tools/verify_repo.py` and unit tests. The single source the descriptions will
  iterate. No runtime behaviour change.
- **Step 2 — Schema-driven User Data.** Add `userdata.build_from_spec(obj, entity)`
  and have `scene_controller`/`camera_tools`/`object_tools` build their User Data
  by iterating `field_specs` (and source their `FIELD_*`/`DEFAULTS` from it),
  removing duplication. Verify parity manually in Cinema 4D.
- **Step 3 — Relativistic Object `TagData` (flagged).** One `TagData` with a
  **programmatic `GetDDescription`** generated from `field_specs`; read its values
  via the same accessors. Manual test in C4D; User Data remains the default.
- **Step 4 — Relativistic Camera `TagData` (flagged).** Same pattern for the
  camera.
- **Step 5 — Controller decision.** Keep Null-based (recommended) or move to
  `SceneHookData`; do **not** require an `ObjectData` controller.
- **Step 6 — Migration + compatibility.** A helper to convert existing User-Data
  scenes to tags; icons; round-trip/missing-plugin handling; register **real
  plugin IDs**.
- **Step 7 — Promote & deprecate.** Once tags are proven, flip the default,
  update commands/docs/tests, and deprecate the User Data path.

**Cross-cutting:** register real Plugin Café IDs (blocker for any tag), keep
`tools/verify_repo.py` green, keep all math in `core`, and add C4D manual test
cases (extend [`TEST_PLAN_C4D.md`](TEST_PLAN_C4D.md)) for each new tag.

## Decision summary

Incremental, **schema-driven**, **programmatic descriptions**, tags **behind a
flag**, controller **stays Null-based**. Step 1 (the schema) is implemented now;
everything else is deferred and gated on registered plugin IDs and in-Cinema-4D
validation.
