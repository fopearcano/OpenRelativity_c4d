# User Guide — OpenRelativity for Cinema 4D

A short, practical guide to using the plugin. For the design and scope, see
[`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) and [`ROADMAP.md`](ROADMAP.md).

> **In a hurry?** [`QUICKSTART.md`](QUICKSTART.md) gets you from install to a
> rendered relativistic preview in about 5 minutes via *Create Test Scene* +
> *Apply All Previews*. This guide is the full reference.

> **Phase 1 status.** You can set up a **Relativity Controller**, a relativistic
> **camera**, and per-**object** settings, then preview the **Doppler**,
> **searchlight**, and **Lorentz** effects in the Standard/Physical renderer.
> The previews are artistic approximations; Octane output and true apparent
> geometry (Terrell rotation) are later phases.

## 1. Install the plugin

See the [README](../README.md#installation): copy `openrelativity_c4d.pyp` and
the `openrelativity_c4d/` package into a folder inside your Cinema 4D user
**plugins** folder, then restart Cinema 4D. Octane is **not** required.

## 2. The Control Panel (recommended entry point)

For everyday use, open the one-stop panel: **Extensions > “OpenRelativity C4D:
Control Panel”**. It is a small, dockable window with a button for every command
plus a live status read-out, so you rarely need the Extensions menu directly.

**Status** (updates after each action; press **Refresh** anytime):

- **Controller** - `found` / `MISSING`
- **Camera** - the relativistic camera's name / `MISSING`
- **ORC objects** - how many relativistic objects exist
- **Octane** - `detected` / `not detected` / `unknown`

**Buttons**, grouped to stay compact:

- *Scene setup*: Create Relativity Controller, Setup Relativistic Camera, Setup
  Selected Relativistic Objects, Create Test Scene.
- *Material preview*: Apply Doppler Material Preview, Apply Searchlight Preview,
  Apply Relativity Material Preview (both), Clear Material Preview.
- *Lorentz geometry*: Create Lorentz Preview Copies, Remove Lorentz Preview Copies.
- *Octane / export*: Octane Status, Show AOV Plan, Export Relativity Metadata JSON.
- *Info*: About.

Button labels match the menu command names exactly.

Each button runs the matching command described in the rest of this guide. The
panel is **non-modal** - keep it open while you work, and it stays narrow/short
enough for laptop screens. A typical first run: *Create Test Scene* → *Apply All
Material Previews* → render (see [`QUICKSTART.md`](QUICKSTART.md)).

## 3. Create the Relativity Controller

1. Open the **Extensions** menu.
2. Choose **“OpenRelativity C4D: Create Relativity Controller”**.
3. The plugin either:
   - creates a Null named **`ORC_Relativity_Controller`**, selects it, and
     confirms with a dialog; or
   - if one already exists, simply **selects** the existing controller and tells
     you so (only one controller per scene is intended).

You can confirm a controller exists at any time via **Extensions > “OpenRelativity
C4D: About”**, which shows `Controller: present` or `Controller: not in scene`.

## 4. Adjust the settings

Select `ORC_Relativity_Controller` and open the **Attribute Manager**. Its
**User Data** is organised into three sections:

### Relativity

| Field | Type | Default | Meaning |
|---|---|---|---|
| **Enabled** | Bool | On | Master switch for the controller. |
| **Artificial Speed of Light** | Float | `1000.0` | The speed of light `c` in scene units/second. Lower it to make relativistic effects visible at ordinary scene speeds (as OpenRelativity does). |
| **Global Beta Override** | Percent | `0%` | A global `v/c` used for previewing, `0–99.9%`. `0%` means "no override" (per-object velocities will be used in later phases). |

### Visual Effects

| Field | Type | Default | Meaning |
|---|---|---|---|
| **Doppler Strength** | Percent | `100%` | Art-directable blend of the Doppler color shift (`0%` = off). |
| **Searchlight Strength** | Percent | `100%` | Art-directable blend of the beaming/searchlight intensity. |
| **Lorentz Deformation Strength** | Percent | `100%` | Art-directable blend of the geometric length contraction. |
| **Preview Mode** | Cycle | `Doppler + Searchlight` | Which previews to show: `Off`, `Doppler`, `Searchlight`, or `Doppler + Searchlight`. |
| **Hide Originals (Lorentz Preview)** | Bool | On | When the Lorentz preview copies are created, hide the originals (restored on removal). |

### Integration

| Field | Type | Default | Meaning |
|---|---|---|---|
| **Octane Adapter Enabled** | Bool | Off | When on (and Octane is installed), mirror results onto Octane materials/camera. Octane is **optional**; leaving it off changes nothing. |
| **Bake Mode Enabled** | Bool | Off | When on, effects will be baked per frame (for rendering) instead of shown as a live preview. |

> The strength and beta fields use a **percent** display: the stored value is a
> fraction (`0.0–1.0`), shown as `0–100%`. These map directly to the `strength`
> and `beta` parameters of the math core
> (`openrelativity_c4d.core`).

## 5. Set up a Relativistic Camera

The observer (the point of view that "sees" the relativistic effects) is a
camera carrying its own User Data.

1. *(Optional)* select a camera. If a camera is selected it is used; if none is
   selected, a new camera named **`ORC_Relativistic_Camera`** is created.
2. Open **Extensions > “OpenRelativity C4D: Setup Relativistic Camera”**.
3. The plugin adds the camera's User Data (or just selects it, if it already has
   it). The **About** dialog's `Camera:` line then shows the camera's name.

Select the camera and open the **Attribute Manager** to edit its **User Data**:

### Relativistic Camera

| Field | Type | Default | Meaning |
|---|---|---|---|
| **ORC Enabled** | Bool | On | Whether this camera participates in relativity. |
| **Observer Beta** | Percent | `0%` | The observer's speed as a fraction of `c`, set directly. `0%` means "derive from Observer Velocity instead". |
| **Observer Velocity** | Vector | `(0, 0, 0)` | Observer velocity in scene units/second. Its magnitude ÷ `c` gives beta when *Observer Beta* is `0`; its direction is used for direction-dependent effects later. |
| **Use Controller Global Beta** | Bool | On | When on **and** the Scene Controller's *Global Beta Override* is > 0, that global value is used instead of this camera's own beta. |

### Preview

| Field | Type | Default | Meaning |
|---|---|---|---|
| **Doppler Preview Enabled** | Bool | On | Show the Doppler color shift for this observer (when previews exist). |
| **Searchlight Preview Enabled** | Bool | On | Show the searchlight/beaming intensity. |
| **Aberration Preview Enabled** | Bool | Off | *Placeholder* - apparent-position aberration is not implemented yet. |

### Integration (Experimental)

| Field | Type | Default | Meaning |
|---|---|---|---|
| **Octane Camera Sync Enabled** | Bool | Off | *Stub* - will mirror the observer onto an Octane camera (Phase 3). Octane is **not** required. |
| **OSL Camera Experimental Enabled** | Bool | Off | *Placeholder* - no OSL shader is generated yet. |

**How the effective beta is chosen** (`compute_observer_beta`):

1. Controller's *Global Beta Override* — if *Use Controller Global Beta* is on
   and that override is > 0.
2. Else the camera's own *Observer Beta* — if > 0.
3. Else `|Observer Velocity| ÷ c`, where `c` is the controller's *Artificial
   Speed of Light* (or the core default if there is no controller).

The result is always clamped to ≤ `99.9%` of `c`.

## 6. Set up relativistic objects

Any scene object can be marked as relativistic by giving it its own User Data.

1. Select one or more objects.
2. Open **Extensions > “OpenRelativity C4D: Setup Selected Relativistic
   Objects”**. Each eligible object gets the User Data below. The Relativity
   Controller and any cameras in the selection are **skipped**, and objects that
   already have the data are left unchanged.
3. To gather them again later, run **Extensions > “OpenRelativity C4D: Select
   Relativistic Objects”**, which selects every object that has the data. The
   **About** dialog's `Objects:` line shows how many exist.

Select an object and open the **Attribute Manager** to edit its **User Data**:

### Relativistic Object

| Field | Type | Default | Meaning |
|---|---|---|---|
| **ORC Object Enabled** | Bool | On | Whether this object participates in relativity. |
| **Object Beta** | Percent | `0%` | The object's speed as a fraction of `c`, set directly. `0%` means "derive from the velocity below". |
| **Velocity X / Y / Z** | Float ×3 | `0` | The object's velocity vector in scene units/second (three separate fields). |
| **Use Camera Relative Direction** | Bool | On | When on, the line-of-sight direction for Doppler/searchlight is computed relative to the active relativistic camera. |

### Material Preview

| Field | Type | Default | Meaning |
|---|---|---|---|
| **Doppler Material Preview** | Bool | On | Show this object's Doppler color shift (when previews exist). |
| **Searchlight Material Preview** | Bool | On | Show this object's searchlight/beaming brightness. |
| **Lorentz Deformation Preview** | Bool | On | Show this object's length contraction. |

### Integration

| Field | Type | Default | Meaning |
|---|---|---|---|
| **Bake Eligible** | Bool | Off | Mark this object to be included when baking effects for rendering. |
| **Octane Material Sync Enabled** | Bool | Off | *Stub* - will mirror the Doppler/searchlight result onto the object's Octane material (Phase 3). Octane is **not** required. |

## 7. Preview the relativistic effects

The first **visible** effects. After setting up a controller, camera, and some
objects with a beta/velocity, use the *Extensions* menu:

- **Apply Doppler Material Preview** — tints each object blue (approaching) or
  red (receding).
- **Apply Searchlight Preview** — brightens (approaching) or dims (receding) each
  object, with a little emission glow when strongly approaching.
- **Apply Relativity Material Preview** — both at once (the usual choice).
- **Clear Material Preview** — removes them all.

These material commands generate one Standard material per object
(`ORC_Preview_<name>`), applied non-destructively (a layered Texture tag; your
materials are untouched), and render in Standard/Physical. For **geometry**:

- **Create Lorentz Preview Copies** — makes a contracted duplicate
  (`ORC_LorentzPreview_<name>`) of each object, shortened along its velocity
  axis, and hides the original (restored on removal).
- **Remove Lorentz Preview Copies** — deletes the copies and restores originals.

These are **artistic approximations, not spectral/radiometric rendering**, and
the Lorentz copy is an **axis-aligned length contraction only** (no Terrell
rotation/apparent geometry). See [`DOPPLER_PREVIEW.md`](DOPPLER_PREVIEW.md),
[`SEARCHLIGHT_PREVIEW.md`](SEARCHLIGHT_PREVIEW.md), and
[`LORENTZ_PREVIEW.md`](LORENTZ_PREVIEW.md) for details and limitations.

## 8. What the fields do *not* do yet

The **Doppler/searchlight material previews** and an **axis-aligned Lorentz
geometry preview** are implemented. The following are still intentionally **not
implemented yet** (see [`ROADMAP.md`](ROADMAP.md)):

- **Terrell rotation / true apparent geometry** (the Lorentz preview is a simple
  axis-aligned contraction only).
- **Octane** output. The plugin can *detect* Octane (**Octane Status**), run
  **Apply Octane-Compatible Material Preview** (currently falls back to the
  Standard preview and reports it), and **Show AOV Plan** (the desired
  compositing passes; manual setup for now). Native Octane material/AOV creation
  isn't implemented yet. **Export Experimental OSL Camera** writes a placeholder
  OSL shader (experimental, not wired into Octane). See
  [`OCTANE_INTEGRATION.md`](OCTANE_INTEGRATION.md),
  [`AOV_PIPELINE.md`](AOV_PIPELINE.md), and
  [`OSL_CAMERA_EXPERIMENTS.md`](OSL_CAMERA_EXPERIMENTS.md).
- **Bake** workflow.

Changing the values now is safe and will be honored once those features land.
Placeholder/stub fields (no effect yet): the camera's *Aberration*, *Octane
Camera Sync*, and *OSL*; and each object's *Bake Eligible* and *Octane Material
Sync*. No OSL is generated and no Octane material/tag is touched.

**Exporting metadata.** *Extensions > “OpenRelativity C4D: Export Relativity
Metadata JSON”* writes the current frame's controller/camera/object settings,
velocities, betas, and computed Doppler/searchlight factors to a JSON file for
compositing/debugging/reproducibility - schema in
[`METADATA_SCHEMA.md`](METADATA_SCHEMA.md).

## 9. For developers

Read and write values by **field name** (no hard-coded IDs). Controller, camera,
and objects share the same accessor style:

```python
from openrelativity_c4d.c4d import scene_controller, camera_tools, object_tools

doc = c4d.documents.GetActiveDocument()

controller = scene_controller.find_controller(doc)
c_value = scene_controller.get_value(controller, scene_controller.FIELD_SPEED_OF_LIGHT)
scene_controller.set_value(controller, scene_controller.FIELD_DOPPLER_STRENGTH, 0.5)

camera = camera_tools.find_relativistic_camera(doc)
beta = camera_tools.compute_observer_beta(camera, controller)  # effective v/c

for obj in object_tools.collect_orc_objects(doc):
    settings = object_tools.read_orc_object_settings(obj)   # dict of every field
    vx, vy, vz = object_tools.get_object_velocity(obj)      # (x, y, z) tuple
```

Field-name constants, defaults, and creation logic live in
`openrelativity_c4d/c4d/scene_controller.py`,
`openrelativity_c4d/c4d/camera_tools.py`, and
`openrelativity_c4d/c4d/object_tools.py`; the shared User Data plumbing is in
`openrelativity_c4d/c4d/userdata.py`.
