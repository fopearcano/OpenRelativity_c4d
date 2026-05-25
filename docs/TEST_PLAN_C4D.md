# Manual Test Plan - Cinema 4D (core, no Octane required)

A formal manual test plan for OpenRelativity_c4d in **Cinema 4D 2023+**, with
**no Octane** required. Octane-specific testing is in
[`TEST_PLAN_OCTANE.md`](TEST_PLAN_OCTANE.md). Known limitations (expected
behaviour, not bugs) are in [`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md).

These steps cannot be automated (they need a running Cinema 4D); the pure-Python
math is covered by `python tools/verify_repo.py`.

## Environment

| Item | Value |
|---|---|
| Cinema 4D version | __________ (must be 2023+) |
| OS | __________ |
| Plugin version | 0.1.0 |
| Renderer used | Standard / Physical |
| Tester / date | __________ |

Record each case as **Pass / Fail** with notes. Keep the *Extensions > Console*
open throughout and watch for `[OpenRelativity C4D]` lines and tracebacks.

## TC-1 - Install & load

**Pre:** plugin not yet installed.
**Steps:**
1. Copy the `OpenRelativity_c4d/` folder (entry point + package) into the C4D
   user `plugins` folder (see [`INSTALLATION.md`](INSTALLATION.md)).
2. Restart Cinema 4D.
3. Open *Extensions > Console*.

**Expected:** Console shows `Loading OpenRelativity C4D v0.1.0 ...` and
`... loaded successfully.`; **no Python traceback**. ☐ Pass ☐ Fail

## TC-2 - Extensions menu commands appear

**Steps:** Open the *Extensions* menu.
**Expected:** all commands are present:
About; Control Panel; Create Relativity Controller; Setup Relativistic Camera;
Setup Selected Relativistic Objects; Select Relativistic Objects; Create Test
Scene; Apply Doppler Material Preview; Apply Searchlight Preview; Apply Relativity
Material Preview; Clear Material Preview; Create Lorentz Preview Copies; Remove
Lorentz Preview Copies; Apply All Previews; Octane Status; Apply Octane-Compatible
Material Preview; Show AOV Plan; Export Experimental OSL Camera; Export Relativity
Metadata JSON. ☐ Pass ☐ Fail

## TC-3 - About dialog

**Steps:** Run *Extensions > OpenRelativity C4D: About*.
**Expected:** a dialog lists version `0.1.0`, target `Cinema 4D 2023+`, the
running build, Octane (`detected`/`not detected`), and Controller / Camera /
Objects / Doppler-preview status; closes cleanly. ☐ Pass ☐ Fail

## TC-4 - Control Panel

**Steps:** Run *Extensions > OpenRelativity C4D: Control Panel*.
**Expected:** a compact, non-modal window opens with a **Status** group
(Controller / Camera / ORC objects / Octane) and grouped buttons (Scene setup,
Material preview, Lorentz geometry, Octane / export, Info), plus Refresh / Close.
It fits on the screen without being excessively tall. ☐ Pass ☐ Fail

## TC-5 - Create test scene (and repeat-safety)

**Steps:**
1. From the Control Panel (or Extensions), run **Create Test Scene**.
2. Inspect the Object Manager.
3. Run **Create Test Scene** a second time.

**Expected:**
- First run creates `ORC_Relativity_Controller`, `ORC_Relativistic_Camera`
  (the viewport looks through it), an `ORC_Test_Scene` null containing
  `ORC_Test_Approaching`, `ORC_Test_Receding`, `ORC_Test_Lateral`,
  `ORC_Test_Static`, and a light.
- The Control Panel status shows Controller `found`, Camera name, ORC objects
  `4` (or more), Octane status.
- Second run **does not overwrite**: it reuses the controller/camera and adds a
  new `ORC_Test_Scene_2` (uniquely-named objects). ☐ Pass ☐ Fail

## TC-6 - Apply material previews

**Pre:** a test scene exists.
**Steps:** run **Apply Relativity Material Preview** (or *Apply All Previews*),
then render with **Standard** or **Physical**.
**Expected (approximate look):**
- `ORC_Test_Approaching` - **bluer and brighter**.
- `ORC_Test_Receding` - **redder and dimmer**.
- `ORC_Test_Lateral` - slightly red / slightly dimmer (transverse).
- `ORC_Test_Static` - **unchanged**.
- One `ORC_Preview_<name>` material per object appears; the objects' **original
  materials/tags are not modified** (a preview Texture tag is layered on top).
- **Apply Doppler Material Preview** alone changes only colour; **Apply
  Searchlight Preview** alone changes only brightness. ☐ Pass ☐ Fail

## TC-7 - Clear material preview

**Steps:** run **Clear Material Preview**.
**Expected:** all `ORC_Preview_*` materials and the preview Texture tags are
removed; original look is restored; the About/Control-Panel preview count returns
to 0. ☐ Pass ☐ Fail

## TC-8 - Create / remove Lorentz preview copies

**Steps:**
1. Run **Create Lorentz Preview Copies**.
2. Inspect the Object Manager and viewport.
3. Run **Remove Lorentz Preview Copies**.

**Expected:**
- Create makes `ORC_LorentzPreview_<name>` duplicates, **contracted along the
  velocity axis** (e.g. the approaching/receding cubes are shorter in Z); the
  originals are **hidden** (with *Hide Originals* on) but otherwise unedited.
- Remove deletes the copies and **restores the originals' visibility**.
- Running Create twice does not stack duplicates (the copy is replaced). ☐ Pass ☐ Fail

## TC-9 - Export metadata JSON

**Steps:** run **Export Relativity Metadata JSON**, choose a path, open the file.
**Expected:** valid JSON matching [`METADATA_SCHEMA.md`](METADATA_SCHEMA.md):
`schema`, `schema_version`, `document` (fps/frame/time), `controller`, `camera`
(with `observer_beta`), and one `objects[]` entry per ORC object with `velocity`,
`beta`, `cos_theta`, `doppler_factor`, `searchlight_multiplier`, `guid`, and
`approximation_notes`. ☐ Pass ☐ Fail

## TC-10 - Setup commands on user geometry

**Steps:**
1. Add your own primitive; with it selected run **Setup Selected Relativistic
   Objects**. Give it a velocity in its User Data.
2. Select a camera (or none) and run **Setup Relativistic Camera**.
3. Run **Select Relativistic Objects**.

**Expected:** the object gets ORC User Data (controller/cameras are skipped);
the camera gets ORC User Data or one is created; Select selects all ORC objects.
Re-running **Setup Selected** on an already-configured object does not duplicate
its User Data. ☐ Pass ☐ Fail

## TC-11 - No console errors

**Steps:** review *Extensions > Console* after performing TC-1..TC-10.
**Expected:** informational `[OpenRelativity C4D]` lines only; **no tracebacks /
ERROR** entries. ☐ Pass ☐ Fail

## TC-12 - Repeated execution is safe

**Steps:** run each of these **twice in a row**: Create Relativity Controller,
Setup Relativistic Camera, Apply Relativity Material Preview, Create Lorentz
Preview Copies, Create Test Scene; and run **Clear Material Preview** / **Remove
Lorentz Preview Copies** when nothing is present.
**Expected:** no duplicate controllers/cameras/materials/tags/copies; "create"
of an existing controller/camera just **selects** it; test scene makes a new
numbered set; clear/remove with nothing present is a harmless no-op (a "nothing
to clear/remove" message). ☐ Pass ☐ Fail

## Results summary

| TC | Title | Result | Notes |
|---|---|---|---|
| 1 | Install & load | | |
| 2 | Menu commands appear | | |
| 3 | About dialog | | |
| 4 | Control Panel | | |
| 5 | Create test scene + repeat | | |
| 6 | Apply material previews | | |
| 7 | Clear material preview | | |
| 8 | Lorentz preview copies | | |
| 9 | Export metadata JSON | | |
| 10 | Setup on user geometry | | |
| 11 | No console errors | | |
| 12 | Repeated execution safe | | |
