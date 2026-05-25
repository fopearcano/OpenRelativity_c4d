# `relativity_core` — portable physics/math (pure Python)

The **science layer**. Dependency-free Python; **must never `import c4d`** and
must never import Octane. Designed so it can later be reimplemented in C++ behind
the same numeric API (numbers/arrays in, numbers/arrays out).

Planned modules (see [`../../docs/ARCHITECTURE.md`](../../docs/ARCHITECTURE.md) §3):

- `constants` — default speed of light, epsilon guards.
- `lorentz` — Lorentz factor, inverse factor, length contraction.
- `velocity` — relativistic velocity addition.
- `doppler` — relativistic Doppler factor and searchlight/beaming intensity.
- `spectrum` — RGB↔XYZ and approximate wavelength-shift recolor.
- `aberration` — retarded-time apparent-position solve.

> **No code yet (Phase 0).** This stub documents intent only.
