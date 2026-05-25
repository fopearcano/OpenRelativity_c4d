"""Small shared Cinema 4D scene helpers.

Currently just object-tree traversal, factored out so the controller, camera,
object, preview, Lorentz, and test-scene modules don't each carry their own copy.

``import c4d`` here is Cinema 4D's module (this is a c4d-layer helper).
"""

import c4d  # noqa: F401  (kept for parity with the c4d layer; not strictly used)


def iter_objects(op):
    """Depth-first iterate an object and all its siblings and descendants.

    ``op`` is typically ``doc.GetFirstObject()``. Safe with ``None``.
    """
    while op:
        yield op
        for child in iter_objects(op.GetDown()):
            yield child
        op = op.GetNext()
