"""Pure-Python relativistic physics/math core.

**No Cinema 4D, no Octane, no third-party dependencies.** Every function takes
and returns plain numbers / tuples so the API is portable and easy to migrate to
C++ later. This sub-package can be imported and unit-tested with a plain Python
interpreter.
"""

from . import doppler, relativity_math, searchlight, transforms

__all__ = ["relativity_math", "doppler", "searchlight", "transforms"]
