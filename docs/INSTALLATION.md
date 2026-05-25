# Installation & Testing

How to install OpenRelativity_c4d into Cinema 4D 2023+, run the pure-Python tests
outside Cinema 4D, and where the limits are.

## 1. Install into Cinema 4D 2023+

The plugin is a folder containing the entry point (`openrelativity_c4d.pyp`) and
the `openrelativity_c4d/` package, placed in Cinema 4D's user **plugins** folder.

**Get the folder** either way:

- **From a built zip** - run `python tools/make_plugin_zip.py` to produce
  `build/OpenRelativity_c4d_v<version>.zip`. Unzip it; it contains a single
  `OpenRelativity_c4d/` folder.
- **Straight from the repo** - use the repository folder itself (Cinema 4D only
  executes the `.pyp`; the extra files are harmless).

**Install:**

1. In Cinema 4D, open *Edit > Preferences* and click **Open Preferences
   Folder…**. The `plugins` sub-folder there is your user plugins folder.
2. Copy the `OpenRelativity_c4d/` folder into that `plugins` folder, so you have:

   ```
   <C4D user folder>/plugins/OpenRelativity_c4d/
   ├── openrelativity_c4d.pyp
   └── openrelativity_c4d/        (the package)
   ```

3. **Restart Cinema 4D.**
4. Open the **Extensions** menu and run **“OpenRelativity C4D: Control Panel”**
   (or **“About”**). The Control Panel is the recommended way to drive the plugin
   - see [`USER_GUIDE.md`](USER_GUIDE.md) and the 5-minute
   [`QUICKSTART.md`](QUICKSTART.md).

If nothing appears, open *Extensions > Console* and look for `[OpenRelativity
C4D]` log lines.

**Requirements:** Cinema 4D 2023 or newer (uses its bundled Python 3 runtime) and
**no external Python packages**.

## 2. Run the pure-Python tests (outside Cinema 4D)

The physics core (`openrelativity_c4d/core`) and the import-safe Octane/export
helpers can be tested with a plain Python 3 interpreter - **no Cinema 4D needed**.
From the repository root:

```
python -m unittest                 # discover & run all pure tests
python tools/run_core_tests.py     # same, verbose
python tools/verify_repo.py        # structure + no-c4d + tests + docs + entrypoint
```

`verify_repo.py` is the one-shot health check (exits non-zero on any failure) and
is suitable for CI or a pre-commit hook.

## 3. Cinema 4D plugin testing must happen inside Cinema 4D

Everything under `openrelativity_c4d/c4d/` (commands, dialogs, tags-as-User-Data,
material/geometry previews) calls Cinema 4D's `c4d` module and **cannot be unit
tested outside Cinema 4D**. Those parts are verified **manually inside Cinema 4D**
(load the plugin, run the commands, render). Only the renderer-agnostic math and
the import-safe helpers are automatically tested. When a change touches the
`c4d/` layer, test it in Cinema 4D 2023+.

## 4. Octane is optional (adapter-level only, for now)

The plugin **does not require Octane** and imports/runs fully without it. Octane
support is isolated in `openrelativity_c4d/octane/` and is currently
**adapter-level**: detection/status, a material adapter that **falls back to
Standard materials**, an AOV *plan* (manual setup), and an **experimental,
not-wired** OSL camera generator. Native Octane material/AOV creation is not
implemented yet. See [`OCTANE_INTEGRATION.md`](OCTANE_INTEGRATION.md),
[`AOV_PIPELINE.md`](AOV_PIPELINE.md), and
[`OSL_CAMERA_EXPERIMENTS.md`](OSL_CAMERA_EXPERIMENTS.md). Render previews with the
**Standard/Physical** renderers.

## 5. Plugin IDs must be replaced before public distribution

The plugin IDs in `openrelativity_c4d/ids.py` are **development placeholders**.
The early ones use Maxon's `1000001–1000010` test range and the later ones go
**past** it, so they can collide with other plugins. **Before distributing the
plugin publicly**, obtain unique IDs (free) from the Maxon Plugin Café /
developer portal (https://plugincafe.maxon.net/, https://developers.maxon.net/)
and replace every value in `ids.py`. See the warnings in that file and
[`DEVELOPER_NOTES.md`](DEVELOPER_NOTES.md).
