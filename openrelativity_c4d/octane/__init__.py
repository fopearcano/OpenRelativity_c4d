"""Optional, isolated Octane integration.

This sub-package is the **only** place allowed to import an Octane module, always
through a guarded ``try/except`` (see :mod:`openrelativity_c4d.octane.detection`).
Importing anything here is safe whether or not Octane - or even Cinema 4D - is
present; when Octane is absent every operation is a no-op.

Phase 1 ships **stubs**: detection works, but the node/material mapping is not
implemented. See docs/ROADMAP.md (Phase 3).
"""
