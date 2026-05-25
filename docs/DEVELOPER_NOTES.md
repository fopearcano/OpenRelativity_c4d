# Developer Notes

Practical notes for working on OpenRelativity_c4d. For the *why* and the big
picture see [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) and
[`ARCHITECTURE.md`](ARCHITECTURE.md); for the plan see [`ROADMAP.md`](ROADMAP.md).

## Layers & import rules

| Layer | Path | May import | Must NOT import |
|---|---|---|---|
| Physics core | `openrelativity_c4d/core/` | stdlib only | `c4d`, Octane, host-specific |
| C4D integration | `openrelativity_c4d/c4d/` | `c4d`, core, `..octane` | Octane modules directly |
| Octane adapter | `openrelativity_c4d/octane/` | Octane (guarded), core, `..c4d` (lazy) | — (must run with Octane absent) |
| Export | `openrelativity_c4d/export/` | stdlib, core, `..c4d` (lazy) | top-level `c4d` |
| Tests | `openrelativity_c4d/tests/` | core + import-safe helpers, stdlib | `c4d` |

Key invariants (enforced by tests + `tools/verify_repo.py`):

- **`core/` and `tests/` never import `c4d`** - the core is renderer-agnostic and
  C++-migratable; tests run in plain Python.
- **Octane is reached only through `openrelativity_c4d/octane/`**, always guarded;
  the plugin imports and runs without Octane.
- `octane/` and `export/` modules are **import-safe** (no top-level `import c4d`)
  so their non-C4D logic can be unit-tested; C4D access is lazy/inside functions.

## Module map

- `openrelativity_c4d.pyp` - entry point; adds its dir to `sys.path`, calls
  `bootstrap.register()`.
- `bootstrap.py` - guarded registration entry; `plugin_register.register_all()`
  registers every command.
- `core/` - `relativity_math`, `doppler`, `searchlight`, `transforms` (pure).
- `c4d/` - `commands` (all CommandData), `control_panel` (GeDialog launcher),
  `scene_controller` / `camera_tools` / `object_tools` (User-Data managers),
  `preview_material` (Doppler+searchlight materials), `lorentz_preview`
  (geometry copies), `test_scene`, `userdata` (shared User-Data plumbing).
- `octane/` - `detection`, `adapter` (facade), `material_adapter`, `aov_adapter`,
  `osl_camera` (experimental), `camera_adapter` (stub).
- `export/` - `metadata_export` (JSON).
- `tools/` - `run_core_tests.py`, `verify_repo.py`, `make_plugin_zip.py`.

## Conventions

- **User Data, not (yet) ObjectData/TagData.** The controller/camera/objects are
  ordinary C4D objects carrying organized **User Data**; values are addressed
  **by field name** (see `c4d/userdata.py`), so no per-field IDs are needed.
- **Generated names are reserved.** Materials/objects use `ORC_` prefixes
  (`ORC_Preview_`, `ORC_LorentzPreview_`, ...). `object_tools` excludes generated
  copies from the relativistic-object collection (single source of truth in
  `object_tools.LORENTZ_PREVIEW_PREFIX`).
- **Approximations, not physics.** Doppler/searchlight/Lorentz results are
  art-directable approximations; this is stated in code, docs, and the metadata
  export's `approximation_notes`.

## Running checks

```
python tools/verify_repo.py        # one-shot: files, no-c4d, tests, docs, entrypoint
python -m unittest                 # the pure-Python tests
python tools/make_plugin_zip.py    # build build/OpenRelativity_c4d_v<version>.zip
```

`verify_repo.py` exits non-zero on failure - use it in CI / pre-commit. The
`c4d/` layer is **not** covered by these; test it manually inside Cinema 4D 2023+
(see [`INSTALLATION.md`](INSTALLATION.md) §3).

## Adding a new command

1. Add a `CommandData` subclass in `c4d/commands.py` (or a dedicated module).
2. Add a placeholder ID in `ids.py` (see the ID note below).
3. Register it in `c4d/plugin_register.py` with a clear menu string.
4. (Optional) add a button to `c4d/control_panel.py` (`_SECTIONS`).
5. Update the docs and `tools/verify_repo.py` (`EXPECTED_FILES`/`EXPECTED_DOCS`)
   if you added files.

