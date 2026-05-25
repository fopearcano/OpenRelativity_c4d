"""Experimental OSL camera shader generator (NOT wired into Octane).

Generates a **placeholder** OSL camera shader for FUTURE Octane OSL-camera
experiments. It only produces a text file - it does **not** install, compile, or
bind anything into Octane, and the shader's relativistic ray distortion is a
crude, physically-incomplete placeholder. See docs/OSL_CAMERA_EXPERIMENTS.md.

import-safe: no top-level ``import c4d``. ``get_osl_source`` is pure; the export
helper uses only plain file I/O.
"""

from ..logging_utils import get_logger

log = get_logger("octane.osl")

#: Suggested file name for the generated shader.
OSL_FILENAME = "relativity_camera_experimental.osl"

#: Shader parameters (name, default, description) - documentation/UX aid.
PARAMETERS = (
    ("beta", 0.0, "Observer speed v/c, in [0, 1)."),
    ("velocity_dir", (0.0, 0.0, 1.0), "Observer motion direction."),
    ("aberration_strength", 1.0, "0 = off, 1 = full aberration."),
    ("doppler_strength", 1.0, "0 = off, 1 = full Doppler factor."),
    ("fov_scale", 1.0, "Crude FOV / zoom placeholder."),
)

#: The experimental OSL camera shader source. Kept byte-identical to
#: examples/osl/relativity_camera_experimental.osl (a test enforces this).
_OSL_SOURCE = """// =====================================================================
// relativity_camera_experimental.osl
// OpenRelativity for Cinema 4D - EXPERIMENTAL OSL camera placeholder
//
// !!! EXPERIMENTAL - NOT PHYSICALLY COMPLETE - NOT WIRED INTO OCTANE !!!
//
// This is a PLACEHOLDER shader for FUTURE Octane OSL-camera experiments. It
// shows WHERE relativistic ray-direction aberration and a Doppler tint factor
// would be computed, but:
//   * it is NOT a correct relativistic camera;
//   * the Octane OSL *camera* ray input/output convention (which globals carry
//     the generated ray origin/direction) MUST be verified for your Octane
//     version and wired up - the in_ray_dir input / out_ray_dir output below
//     are GENERIC placeholders, not confirmed Octane camera bindings;
//   * there is no light-travel-time / retarded position and no ray ORIGIN
//     output; only the direction/colour math is illustrated.
//
// See docs/OSL_CAMERA_EXPERIMENTS.md. Do not expect physically correct results.
// =====================================================================

shader relativity_camera_experimental(
    // --- relativity parameters ---
    float  beta                = 0.0,             // observer speed v/c, in [0, 1)
    vector velocity_dir        = vector(0, 0, 1), // observer motion direction
    float  aberration_strength = 1.0,             // 0 = off, 1 = full aberration
    float  doppler_strength    = 1.0,             // 0 = off, 1 = full Doppler factor
    float  fov_scale           = 1.0,             // crude FOV / zoom placeholder

    // --- generic ray I/O (PLACEHOLDER - verify Octane camera bindings!) ---
    vector in_ray_dir          = vector(0, 0, 1), // incoming camera ray direction
    output vector out_ray_dir  = vector(0, 0, 1), // aberrated ray direction
    output float  out_doppler_factor = 1.0)       // observed/emitted wavelength
{
    float b = clamp(beta, 0.0, 0.999);

    // Normalise inputs (guard against zero-length vectors).
    vector n = normalize(in_ray_dir);
    float vlen = length(velocity_dir);
    vector vhat = (vlen > 1e-6) ? velocity_dir / vlen : vector(0, 0, 1);

    float ct = dot(n, vhat); // cosine of angle between ray and motion

    // --- crude FOV placeholder: scale the perpendicular spread of the ray ---
    vector npar  = ct * vhat;
    vector nperp = n - npar;
    n  = normalize(npar + nperp * max(fov_scale, 1e-4));
    ct = dot(n, vhat);

    // --- relativistic aberration of light (approximate) ---
    // cos(theta') = (cos(theta) + beta) / (1 + beta * cos(theta))
    float ct_ab = (ct + b) / (1.0 + b * ct);
    vector perp = n - ct * vhat;
    float perp_len = length(perp);
    vector perp_hat = (perp_len > 1e-6) ? perp / perp_len : vector(0, 0, 0);
    float st_ab = sqrt(max(0.0, 1.0 - ct_ab * ct_ab));
    vector n_ab = normalize(ct_ab * vhat + st_ab * perp_hat);

    // Blend original vs. aberrated direction (artistic control).
    out_ray_dir = normalize(mix(n, n_ab, clamp(aberration_strength, 0.0, 1.0)));

    // --- approximate relativistic Doppler factor (observed / emitted) ---
    // shift = (1 - beta * cos(theta)) / sqrt(1 - beta^2)
    float gamma_inv = sqrt(max(1e-6, 1.0 - b * b));
    float shift = (1.0 - b * ct) / gamma_inv;
    out_doppler_factor = mix(1.0, shift, clamp(doppler_strength, 0.0, 1.0));

    // NOTE: a real Octane OSL camera must ALSO output the ray ORIGIN and map
    // these outputs onto Octane's camera ray globals. That binding is NOT done
    // here - this shader only illustrates the relativistic direction/colour math.
}
"""


def get_osl_source():
    """Return the experimental OSL camera shader source as a string."""
    return _OSL_SOURCE


def export_osl_camera(path):
    """Write the OSL shader to ``path``. Returns a result dict; never raises hard.

    Plain file write only - it does NOT install or register anything in Octane.
    Result keys: ``ok`` (bool), ``path`` (str), ``error`` (str or ``None``).
    """
    try:
        with open(path, "w") as handle:
            handle.write(get_osl_source())
        log.info("Wrote experimental OSL camera shader to %s", path)
        return {"ok": True, "path": path, "error": None}
    except Exception as exc:  # noqa: BLE001
        log.exception("Failed to write OSL camera shader to %s", path)
        return {"ok": False, "path": path, "error": str(exc)}
