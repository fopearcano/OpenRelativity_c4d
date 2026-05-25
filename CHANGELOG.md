# Changelog

All notable changes to **OpenRelativity_c4d** are recorded here. The format
loosely follows [Keep a Changelog](https://keepachangelog.com/). The project is
**pre-release**: plugin IDs are still development placeholders (see `ids.py` /
[`TODO.md`](TODO.md)), so there are no published releases yet.

## [Unreleased] - 0.1.0 (prototype)

First end-to-end prototype: a Cinema 4D 2023+ Python plugin for artist-facing,
**approximate** special-relativistic visualization, architected for later Octane
and C++ work. Inspired by MIT's Unity OpenRelativity but **not a port**.

### Added - physics core (pure Python, no `c4d`)
- `core.relativity_math`: `clamp_beta`, `beta_from_speed`, `gamma_from_beta`,
  `inverse_gamma_from_beta`, `lorentz_contraction_scale`, clamp helpers.
- `core.doppler`: `doppler_factor`, `approximate_rgb_doppler_shift`.
- `core.searchlight`: `searchlight_intensity_multiplier`.
- `core.transforms`: vector helpers, `add_velocity`, `apparent_position`
  (retarded-time), `cos_theta_towards_observer`, `dominant_axis`.
- `core.history`: data structures for the future time-delay / light-cone system
  (`TransformSample`, `lerp_sample`, `ObjectHistory`, `HistoryCache`) - storage /
  query only, **no physics yet**. Designed in `docs/TIME_DELAY_LIGHT_CONE_DESIGN.md`.
- Unit tests (run without Cinema 4D), incl. guards that the core imports no `c4d`.

### Added - Cinema 4D integration
- Plugin entry point (`openrelativity_c4d.pyp`) + defensive bootstrap/logging.
- **Relativity Controller** (Null + organized User Data) and **Relativistic
  Camera** / **Relativistic Object** setup, all addressed by field name.
- **Material previews**: Doppler colour, searchlight brightness/emission, and a
  combined preview - one shared `ORC_Preview_<name>` Standard material per
  object, applied non-destructively (layered Texture tag); plus Clear.
- **Lorentz geometry preview**: non-destructive contracted `ORC_LorentzPreview_<name>`
  duplicates; originals optionally hidden and restored on removal.
- **Create Test Scene** (approaching/receding/lateral/static; re-runnable) and
  **Apply All Previews**.
- **Control Panel** (`GeDialog`): one window with a button per command and a live
  status read-out.
- **Metadata JSON export** for renderer/post/debugging (documented schema).

### Added - Octane (optional, isolated; adapter/scaffolding only)
- Safe, ID-independent detection + **Octane Status**.
- Material adapter with a **Standard-material fallback** (no native Octane
  material yet) via **Apply Octane-Compatible Material Preview**.
- **AOV plan** (`Show AOV Plan`) documenting manual setup (no auto-creation yet).
- **Experimental OSL camera** generator + export (placeholder, not wired in).

### Added - tooling & docs
- `tools/run_core_tests.py`, `tools/verify_repo.py`, `tools/make_plugin_zip.py`.
- Docs: README, PROJECT_CHARTER, ARCHITECTURE, ROADMAP,
  ORIGINAL_OPENRELATIVITY_REFERENCE, USER_GUIDE, QUICKSTART, INSTALLATION,
  DEVELOPER_NOTES, DOPPLER_PREVIEW, SEARCHLIGHT_PREVIEW, LORENTZ_PREVIEW,
  OCTANE_INTEGRATION, AOV_PIPELINE, OSL_CAMERA_EXPERIMENTS, METADATA_SCHEMA,
  TEST_PLAN_C4D, TEST_PLAN_OCTANE, KNOWN_LIMITATIONS, C4D_PLUGIN_TYPE_MIGRATION,
  TIME_DELAY_LIGHT_CONE_DESIGN (future time-delay/light-cone system design).

### Changed - audit & refactor pass
- Extracted the duplicated object-tree walk into `c4d.scene_utils.iter_objects`
  (was copied in 6 modules).
- Centralized controller-field reading in `scene_controller.read_runtime`
  (replaced two near-duplicate settings readers in `preview_material` and
  `lorentz_preview`).
- Aligned **Control Panel button labels with the registered command names** (and
  added a Clear Material Preview button) to remove naming ambiguity.

### Known limitations
Approximate, not physics-grade: RGB (not spectral) Doppler; artistic searchlight;
axis-aligned Lorentz (no Terrell rotation); no light-travel-time sampling in the
previews yet (design + core data structures only - see
`docs/TIME_DELAY_LIGHT_CONE_DESIGN.md`); per-object/pivot-based; Octane native
materials/AOVs not implemented;
OSL camera experimental. Full list: [`docs/KNOWN_LIMITATIONS.md`](docs/KNOWN_LIMITATIONS.md).

### Notes
- **Plugin IDs are placeholders** (some past Maxon's `1000001-1000010` test
  range) and **must be replaced** with registered Plugin Café IDs before any
  public distribution.
- C4D-side behaviour is **manual-tested** (see the test plans); only the pure
  math and import-safe helpers are unit-tested.
