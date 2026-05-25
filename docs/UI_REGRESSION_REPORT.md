# UI Regression Report

Final UI regression audit of the OpenRelativity C4D plugin. **Audit only** - no
features added, no plugin IDs changed, no physics/math or Octane behavior altered.

Run from the repo root:

```sh
python tools/audit_plugin_ids.py
python tools/audit_ui_assets.py
python tools/verify_repo.py
```

## Automated results (this environment, no Cinema 4D)

| Tool / check | Result |
|---|---|
| `python -c "import openrelativity_c4d"` | OK (package is import-safe, v0.1.0) |
| `python -m compileall openrelativity_c4d openrelativity_c4d.pyp tools` | OK - no syntax errors |
| `tools/audit_plugin_ids.py` | **PASS** - 28 ORC IDs unique; none are sample/test IDs; all registrations use `ids.*` constants; no stray sample literals |
| `tools/audit_ui_assets.py` | **PASS** - all expected icons exist; command↔icon registry matches `ids.py`; source icon refs valid; UI docs present |
| `tools/verify_repo.py` | **PASS** - 39 expected files; entry point wired; no `c4d` in core/tests; field schema valid; **147 pure tests, 0 failures**; 30 docs |

> The `ERROR … Failed to export …` / traceback lines printed by `verify_repo.py`
> are **expected**: two tests deliberately exercise the export error paths
> (writing to a non-existent directory). The suite reports 0 failures.

## Checklist

Legend: **PASS** = verified offline (static analysis / pure tests);
**MANUAL** = must be confirmed inside Cinema 4D, with the static evidence that
makes it expected to pass.

| # | Check | Status | Evidence |
|--:|---|---|---|
| 1 | Plugin still imports | **PASS** | `import openrelativity_c4d` succeeds in plain Python; `compileall` clean for every module + `openrelativity_c4d.pyp`. Full in-host load is **MANUAL**, but `bootstrap.register()` guards the `c4d` import and degrades gracefully. |
| 2 | All commands still register | **PASS (static)** | 21 `RegisterCommandPlugin(...)` calls in `plugin_register.py`; every `id=` is an `ids.ID_ORC_*` constant; all 21 unique; count matches the `ui_assets` registry (21). Per-command registration *success* is logged at startup → **MANUAL** confirm. |
| 3 | Command IDs are centralized constants | **PASS** | 0 raw numeric `id=` in registration; every `id=` constant resolves in `ids.py`; `audit_plugin_ids.py` PASS. |
| 4 | No duplicate button IDs in dialogs | **PASS** | Control Panel fixed widget IDs `{1000–1005, 1010–1016, 1020, 1021, 1023}` are unique and all `< _GADGET_BASE (2000)`, so dynamically-assigned command gadgets (≥2000) cannot collide. UI Diagnostics dialog uses `{2000, 2001}` (unique). About dialog uses base `2000`+sequential offsets, group `1000`, and the `DLG_OK` constant (no overlap). Non-interactive labels use id `0` by convention. |
| 5 | Control Panel opens | **MANUAL** | `ControlPanelCommand.Execute` opens an async dialog with a constant `pluginid`; layout compiles. Opening/docking is a runtime/visual check in C4D. |
| 6 | Dialog compact, not absurdly tall | **MANUAL** | Tabs show one section at a time (≤7 button rows), status area is ~3 short rows, `defaulth=0` (auto), `defaultw=340`. Final size is visual → confirm in C4D. |
| 7 | Missing icons don't block registration | **PASS** | `icon_loader.safe_icon(<missing>)` returns `None` and never raises; registration passes that to `RegisterCommandPlugin(icon=…)`, so a missing/unreadable icon falls back to the prior `icon=None` behavior. Covered by `tests/test_icon_loader.py`. |
| 8 | Octane absence doesn't block the UI | **PASS** | `detection.detect_octane_available()` → `False` without raising; `ui_status` Octane token → `Unknown`/`Missing`; the status read and panel build never require Octane. Covered by `tests/test_octane_detection.py`, `test_ui_status.py`. |
| 9 | Commands run from menu **and** Control Panel | **PASS (static)** | Every registered command (except the launcher itself) is reachable from a panel button; every panel button id is a registered `ids.ID_ORC_*_COMMAND`; buttons call `c4d.CallCommand(<same id>)`, so both paths invoke the identical command. Actual click-through is **MANUAL**. |
| 10 | Repeated command execution is safe | **PASS (by design)** | Commands are non-destructive/idempotent (reuse the `ORC_Preview_<name>` slot; Clear/Remove handle "nothing to do"; guarded for no-doc/no-selection - established in the earlier audit & refactor). The panel's `Command()` wraps `CallCommand` in `try/except` (logs once, shows a short error, keeps the dialog alive). Repeated-run *visual* behavior is **MANUAL**. |
| 11 | `docs/USER_GUIDE.md` matches the current UI | **PASS** | No stale `OpenRelativity C4D:` (colon) labels remain; 7 grouped `OpenRelativity C4D / …` labels present; the guide's tab names equal the panel's `_begin_tab` titles (Setup/Preview/Octane/Export/Help); sampled button labels (Apply Doppler, Clear Generated Materials, Create Lorentz Copies, UI Diagnostics, Refresh Status) all appear. |

## What remains to verify manually inside Cinema 4D

These cannot be exercised without a running Cinema 4D (the repo is built/tested in
a host-free environment) and are the standard manual pass:

1. The plugin loads with no errors in the Console; the startup log shows
   `Command icons: N loaded, M missing.` and a `Registered …` line per command.
2. The Extensions menu shows the grouped `OpenRelativity C4D / <Section> / …`
   entries and each command runs.
3. **Control Panel** opens, is compact (no off-screen / excessive height), tabs
   switch, icons display (or degrade to text), and the status read-out and
   **Refresh Status** update after actions.
4. **UI Diagnostics** opens a small, copyable report; **About** opens.
5. Run each command from the menu and from the panel; re-run previews / Clear /
   Remove repeatedly and confirm no errors and correct counts.
6. With Octane installed and with it absent, confirm the UI opens and Octane
   commands report status / fall back safely.

See [`TEST_PLAN_C4D.md`](TEST_PLAN_C4D.md), [`TEST_PLAN_OCTANE.md`](TEST_PLAN_OCTANE.md),
and [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) (the **UI Diagnostics** command
produces a copyable report for exactly this).

## Known limitations

- **Host-free verification.** Everything `c4d`-bound (GeDialog rendering, menu
  population, `BaseBitmap` icon loading, `CallCommand`) is verified by static
  analysis + import-safety + pure tests, **not** by running Cinema 4D. The items
  marked MANUAL above remain the authoritative visual/runtime confirmation.
- **Prototype plugin IDs.** IDs are temporary `ORC_ID_BASE + n` values, not
  registered Plugin Café IDs; replace before public release (see
  [`DEVELOPER_NOTES.md`](DEVELOPER_NOTES.md) → "Plugin IDs").
- **Menu grouping is by label, not true submenus.** Cinema 4D does not turn the
  `/` in a command name into nested submenus; the grouped labels are a flat,
  prefix-clustered list (a `C4DPL_BUILDMENU` hook for real submenus is future
  work).
- **Prototype icons.** Programmer-art flat icons; replaceable without code changes
  (see [`ICONS.md`](ICONS.md)). Registry↔icon↔docs consistency is guarded by
  `tools/audit_ui_assets.py`.
- **Scope.** This audit changed no code behavior; it only added this report.
