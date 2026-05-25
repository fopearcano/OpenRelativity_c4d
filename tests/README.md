# `tests` — unit tests for `relativity_core`

Tests for the **pure-Python physics core**. They must run with a plain Python
interpreter — **no Cinema 4D, no `c4d` import, no third-party requirement**
(runnable via `python -m unittest`; `pytest` optional).

Planned coverage (see [`../docs/ROADMAP.md`](../docs/ROADMAP.md), Phase 1):

- `lorentz` — gamma at known β; contraction limits (β→0 ⇒ no change, β→1 ⇒ →0).
- `velocity` — addition stays below `c`; reduces to Galilean at low β.
- `doppler` — `shift > 1` receding, `< 1` approaching; searchlight monotonicity.
- `aberration` — retarded-time solve against hand-checked cases.

> **No tests yet (Phase 0).** This stub documents intent only.
