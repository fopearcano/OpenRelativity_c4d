# Manual Test Plan - Octane

Manual tests for the **Octane** side of OpenRelativity_c4d. Octane support is
**adapter/scaffolding-level** today (detection, a material adapter that falls
back to Standard, an AOV *plan*, and an experimental OSL export) - see
[`OCTANE_INTEGRATION.md`](OCTANE_INTEGRATION.md) and
[`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md). The core C4D behaviour is tested
in [`TEST_PLAN_C4D.md`](TEST_PLAN_C4D.md).

> **No native Octane materials/AOVs are created yet.** The expected outcome of
> the material command is currently a **Standard-material fallback** that is
> reported honestly. These tests verify *safety, detection, and fallback* - not
> a finished Octane look.

## Environment

| Item | Value |
|---|---|
| Cinema 4D version | __________ (2023+) |
| Octane plugin + version | __________ |
| Octane installed for the "present" cases? | yes / no |
| Plugin version | 0.1.0 |
| Tester / date | __________ |

Keep *Extensions > Console* open and watch for tracebacks.

## TC-O1 - Install & load with Octane present

**Pre:** Octane for Cinema 4D installed and working.
**Steps:** install OpenRelativity_c4d, restart, open the Console.
**Expected:** the plugin loads normally (`... loaded successfully.`); **no error
referencing Octane / `c4doctane`**; both plugins coexist. ☐ Pass ☐ Fail

## TC-O2 - No direct Octane import errors

**Steps:** review the load log; (optional) confirm the core package import path
does not hard-import Octane.
**Expected:** loading OpenRelativity_c4d never triggers an Octane import error,
whether Octane is present or not - Octane is only ever imported guarded, inside
`openrelativity_c4d/octane/`. ☐ Pass ☐ Fail

## TC-O3 - Octane Status (Octane present)

**Steps:** run *Extensions > OpenRelativity C4D: Octane Status*.
**Expected:** the dialog reports `Octane detected: yes` (and/or matched plugin
names), `Octane renderer active: yes/no` (depending on the active renderer), and
the standing notes ("integration not implemented yet", "no guarantee of full
physical relativistic ray tracing"). ☐ Pass ☐ Fail

## TC-O4 - Apply Octane-Compatible Material Preview

**Pre:** a test scene with relativistic objects (run *Create Test Scene*).
**Steps:** run **Apply Octane-Compatible Material Preview**, then render with
Octane.
**Expected (current behaviour):** the report says `via Octane material: 0` and
`via Standard fallback: N`; each object gets a Standard `ORC_Preview_<name>`
material (Octane renders these), tinted/brightened like the Standard preview.
**No crash**, no Octane material nodes are created. ☐ Pass ☐ Fail

## TC-O5 - Fallback when Octane APIs are unavailable

Run **both** scenarios:

**(a) Octane absent** - on a C4D without Octane (or with it disabled): run
*Octane Status* (expect `not detected`) and **Apply Octane-Compatible Material
Preview** (expect it still applies the Standard fallback, no crash).

**(b) Octane present but mapping unavailable** - this is the normal case today:
the adapter resolves Octane but reports the material mapping as `unsupported` and
falls back. Confirm the dialog/Console explains the fallback and nothing errors.
**Expected:** in both, the command completes safely with a Standard-material
result and a clear report. ☐ Pass ☐ Fail

## TC-O6 - Manual AOV plan review

**Steps:** run **Show AOV Plan**.
**Expected:** lists the five desired AOVs (`ORC_DopplerFactor`, `ORC_Beta`,
`ORC_Searchlight`, `ORC_ObjectVelocity`, `ORC_RelativityMask`); states
**Automatic Octane AOV creation: NOT supported - manual setup required**; shows
the manual-setup summary. Cross-check against
[`AOV_PIPELINE.md`](AOV_PIPELINE.md). No render settings are modified. ☐ Pass ☐ Fail

## TC-O7 - Optional OSL export review

**Steps:** run **Export Experimental OSL Camera**, choose a path, open the file.
**Expected:** an `.osl` file is written **to the chosen location only** (it is
**not** installed into Octane); the file is clearly marked `EXPERIMENTAL`, NOT
physically complete, NOT wired into Octane, and exposes `beta`, `velocity_dir`,
`aberration_strength`, `doppler_strength`, `fov_scale`. See
[`OSL_CAMERA_EXPERIMENTS.md`](OSL_CAMERA_EXPERIMENTS.md). ☐ Pass ☐ Fail

## TC-O8 - Core unaffected by Octane

**Steps:** with Octane present, run the standard previews from
[`TEST_PLAN_C4D.md`](TEST_PLAN_C4D.md) (TC-6..TC-9).
**Expected:** the Standard/Physical previews, Lorentz copies, and metadata export
behave identically with Octane installed - the Octane presence changes nothing in
the core paths. ☐ Pass ☐ Fail

## Results summary

| TC | Title | Result | Notes |
|---|---|---|---|
| O1 | Install/load with Octane | | |
| O2 | No direct Octane import errors | | |
| O3 | Octane Status | | |
| O4 | Octane-compatible material preview | | |
| O5 | Fallback (absent / unsupported) | | |
| O6 | AOV plan review | | |
| O7 | OSL export review | | |
| O8 | Core unaffected by Octane | | |
