# Experimental OSL Camera

A **placeholder** OSL camera shader for *future* Octane OSL-camera experiments,
plus a command to export it. This is the most speculative part of the project.

> ⚠️ **EXPERIMENTAL - not physically complete, not wired into Octane.**
> The generator only writes a text file. It does **not** install, compile, or
> bind anything into Octane, and the shader's relativistic ray distortion is a
> crude approximation (no light-travel-time, no ray-origin output, no verified
> Octane camera binding). Do not expect physically correct results. This is
> scaffolding to experiment with later.

## The command

**Extensions > “OpenRelativity C4D: Export Experimental OSL Camera”** opens a
save dialog and writes `relativity_camera_experimental.osl` to the location you
choose. It never writes into an Octane installation and never auto-installs.

A committed reference copy lives at
[`examples/osl/relativity_camera_experimental.osl`](../examples/osl/relativity_camera_experimental.osl).
The generator (`openrelativity_c4d/octane/osl_camera.py`:
`get_osl_source()` / `export_osl_camera(path)`) is import-safe and keeps the two
in sync (a unit test enforces it).

## Shader parameters

| Parameter | Default | Meaning |
|---|---|---|
| `beta` | `0.0` | Observer speed `v/c`, in `[0, 1)`. |
| `velocity_dir` | `(0, 0, 1)` | Observer motion direction. |
| `aberration_strength` | `1.0` | Blend `0` (off) → `1` (full aberration). |
| `doppler_strength` | `1.0` | Blend `0` (off) → `1` (full Doppler factor). |
| `fov_scale` | `1.0` | Crude FOV / zoom placeholder. |

Plus **placeholder** I/O: `in_ray_dir` (input) and `out_ray_dir` /
`out_doppler_factor` (outputs). **These are generic, not confirmed Octane camera
bindings.**

## What the shader does (and doesn't)

Does (as a crude illustration):
- Applies the **relativistic aberration of light** to a ray direction:
  `cos θ' = (cos θ + β) / (1 + β cos θ)`, blended by `aberration_strength`.
- Computes an approximate **Doppler factor**
  `(1 − β cos θ) / √(1 − β²)`, blended by `doppler_strength`.
- A crude `fov_scale` that scales the ray's perpendicular spread.

Does **not**:
- Output a ray **origin**, or generate the full camera ray (a real OSL camera
  must produce both origin and direction from the sensor sample).
- Use the correct **Octane OSL-camera globals/bindings** - the inputs/outputs
  here are placeholders that must be mapped to Octane's actual camera ray I/O for
  your Octane version.
- Model **light-travel-time / retarded position**, or any 4-vector treatment.
- Guarantee it **compiles or binds** as an Octane camera on any given version.

## How you might experiment (manual, unsupported)

1. Export the shader with the command above.
2. In Octane, create an **OSL camera** node and load/paste the shader.
3. **Verify and wire** the Octane camera ray I/O: map Octane's actual sensor /
   ray globals to `in_ray_dir`, and Octane's ray output to `out_ray_dir` (and add
   a ray-origin output). This is the unknown that makes it experimental.
4. Drive `beta` / `velocity_dir` from the Relativity Controller + camera (by hand
   for now).
5. Expect to iterate - treat the result as a look-dev experiment, not physics.

## TODO / unknowns to make this real

- The exact **Octane OSL-camera shader contract** (which globals provide the
  sensor sample and how the generated ray origin/direction are returned) for the
  target Octane version.
- Whether Octane OSL cameras can output an auxiliary value (the Doppler factor)
  usable downstream, or whether that must come from an AOV instead
  (see [`AOV_PIPELINE.md`](AOV_PIPELINE.md)).
- A correct ray-generation model (origin + direction from the film sample) before
  any physical claims.

This work is tracked as **Phase 3 (experimental)** in
[`OCTANE_INTEGRATION.md`](OCTANE_INTEGRATION.md) and [`ROADMAP.md`](ROADMAP.md).
The object/camera *OSL* User Data toggles remain placeholders until the above is
resolved.
