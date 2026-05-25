# Troubleshooting

Common issues with the OpenRelativity C4D plugin and how to diagnose them.

## First step: run UI Diagnostics

Inside Cinema 4D, run **Extensions > “OpenRelativity C4D / Diagnostics / UI
Diagnostics”** (or the **UI Diagnostics** button on the Control Panel's *Help*
tab). It opens a small, **copyable** report showing:

- plugin version, plugin root path, Cinema 4D version;
- every command's ID and whether it is **loaded** (`[OK]` / `[--]`);
- each icon: `loaded` / `found, not loaded` / `MISSING`;
- controller / camera / ORC-object / Octane status.

The same report is also written to the **Console** (*Script > Console* / *Window >
Console*). Copy it when asking for help.

Outside Cinema 4D you can run the offline auditors from the repo root:

```sh
python tools/audit_ui_assets.py     # icons exist, registry consistent, UI docs
python tools/audit_plugin_ids.py    # plugin IDs unique, no sample IDs
python tools/verify_repo.py         # files, no-c4d core, tests, docs
```

---

## Commands missing from the menu

The commands live under **Extensions** with the grouped label
**`OpenRelativity C4D / <Section> / <Command>`** (see
[`COMMAND_REFERENCE.md`](COMMAND_REFERENCE.md)). If some are missing:

- **Check the Console at startup.** Registration logs one line per command
  (`Registered '<name>' (id=…)` or `Failed to register …`). A failure usually
  means an **ID collision** with another plugin - see *plugin blocks another
  plugin* below.
- **Run UI Diagnostics** and look at *Commands loaded: M/N*; any `[--]` row is a
  command that did not register.
- **The plugin did not load at all.** Confirm the `openrelativity_c4d` folder and
  `openrelativity_c4d.pyp` are in a Cinema 4D **plugins** path, then restart. The
  Console prints `Loading OpenRelativity C4D …` when the `.pyp` is found.
- Cinema 4D does **not** create nested submenus from the `/` in the label - it is
  a flat, prefix-grouped list. That is expected, not a bug.

## Icons not showing

Icons are optional - **commands still work without them** (text-only buttons).
If icons are blank:

- **Run UI Diagnostics** → the *Icons* section. `MISSING` means the PNG was not
  found under `openrelativity_c4d/resources/icons/png/`; `found, not loaded` means
  the file exists but Cinema 4D's bitmap loader rejected it.
- **Regenerate** the icons: `python tools/generate_icons.py`, then
  `python tools/audit_ui_assets.py` to confirm every expected PNG exists.
- Make sure the `resources/icons/png/` folder shipped with the plugin (it is part
  of the package; see [`ICONS.md`](ICONS.md)).
- Icon loading is centralized and safe (`c4d/icon_loader.py`): a missing icon is
  logged at debug level and never blocks a command.

## The plugin blocks another plugin (or fails to load itself)

Cinema 4D loads only **one** plugin per ID. If installing this plugin makes
another stop loading (or vice versa), an **ID collides**.

- All IDs are centralized in `openrelativity_c4d/ids.py`, derived from a single
  **`ORC_ID_BASE`** (a temporary private prototype value).
- **Fix:** open `ids.py`, change `ORC_ID_BASE` to a different high number, save,
  and **restart Cinema 4D**. That relocates every ID at once.
- Verify uniqueness with `python tools/audit_plugin_ids.py`.
- Before public distribution, replace the prototype IDs with registered Plugin
  Café IDs (see [`DEVELOPER_NOTES.md`](DEVELOPER_NOTES.md) → “Plugin IDs”).

## Control Panel is too large / off-screen

The panel is tabbed to stay small (one section's buttons at a time).

- Drag the panel edge to resize, or **dock** it into a layout tab; Cinema 4D
  remembers the docked size.
- If it opens off-screen, reset via *Window > Customization > … layout*, or delete
  the saved layout for the dialog and reopen it.
- It is non-modal - keep it docked while you work. If it still feels tall, use the
  **Extensions** menu commands directly instead of the panel.

## Octane not detected

The plugin **never requires Octane** - everything works in Standard/Physical, and
Octane-tab commands report status or fall back to a Standard material.

- **Octane: Missing** in the status means no Octane integration was found. That is
  normal if Octane is not installed; previews still render in Standard/Physical.
- **Octane: Unknown** means detection could not run (rare) - treated as
  unavailable, which is safe.
- If Octane *is* installed but shows Missing: run **Octane / Status** and **Octane
  / Diagnostics** for what was detected; detection is by plugin **name** and a
  guarded `c4doctane` import (see [`OCTANE_INTEGRATION.md`](OCTANE_INTEGRATION.md)).
  Native Octane material/AOV support is still future work, so a fallback to the
  Standard `ORC_Preview` material is expected even when Octane is present.

---

If a problem persists, copy the **UI Diagnostics** report and the **Console** log
and include them in your report (project page in
[`USER_GUIDE.md`](USER_GUIDE.md)).
