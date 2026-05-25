# Quickstart - a 5-minute relativistic test

The fastest way to see OpenRelativity_c4d working. Everything here is an
**artistic approximation, not spectral/radiometric rendering** (see the linked
docs for the science and limitations).

## 1. Install the plugin (~1 min)

Copy `openrelativity_c4d.pyp` and the `openrelativity_c4d/` package folder into a
folder inside your Cinema 4D **user plugins** directory, then restart Cinema 4D.
Full steps: [README - Installation](../README.md#installation). Octane is **not**
required.

Check it loaded: *Extensions > “OpenRelativity C4D: About”*.

## 2. Create the test scene (~30 sec)

Run **Extensions > “OpenRelativity C4D: Create Test Scene”**.

It builds (and looks through) a relativistic camera, a Relativity Controller, a
light, and four labelled cubes - each moving differently relative to the camera:

| Object | Motion | Expect after previews |
|---|---|---|
| `ORC_Test_Approaching` | toward the camera | **blue** + **brighter** (glow) + contracted |
| `ORC_Test_Receding` | away from the camera | **red** + **dimmer** |
| `ORC_Test_Lateral` | across the view | slight transverse **redshift** |
| `ORC_Test_Static` | not moving | unchanged |

Run it again anytime - it reuses the controller/camera and makes a fresh,
uniquely-named set (`ORC_Test_Scene_2`, ...), so nothing is overwritten.

## 3. Apply the previews (~30 sec)

Run **Extensions > “OpenRelativity C4D: Apply All Previews”**.

This applies the **Doppler** colour shift and **searchlight** brightness (one
generated `ORC_Preview_<name>` material per object, layered non-destructively)
**and** creates **Lorentz** contracted duplicates (`ORC_LorentzPreview_<name>`,
originals hidden). You should now see the colours/brightness above, and the
moving cubes shortened along their direction of travel.

To revert: *Clear Material Preview* and *Remove Lorentz Preview Copies*.

## 4. Render with Standard / Physical first (~2 min)

Set the renderer to **Standard** or **Physical** and render the view (the test
scene already looks through the relativistic camera). Tweak and re-run:

- Lower the controller's **Artificial Speed of Light** (e.g. 1000 → 400) to make
  the same speeds look *more* relativistic, then *Apply All Previews* again.
- Adjust **Doppler / Searchlight / Lorentz Deformation Strength** on the
  controller for an art-directable amount.
- Give objects different **Velocity X/Y/Z** or **Object Beta** and re-apply.

These previews are **not live** - re-run *Apply All Previews* after any change.

## 5. Later: Octane (optional)

Octane support is **optional and isolated** - the plugin runs fully without it.
Octane material/camera mapping is **not implemented yet** (the adapter is a safe
no-op and the *Octane* toggles are stubs); it is planned for a later phase. For
now, render the previews with Standard/Physical. See
[`ROADMAP.md`](ROADMAP.md) (Phase 3) and [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Where to go next

- [`USER_GUIDE.md`](USER_GUIDE.md) - every command and field in detail.
- [`DOPPLER_PREVIEW.md`](DOPPLER_PREVIEW.md),
  [`SEARCHLIGHT_PREVIEW.md`](SEARCHLIGHT_PREVIEW.md),
  [`LORENTZ_PREVIEW.md`](LORENTZ_PREVIEW.md) - how each effect works and its
  limitations.
- [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) - scope and the "why".
