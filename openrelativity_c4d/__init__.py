"""OpenRelativity C4D - artist-facing relativistic visualization for Cinema 4D.

Importing this package is **safe outside Cinema 4D**. It does not import the
``c4d`` module or any Cinema-4D-specific submodule at import time, so the
pure-Python physics core under :mod:`openrelativity_c4d.core` can be imported and
unit-tested with a plain Python interpreter (see ``openrelativity_c4d/tests``).

Sub-packages
------------
* :mod:`openrelativity_c4d.core`   - pure-Python relativistic math (no ``c4d``).
* :mod:`openrelativity_c4d.c4d`    - Cinema 4D integration (imports ``c4d``).
* :mod:`openrelativity_c4d.octane` - optional, isolated Octane adapter (stubs).
"""

from .constants import (
    PLUGIN_NAME,
    PLUGIN_VERSION,
    TARGET_C4D_VERSION,
)

__version__ = PLUGIN_VERSION

__all__ = [
    "PLUGIN_NAME",
    "PLUGIN_VERSION",
    "TARGET_C4D_VERSION",
    "__version__",
    "is_c4d_available",
]


def is_c4d_available():
    """Return ``True`` if the Cinema 4D ``c4d`` module can be imported.

    Used by the integration and Octane layers to stay import-safe when running
    outside Cinema 4D (e.g. during ``unittest`` runs of the math core).
    """
    try:
        import c4d  # noqa: F401  (probe import only)

        return True
    except ImportError:
        return False
