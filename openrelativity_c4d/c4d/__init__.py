"""Cinema 4D integration layer.

Modules here import the Cinema 4D ``c4d`` module and therefore only work inside
Cinema 4D. They are imported lazily by :mod:`openrelativity_c4d.bootstrap`, never
by the pure-Python core or the test-suite.

Note: ``import c4d`` inside these modules resolves to **Cinema 4D's** top-level
``c4d`` module (Python 3 absolute import), not to this ``openrelativity_c4d.c4d``
sub-package. Use relative imports (``from .. import ...``) for package code.
"""
