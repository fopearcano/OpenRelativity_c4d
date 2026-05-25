# UI / UX Audit

> **Audit only - no behavior changes.** This document inventories the current
> user-facing surface (menu commands, dialogs, Control Panel) and proposes a
> clean reorganization pass. It changes **no** physics/math, **no** Octane adapter
> behavior, **no** plugin IDs, and adds **no** feature logic. Nothing here is
> implemented yet; see [Implementation plan](#9-implementation-plan).

## 1. Current UI structure

### Entry points
The plugin exposes itself in two ways, both registered from
`c4d/plugin_register.py::register_all` (called by `bootstrap.register`):

1. **Extensions menu** - 20 `CommandData` plugins, each registered with
   `c4d.plugins.RegisterCommandPlugin(...)` and a name prefixed
   `"OpenRelativity C4D: "` (from `constants.PLUGIN_NAME`). They appear as a
   **flat, alphabetical-ish list** under *Extensions* (no submenu grouping).
2. **Two dialogs** (`c4d.gui.GeDialog`):
   - **About** - modal (`commands.py::AboutDialog` / `AboutCommand`), opened at
     `defaultw=460, defaulth=260`.
   - **Control Panel** - async/dockable (`control_panel.py::ControlPanelDialog` /
     `ControlPanelCommand`), opened at `defaultw=300, defaulth=0`.

### Registration code (`plugin_register.py`)
- 20 **near-identical blocks**, ~16 lines each: a `RegisterCommandPlugin(...)`
  call followed by an `if registered: log.info(...) else: log.error(...); ok=False`.
- Every call passes **`icon=None`** (20×) - the plugin ships with **no icons**.
- Startup logging already reports command name + assigned ID + success/failure
  (good; keep it).

### Control Panel (`control_panel.py`)
- A compact `GeDialog`: a 4-row **status read-out** (Controller / Camera / ORC
  objects / Octane), then command buttons grouped into **5 sections** laid out 2
  columns each, then a **Refresh / Close** footer.
- Sections today (`_SECTIONS`): *Scene setup* (4), *Material preview* (4),
  *Lorentz geometry* (2), *Octane / export* (4), *Info* (1) = **15 buttons**.
- Buttons fire the real commands via `c4d.CallCommand(<id>)` (no duplicated
  logic - good), with IDs referenced from `ids.py`.

### About dialog (`commands.py`)
- Single-column stack of ~17 `AddStaticText` lines built by `about_info_lines()`
  (tagline, versions, Octane/controller/camera/object/preview/Lorentz status,
  phase, status summary, URL), plus an OK button.

### Icons / resources
- **None.** All commands use `icon=None`. `c4d/descriptions/` contains only a
  `README.md` (no `.res`/`.str`/`.h`, no bitmaps). There is no `res/` or `icons/`
  directory anywhere in the repo.

## 2. Existing commands

All 20 registered commands (class → menu name → central ID constant), with the
proposed section (see [§7](#7-proposed-section-mapping)) and whether the command
is currently reachable from the Control Panel:

| # | Class (`commands.py` / `control_panel.py`) | Menu name (after `"OpenRelativity C4D: "`) | ID constant (`ids.py`) | In Control Panel? | Proposed section |
|--:|---|---|---|:--:|---|
| 1 | `AboutCommand` | About | `ID_ORC_ABOUT_COMMAND` | yes | Help |
| 2 | `ControlPanelCommand` | Control Panel | `ID_ORC_CONTROL_PANEL_COMMAND` | n/a (is the panel) | launcher |
| 3 | `CreateControllerCommand` | Create Relativity Controller | `ID_ORC_CREATE_CONTROLLER_COMMAND` | yes | Setup |
| 4 | `SetupCameraCommand` | Setup Relativistic Camera | `ID_ORC_SETUP_CAMERA_COMMAND` | yes | Setup |
| 5 | `SetupObjectsCommand` | Setup Selected Relativistic Objects | `ID_ORC_SETUP_OBJECTS_COMMAND` | yes | Setup |
| 6 | `SelectObjectsCommand` | Select Relativistic Objects | `ID_ORC_SELECT_OBJECTS_COMMAND` | **no** | Setup |
| 7 | `CreateTestSceneCommand` | Create Test Scene | `ID_ORC_CREATE_TEST_SCENE_COMMAND` | yes | Setup |
| 8 | `ApplyDopplerPreviewCommand` | Apply Doppler Material Preview | `ID_ORC_APPLY_DOPPLER_PREVIEW_COMMAND` | yes | Preview |
| 9 | `ApplySearchlightPreviewCommand` | Apply Searchlight Preview | `ID_ORC_APPLY_SEARCHLIGHT_PREVIEW_COMMAND` | yes | Preview |
| 10 | `ApplyRelativityMaterialPreviewCommand` | Apply Relativity Material Preview | `ID_ORC_APPLY_RELATIVITY_PREVIEW_COMMAND` | yes | Preview |
| 11 | `ApplyAllPreviewsCommand` | Apply All Previews | `ID_ORC_APPLY_ALL_PREVIEWS_COMMAND` | **no** | Preview |
| 12 | `CreateLorentzPreviewCommand` | Create Lorentz Preview Copies | `ID_ORC_CREATE_LORENTZ_PREVIEWS_COMMAND` | yes | Preview |
| 13 | `RemoveLorentzPreviewCommand` | Remove Lorentz Preview Copies | `ID_ORC_REMOVE_LORENTZ_PREVIEWS_COMMAND` | yes | Preview |
| 14 | `ClearMaterialPreviewCommand` | Clear Material Preview | `ID_ORC_CLEAR_PREVIEW_COMMAND` | yes | Preview |
| 15 | `OctaneStatusCommand` | Octane Status | `ID_ORC_OCTANE_STATUS_COMMAND` | yes | Octane |
| 16 | `ApplyOctaneCompatibleMaterialPreviewCommand` | Apply Octane-Compatible Material Preview | `ID_ORC_APPLY_OCTANE_MATERIAL_COMMAND` | **no** | Octane |
| 17 | `ShowAOVPlanCommand` | Show AOV Plan | `ID_ORC_SHOW_AOV_PLAN_COMMAND` | yes | Octane |
| 18 | `OctaneDiagnosticsCommand` | Octane Diagnostics | `ID_ORC_OCTANE_DIAGNOSTICS_COMMAND` | yes | Diagnostics |
| 19 | `ExportMetadataCommand` | Export Relativity Metadata JSON | `ID_ORC_EXPORT_METADATA_COMMAND` | yes | Export |
| 20 | `ExportOSLCameraCommand` | Export Experimental OSL Camera | `ID_ORC_EXPORT_OSL_CAMERA_COMMAND` | **no** | Export |

**Coverage gap:** the Control Panel is missing 4 user commands - **Select
Relativistic Objects (6)**, **Apply All Previews (11)**, **Apply
Octane-Compatible Material Preview (16)**, and **Export Experimental OSL Camera
(20)** - so the menu and the panel already disagree about what exists. *Apply All
Previews* (the headline one-click action) being absent is the most surprising.

## 3. Repeated / duplicated UI code

| Where | Duplication | Note |
|---|---|---|
| `plugin_register.py` | 20× the same register-then-log-success/failure block (~300 lines) | Pure boilerplate; differs only by id / name / help / factory. Prime target for a **data-driven registry**. |
| `commands.py` status helpers (`_controller_status`, `_camera_status`, `_object_status`, `_preview_status`, `_lorentz_status`, `_octane_status`) **vs** `control_panel.py::_status_values` | Two independent implementations of "read scene status" | About and Control Panel can drift; should share **one status provider**. |
| Many commands | Repeated `if doc is None: return False` + `c4d.gui.MessageDialog(...)` result patterns | Mild; `_apply_preview_message` already factors one case. Not urgent. |
| `control_panel.py::_SECTIONS` | A hand-maintained button list that must be kept in sync with the registered commands by hand | Should be **derived from** the same registry as the menu so they cannot diverge (see the §2 gap). |

## 4. Sizing & grouping assessment

- **Extensions menu - ungrouped.** 20 flat entries in one list. No submenu, no
  separators; long and hard to scan. Grouping into labelled submenus is the
  biggest menu-side win.
- **Control Panel - grouped but tall, and inconsistent.** Five stacked group
  boxes of 2-column buttons + 4 status rows + footer ≈ 8-10 button rows. On a
  laptop it trends **tall**; the single-button *Info* group wastes a whole row.
  Width (`300`) is fine. It also **omits 4 commands** (§2). **Tabs** would cap the
  height and make the grouping explicit.
- **About - a tall text wall.** ~17 left-aligned static lines in one column.
  Readable but dense; a 2-column key/value layout would roughly halve the height
  and read better. Not wide.

## 5. Icon strategy

Today: **no icons** (`icon=None` ×20), so commands are text-only in the menu,
Commander, and when dragged into palettes/layouts. Proposed (additive, optional,
**never required for behavior**):

- **Folder:** add `openrelativity_c4d/res/icons/` (new; the existing empty
  `c4d/descriptions/` stays for future `.res` description resources).
- **Set, phased:**
  1. one **master/brand** icon (`orc_logo.png`) - a relativity motif
     (e.g. light-cone / redshift→blueshift sweep);
  2. six **section** icons - `orc_setup.png`, `orc_preview.png`, `orc_octane.png`,
     `orc_export.png`, `orc_diagnostics.png`, `orc_help.png`;
  3. (later) **per-command** icons `orc_cmd_<short>.png`.
- **Sizes/format:** 32×32 base + 64×64 HiDPI, PNG with alpha (loaded via
  `c4d.bitmaps.BaseBitmap`). Flat, high-contrast, distinct silhouettes legible at
  32 px; a consistent redshift/blueshift accent palette for brand cohesion.
- **Safe loader:** a small `_load_icon(name)` helper that resolves a path relative
  to the plugin folder and returns a `BaseBitmap` or **`None`** on any failure, so
  a missing/corrupt file degrades to the current text-only behavior (mirrors the
  plugin's "never crash when X is absent" rule). Cache loaded bitmaps.
- **Where used:** pass the section/command bitmap as the `icon=` arg in
  registration; optionally show section icons as small headers in the Control
  Panel via `AddImage`. The Standard-renderer/Octane logic is untouched.

## 6. What must NOT change (guardrails)

- **Plugin IDs** stay exactly as defined in `ids.py`; the UI only **references**
  the existing `ID_ORC_*` constants (never new/literal IDs).
- **Command set & workflows** are preserved: all 20 commands keep their behavior,
  their `Execute`/`GetState`, and (recommended) their **menu names** - those names
  appear in `USER_GUIDE.md`, `QUICKSTART.md`, the test plans, and the Control
  Panel labels, so renaming is treated as a separate, doc-synced decision (§8).
- **Physics/math** (`core/`) and **Octane adapter** (`octane/`) behavior are out
  of scope - not touched.

## 7. Proposed section mapping

Six sections (as requested). Every command maps to exactly one **primary**
section; the Control Panel tabs and a grouped Extensions submenu would both be
driven from this single mapping so they cannot drift.

| Section | Commands (primary) |
|---|---|
| **Setup** | Create Relativity Controller · Setup Relativistic Camera · Setup Selected Relativistic Objects · Select Relativistic Objects · Create Test Scene |
| **Preview** | Apply Doppler Material Preview · Apply Searchlight Preview · Apply Relativity Material Preview · Apply All Previews · Create Lorentz Preview Copies · Remove Lorentz Preview Copies · Clear Material Preview |
| **Octane** | Octane Status · Apply Octane-Compatible Material Preview · Show AOV Plan |
| **Export** | Export Relativity Metadata JSON · Export Experimental OSL Camera |
| **Diagnostics** | Octane Diagnostics |
| **Help** | About |

Counts: Setup 5, Preview 7, Octane 3, Export 2, Diagnostics 1, Help 1 (= 19) +
the **Control Panel** launcher itself (20).

**Ambiguities / notes (resolve during design, not now):**
- *Octane vs Diagnostics.* All four Octane-related read/act commands (Status,
  Apply Octane Material, AOV Plan, Diagnostics) are coherent under **Octane**.
  *Octane Diagnostics* is the deep, developer-facing IDs/parameters dump, so it is
  filed under **Diagnostics** but should be **cross-linked** from the Octane tab.
  *Octane Status* and *Show AOV Plan* are read-only too; an alternative is to pool
  all read-only reports under Diagnostics. Recommended: keep the table above and
  cross-list rather than duplicate.
- *About* is **Help**, but its content is largely a **live status read-out**
  (controller/camera/objects/preview). A future Diagnostics tab could reuse that
  same status provider, letting About shrink to identity/links.
- *Control Panel* is a **launcher/host**, not a tab item - it opens the tabbed UI;
  keep it as a top-level menu entry.

## 8. Risks

1. **No Cinema 4D here to verify.** Every GeDialog/menu/icon change must be
   manually tested in C4D 2023+ (consistent with the repo's "C4D side is
   manual-tested only" reality). Layout reflow cannot be validated offline.
2. **Tab/layout reflow.** `TabGroupBegin`/group flags and DPI scaling can produce
   too-tall or clipped panels; needs in-app testing across at least one
   low-resolution layout.
3. **Menu renames break references.** Changing any menu string would desync
   `USER_GUIDE.md`, `QUICKSTART.md`, `TEST_PLAN_*`, and Control Panel labels (and
   users' muscle memory). Keep names stable; if a rename is wanted (e.g. the
   inconsistent "Apply Doppler **Material** Preview" vs "Apply Searchlight
   Preview"), do it as a separate, fully doc-synced change.
4. **Grouped Extensions submenu** (via a `C4DPL_BUILDMENU` `PluginMessage` hook)
   adds a global message handler - it must be **idempotent and guarded** so it
   never duplicates entries or disturbs other plugins' menus.
5. **Icon path/loading.** Files load relative to the plugin folder; missing or
   bad files must fall back to `icon=None` with no exception.
6. **Registry refactor must be behavior-neutral.** Collapsing the 20 register
   blocks into a data-driven loop must preserve the **exact** IDs, names, help
   text, command instances, and the per-command success/failure logging. Guard
   with `tools/audit_plugin_ids.py` and a "20 registrations, all unique" check.
7. **Control Panel coverage change.** Adding the 4 missing commands changes what
   the panel shows (a UX change, not a behavior change); verify each new button's
   `CallCommand` id resolves to the right `ids.*` constant.

## 9. Implementation plan

Staged, each step behavior-neutral and independently testable in Cinema 4D. **Not
started** - this audit is the only deliverable for now.

- **Step 0 - this audit.** (done: `docs/UI_UX_AUDIT.md`).
- **Step 1 - single command registry (no UX change).** Introduce one declarative
  table (`(id_const, menu_name, help, factory, section)` per command) in a new
  small module. Rewrite `register_all` to iterate it (removes ~300 lines of
  duplication) while emitting the identical names/help/IDs/logging. Verify with
  `audit_plugin_ids.py` + a count test. *Pure dedup; menu unchanged.*
- **Step 2 - shared status provider.** Extract the scene-status reads into one
  helper consumed by both About and the Control Panel (removes the §3 duplication;
  output strings unchanged).
- **Step 3 - Control Panel tabs.** Convert `_SECTIONS` to the six tabs from §7,
  **driven by the registry** so it auto-includes all 20 commands (fixing the §2
  gap); keep the status read-out on the first/overview tab; cap height via tabs.
- **Step 4 - grouped Extensions submenu.** Add a guarded `C4DPL_BUILDMENU` hook
  presenting Setup ▸ / Preview ▸ / Octane ▸ / Export ▸ / Diagnostics ▸ / Help ▸,
  referencing the same registry. (Commands stay individually registered.)
- **Step 5 - icons.** Add `res/icons/` + the safe loader; wire master + 6 section
  icons (then per-command) into registration and the panel; degrade to `None`.
- **Step 6 - About polish.** 2-column key/value layout using the shared status
  provider.
- **Cross-cutting.** Update `USER_GUIDE.md` / `QUICKSTART.md` (and screenshots),
  keep menu names stable, and run `tools/verify_repo.py` + `tools/audit_plugin_ids.py`
  after each step; add the new UI behaviors to `TEST_PLAN_C4D.md`.

---

*Sources audited:* `openrelativity_c4d/c4d/plugin_register.py`,
`openrelativity_c4d/c4d/commands.py`, `openrelativity_c4d/c4d/control_panel.py`,
`openrelativity_c4d/ids.py`, `openrelativity_c4d/constants.py`,
`openrelativity_c4d/bootstrap.py`, `openrelativity_c4d/c4d/descriptions/`.
