# User Guide — OpenRelativity for Cinema 4D

A short, practical guide to using the plugin. For the design and scope, see
[`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) and [`ROADMAP.md`](ROADMAP.md).

> **Phase 1 status.** Today the plugin lets you create and configure a
> **Relativity Controller** that stores all the relativistic settings for a
> scene. The visual effects those settings will drive (Lorentz deformation,
> Doppler recolor, searchlight beaming, Octane output) arrive in later phases —
> this step establishes the data model and the artist workflow.

## 1. Install the plugin

See the [README](../README.md#installation): copy `openrelativity_c4d.pyp` and
the `openrelativity_c4d/` package into a folder inside your Cinema 4D user
**plugins** folder, then restart Cinema 4D. Octane is **not** required.

## 2. Create the Relativity Controller

1. Open the **Extensions** menu.
2. Choose **“OpenRelativity C4D: Create Relativity Controller”**.
3. The plugin either:
   - creates a Null named **`ORC_Relativity_Controller`**, selects it, and
     confirms with a dialog; or
   - if one already exists, simply **selects** the existing controller and tells
     you so (only one controller per scene is intended).

You can confirm a controller exists at any time via **Extensions > “OpenRelativity
C4D: About”**, which shows `Controller: present` or `Controller: not in scene`.

## 3. Adjust the settings

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

### Integration

| Field | Type | Default | Meaning |
|---|---|---|---|
| **Octane Adapter Enabled** | Bool | Off | When on (and Octane is installed), mirror results onto Octane materials/camera. Octane is **optional**; leaving it off changes nothing. |
| **Bake Mode Enabled** | Bool | Off | When on, effects will be baked per frame (for rendering) instead of shown as a live preview. |

> The strength and beta fields use a **percent** display: the stored value is a
> fraction (`0.0–1.0`), shown as `0–100%`. These map directly to the `strength`
> and `beta` parameters of the math core
> (`openrelativity_c4d.core`).

## 4. What the fields do *not* do yet

In Phase 1 the controller **stores** these values and exposes clean read/write
helpers for the rest of the plugin. The following are intentionally **not
implemented yet** (see [`ROADMAP.md`](ROADMAP.md)):

- Lorentz **deformation** of geometry.
- Doppler / searchlight **material** changes.
- **Octane** output (the adapter is a safe no-op until Phase 3).
- **Bake** workflow.

Changing the values now is safe and will be honored once those features land.

## 5. For developers

Read and write controller values by **field name** (no hard-coded IDs):

```python
from openrelativity_c4d.c4d import scene_controller

doc = c4d.documents.GetActiveDocument()
controller = scene_controller.find_controller(doc)

c_value = scene_controller.get_value(controller, scene_controller.FIELD_SPEED_OF_LIGHT)
scene_controller.set_value(controller, scene_controller.FIELD_DOPPLER_STRENGTH, 0.5)

state = scene_controller.read_state(controller)  # dict of every field
```

Field-name constants, defaults, and the creation logic all live in
`openrelativity_c4d/c4d/scene_controller.py`.
