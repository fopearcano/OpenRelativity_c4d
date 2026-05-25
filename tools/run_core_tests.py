#!/usr/bin/env python3
"""Run the pure-Python core unit tests without Cinema 4D.

Adds the repository root to ``sys.path`` and runs unittest discovery over the
``openrelativity_c4d/tests`` package. Usable from anywhere::

    python tools/run_core_tests.py

Exits non-zero if any test fails (suitable for CI / pre-commit).
"""

import os
import sys
import unittest

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)


def main():
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=os.path.join(_REPO_ROOT, "openrelativity_c4d", "tests"),
        top_level_dir=_REPO_ROOT,
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
