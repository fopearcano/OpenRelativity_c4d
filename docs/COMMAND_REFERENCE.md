# Command Reference

Every OpenRelativity C4D command, its **menu label**, **Control Panel** button
label, source class, plugin-ID constant, and what it does. This is the canonical
list - other docs may still use the older command phrasing; use the
[name cross-walk](#legacy-name-cross-walk) below to map them.

## Naming convention

Menu labels are built by `constants.command_name(section, leaf)` as:

```
OpenRelativity C4D / <Section> / <Leaf>
```

so every command shares the **`OpenRelativity C4D`** prefix (they cluster together
in the *Extensions* menu and the Commander) and the `/ Section /` path reads as a
group. **Note:** Cinema 4D does not turn the `/` into real nested submenus from a
command name - this is a readable, prefix-grouped *label* only. True nested
submenus would require a `C4DPL_BUILDMENU` hook (future work). Switching to a
plain-prefix style (`OpenRelativity C4D: Section - Leaf`) is a one-line change in
`constants.command_name`.

Plugin IDs are unchanged; only labels and grouping changed (no behavior change).
**Generated scene content keeps its `ORC_` prefix** (e.g.
`ORC_Relativity_Controller`, `ORC_Preview_<name>`, `ORC_LorentzPreview_<name>`).

## Commands by section

Legend: **Destructive?** = "yes" means the command **deletes ORC-generated**
content (never your original objects/materials).

### Setup

| Menu label | Panel button | Class | ID constant | Destructive? |
|---|---|---|---|:--:|
| OpenRelativity C4D / Setup / Create Controller | Create Controller | `CreateControllerCommand` | `ID_ORC_CREATE_CONTROLLER_COMMAND` | no |
| OpenRelativity C4D / Setup / Setup Camera | Setup Camera | `SetupCameraCommand` | `ID_ORC_SETUP_CAMERA_COMMAND` | no |
| OpenRelativity C4D / Setup / Setup Selected Objects | Setup Selected Objects | `SetupObjectsCommand` | `ID_ORC_SETUP_OBJECTS_COMMAND` | no |
| OpenRelativity C4D / Setup / Select Objects | Select Objects | `SelectObjectsCommand` | `ID_ORC_SELECT_OBJECTS_COMMAND` | no |

- **Create Controller** - create the `ORC_Relativity_Controller` Null (or select
  the existing one).
- **Setup Camera** - configure the selected camera, or create one, as the
  relativistic observer.
- **Setup Selected Objects** - add relativistic User Data to the selected objects.
- **Select Objects** - select every object that has relativistic User Data.

### Scene

| Menu label | Panel button | Class | ID constant | Destructive? |
|---|---|---|---|:--:|
| OpenRelativity C4D / Scene / Create Test Scene | Create Test Scene | `CreateTestSceneCommand` | `ID_ORC_CREATE_TEST_SCENE_COMMAND` | no |

- **Create Test Scene** - build a demo scene: controller, relativistic camera,
  four test objects (approaching / receding / lateral / static) and a light.

### Preview

| Menu label | Panel button | Class | ID constant | Destructive? |
|---|---|---|---|:--:|
| OpenRelativity C4D / Preview / Apply Doppler | Apply Doppler | `ApplyDopplerPreviewCommand` | `ID_ORC_APPLY_DOPPLER_PREVIEW_COMMAND` | no |
| OpenRelativity C4D / Preview / Apply Searchlight | Apply Searchlight | `ApplySearchlightPreviewCommand` | `ID_ORC_APPLY_SEARCHLIGHT_PREVIEW_COMMAND` | no |
| OpenRelativity C4D / Preview / Apply All Materials | Apply All Materials | `ApplyRelativityMaterialPreviewCommand` | `ID_ORC_APPLY_RELATIVITY_PREVIEW_COMMAND` | no |
| OpenRelativity C4D / Preview / Apply All | Apply All (+ Lorentz) | `ApplyAllPreviewsCommand` | `ID_ORC_APPLY_ALL_PREVIEWS_COMMAND` | no |
| OpenRelativity C4D / Preview / Create Lorentz Copies | Create Lorentz Copies | `CreateLorentzPreviewCommand` | `ID_ORC_CREATE_LORENTZ_PREVIEWS_COMMAND` | no |
| OpenRelativity C4D / Preview / Remove Lorentz Copies | Remove Lorentz Copies | `RemoveLorentzPreviewCommand` | `ID_ORC_REMOVE_LORENTZ_PREVIEWS_COMMAND` | **yes** |
| OpenRelativity C4D / Preview / Clear Generated Preview Materials | Clear Generated Materials | `ClearMaterialPreviewCommand` | `ID_ORC_CLEAR_PREVIEW_COMMAND` | **yes** |

- **Apply Doppler** / **Apply Searchlight** - apply one approximate material
  effect; **Apply All Materials** applies both (Doppler tint + searchlight
  brightness) on the shared `ORC_Preview_<name>` material.
- **Apply All** - the broadest one-click: applies the material preview **and**
  creates the Lorentz preview copies.
- **Create Lorentz Copies** - non-destructive contracted `ORC_LorentzPreview_<name>`
  duplicates.
- **Remove Lorentz Copies** *(destructive)* - **delete** the ORC Lorentz copies and
  restore the originals' visibility. Originals are not modified.
- **Clear Generated Preview Materials** *(destructive)* - **delete** the ORC
  preview materials and tags. Your original materials are left untouched.

### Octane *(works with Octane absent)*

| Menu label | Panel button | Class | ID constant | Destructive? |
|---|---|---|---|:--:|
| OpenRelativity C4D / Octane / Status | Status | `OctaneStatusCommand` | `ID_ORC_OCTANE_STATUS_COMMAND` | no |
| OpenRelativity C4D / Octane / Apply Compatible Preview | Apply Compatible Preview | `ApplyOctaneCompatibleMaterialPreviewCommand` | `ID_ORC_APPLY_OCTANE_MATERIAL_COMMAND` | no |
| OpenRelativity C4D / Octane / Show AOV Plan | Show AOV Plan | `ShowAOVPlanCommand` | `ID_ORC_SHOW_AOV_PLAN_COMMAND` | no |
| OpenRelativity C4D / Octane / Diagnostics | Octane Diagnostics | `OctaneDiagnosticsCommand` | `ID_ORC_OCTANE_DIAGNOSTICS_COMMAND` | no |

- **Status** / **Diagnostics** / **Show AOV Plan** - read-only reports; they change
  nothing in the scene or Octane.
- **Apply Compatible Preview** - apply the combined preview via a native Octane
  material when supported, otherwise via the Standard-material fallback.

### Export

| Menu label | Panel button | Class | ID constant | Destructive? |
|---|---|---|---|:--:|
| OpenRelativity C4D / Export / Metadata JSON | Metadata JSON | `ExportMetadataCommand` | `ID_ORC_EXPORT_METADATA_COMMAND` | no |

- **Metadata JSON** - export controller/camera/object relativity metadata to a JSON
  file you choose (writes only the file you pick).

### Experimental

| Menu label | Panel button | Class | ID constant | Destructive? |
|---|---|---|---|:--:|
| OpenRelativity C4D / Experimental / Export OSL Camera | Export OSL Camera | `ExportOSLCameraCommand` | `ID_ORC_EXPORT_OSL_CAMERA_COMMAND` | no |

- **Export OSL Camera** - write the experimental (placeholder) OSL camera shader to
  a file. Not wired into Octane; see [`OSL_CAMERA_EXPERIMENTS.md`](OSL_CAMERA_EXPERIMENTS.md).

### Diagnostics

| Menu label | Panel button | Class | ID constant | Destructive? |
|---|---|---|---|:--:|
| OpenRelativity C4D / Diagnostics / UI Diagnostics | UI Diagnostics | `UIDiagnosticsCommand` | `ID_ORC_UI_DIAGNOSTICS_COMMAND` | no |

- **UI Diagnostics** - open a small, copyable report (also written to the console)
  for debugging UI / icon / command-registration issues: plugin version + root
  path, Cinema 4D version, each command's ID and load state, each icon's
  found/loaded state, and the scene status. Read-only; see
  [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

### Help

| Menu label | Panel button | Class | ID constant | Destructive? |
|---|---|---|---|:--:|
| OpenRelativity C4D / Help / Control Panel | *(opens the panel)* | `ControlPanelCommand` | `ID_ORC_CONTROL_PANEL_COMMAND` | no |
| OpenRelativity C4D / Help / About | About | `AboutCommand` | `ID_ORC_ABOUT_COMMAND` | no |

- **Control Panel** - open the compact, tabbed launcher (see
  [`USER_GUIDE.md`](USER_GUIDE.md) §2).
- **About** - show version, target/running Cinema 4D, Octane status, and
  controller/camera/object/preview state.

The Control Panel mirrors these commands across its tabs (including **UI
Diagnostics** on the *Help* tab). It also offers one panel-only helper that is not
a menu command: **Open Docs Folder**.

## Legacy name cross-walk

Older docs and tutorials may use the previous `OpenRelativity C4D: <name>` labels.
Map them to the current grouped labels:

| Previous label (`OpenRelativity C4D: …`) | Current label |
|---|---|
| About | OpenRelativity C4D / Help / About |
| Control Panel | OpenRelativity C4D / Help / Control Panel |
| Create Relativity Controller | OpenRelativity C4D / Setup / Create Controller |
| Setup Relativistic Camera | OpenRelativity C4D / Setup / Setup Camera |
| Setup Selected Relativistic Objects | OpenRelativity C4D / Setup / Setup Selected Objects |
| Select Relativistic Objects | OpenRelativity C4D / Setup / Select Objects |
| Create Test Scene | OpenRelativity C4D / Scene / Create Test Scene |
| Apply Doppler Material Preview | OpenRelativity C4D / Preview / Apply Doppler |
| Apply Searchlight Preview | OpenRelativity C4D / Preview / Apply Searchlight |
| Apply Relativity Material Preview | OpenRelativity C4D / Preview / Apply All Materials |
| Apply All Previews | OpenRelativity C4D / Preview / Apply All |
| Create Lorentz Preview Copies | OpenRelativity C4D / Preview / Create Lorentz Copies |
| Remove Lorentz Preview Copies | OpenRelativity C4D / Preview / Remove Lorentz Copies |
| Clear Material Preview | OpenRelativity C4D / Preview / Clear Generated Preview Materials |
| Octane Status | OpenRelativity C4D / Octane / Status |
| Octane Diagnostics | OpenRelativity C4D / Octane / Diagnostics |
| Apply Octane-Compatible Material Preview | OpenRelativity C4D / Octane / Apply Compatible Preview |
| Show AOV Plan | OpenRelativity C4D / Octane / Show AOV Plan |
| Export Relativity Metadata JSON | OpenRelativity C4D / Export / Metadata JSON |
| Export Experimental OSL Camera | OpenRelativity C4D / Experimental / Export OSL Camera |

Plugin IDs (`ids.py`) and command behavior are unchanged by the relabeling.