Keep arithmetic in `core/`; the `c4d/` layer should read scene state, call the
core, and write results back.

## Testing philosophy

- **Unit-tested:** the pure math (`core/`) and the import-safe behaviour of the
  Octane detection/material/AOV/OSL helpers and the metadata export (skeleton,
  serialization, safe fallbacks).
- **Manual (in Cinema 4D):** anything that touches `c4d` - materials, geometry,
  dialogs, undo, save dialogs, render.

When adding pure logic, prefer putting it in `core/` (or an import-safe helper)
so it can be tested.

## C++ migration

`core/` has a numeric, dependency-free API (numbers/tuples in and out) so it can
be reimplemented in C++ behind the same signatures, with the `c4d/` classes
re-authored against the Cinema 4D C++ SDK. Avoid leaking rich Python-only objects
across the core's public boundary. See [`ARCHITECTURE.md`](ARCHITECTURE.md) §7.

## Octane status & what's needed next

Octane is **adapter-level**: detection + Standard-material fallback + an AOV plan
+ an experimental OSL camera generator. To implement native Octane materials/AOVs
you need verified Octane IDs/API data - enumerated in
`octane/material_adapter.required_octane_material_info()` and
`octane/aov_adapter.REQUIRED_OCTANE_AOV_INFO`, with the plan in
[`OCTANE_INTEGRATION.md`](OCTANE_INTEGRATION.md).

## Plugin IDs

Cinema 4D requires every plugin element (command, dialog, tag, object, scene
hook) to have a **globally unique** integer ID. If two installed plugins claim
the same ID, Cinema 4D loads only **one** of them at startup - a duplicated or
copied-from-sample ID here can silently block another plugin (and vice versa).

- **All IDs live in one file:** `openrelativity_c4d/ids.py`. Every registration
  uses a named `ids.ID_ORC_*` constant - never a raw number.
- **They are temporary private prototype IDs**, derived as `ORC_ID_BASE + n`.
  They are **not** registered with Maxon and **not** guaranteed unique; they only
  move the plugin off the heavily-reused `1000001–1000010` test range.
- **Before public distribution:** obtain unique IDs (free) from the Maxon Plugin
  Café (https://plugincafe.maxon.net/, https://developers.maxon.net/) and either
  set `ORC_ID_BASE` to your first registered ID (registering a contiguous block)
  or give each constant its own registered ID; then remove the warning in
  `ids.py`.
- **If another local plugin is blocked:** change `ORC_ID_BASE` in `ids.py` to a
  different high number and restart Cinema 4D - that relocates the whole block at
  once.
- **Audit:** run `python tools/audit_plugin_ids.py` to list the IDs, confirm
  uniqueness, flag any known sample IDs, and confirm every registration uses an
  `ids.*` constant. `ids.all_ids()` returns the full `{name: id}` map.

## Icons

Command icons are loaded through one place,
`openrelativity_c4d/c4d/icon_loader.py`, which is **safe by construction** - a
missing or unreadable icon never affects whether a command works.

- Registration uses `icon=icon_loader.safe_icon("icon_<name>")`; `safe_icon`
  returns a cached `c4d.bitmaps.BaseBitmap` or **`None`** (which registers the
  command without an icon - the prior behavior). It never raises.
- Paths resolve relative to the package via `get_plugin_root()` /
  `get_icon_path()` (no hardcoded absolute paths). The PNGs live in
  `openrelativity_c4d/resources/icons/png/`; the loader reads PNG only.
- `icon_loader.py` has **no top-level `import c4d`** (lazy import inside
  `load_icon_bitmap`), so the path logic is unit-tested in plain Python
  (`tests/test_icon_loader.py`) and pulls in no Octane.
- At the end of `register_all` the plugin logs an icon diagnostic
  (`Command icons: N loaded, M missing.`, plus a warning listing any missing).
  See `icon_loader.get_load_summary()` / `format_load_summary()`.
- To add/replace an icon: regenerate via `python tools/generate_icons.py` (see
  [`ICONS.md`](ICONS.md)); no registration code changes are needed as long as the
  file name matches the `safe_icon("icon_<name>")` call.
