"""Build a ready-to-preview demo scene.

Creates a Relativity Controller, a relativistic camera, and four labelled test
cubes (approaching / receding / lateral / static) with different velocities, all
framed in front of the camera, plus a light. Running it again is safe: it reuses
the singleton controller/camera and creates a fresh, uniquely-named object set
(``ORC_Test_Scene``, ``ORC_Test_Scene_2``, ...) so nothing is overwritten.

The test objects set *Use Camera Relative Direction* off, so the approaching /
receding / lateral classification comes purely from each velocity vs. the
camera's viewing axis - independent of where they sit - for a predictable demo.

``import c4d`` here resolves to Cinema 4D's module (absolute import).
"""

import c4d

from ..logging_utils import get_logger
from . import camera_tools, object_tools, scene_controller, userdata

log = get_logger("test_scene")

GROUP_BASE = "ORC_Test_Scene"
LIGHT_BASE = "ORC_Test_Light"

CUBE_SIZE = 200.0
CAMERA_DISTANCE = 1100.0  # camera sits at -Z, looking toward the objects at z=0

#: Speed for the moving objects. With the controller default c = 1000 this is
#: beta = 0.6 (derived from |velocity| / c).
TEST_SPEED = 600.0

#: (base name, world position, velocity vector). Velocities are along the camera
#: viewing axis: -Z = toward the camera (approaching), +Z = away (receding).
TEST_OBJECTS = (
    ("ORC_Test_Approaching", (-300.0, 160.0, 0.0), (0.0, 0.0, -TEST_SPEED)),
    ("ORC_Test_Receding", (300.0, 160.0, 0.0), (0.0, 0.0, TEST_SPEED)),
    ("ORC_Test_Lateral", (-300.0, -160.0, 0.0), (TEST_SPEED, 0.0, 0.0)),
    ("ORC_Test_Static", (300.0, -160.0, 0.0), (0.0, 0.0, 0.0)),
)


def _iter_objects(op):
    while op:
        yield op
        for child in _iter_objects(op.GetDown()):
            yield child
        op = op.GetNext()


def _next_slot(doc):
    """Return a name suffix ('' , '_2', '_3', ...) free of name collisions."""
    existing = {op.GetName() for op in _iter_objects(doc.GetFirstObject())}
    index = 1
    while True:
        suffix = "" if index == 1 else "_{0}".format(index)
        candidates = [GROUP_BASE + suffix, LIGHT_BASE + suffix]
        candidates += [base + suffix for base, _, _ in TEST_OBJECTS]
        if not any(name in existing for name in candidates):
            return suffix
        index += 1


def _make_cube(name, position, velocity):
    cube = c4d.BaseObject(c4d.Ocube)
    cube.SetName(name)
    cube[c4d.PRIM_CUBE_LEN] = c4d.Vector(CUBE_SIZE, CUBE_SIZE, CUBE_SIZE)
    cube.SetRelPos(c4d.Vector(position[0], position[1], position[2]))

    object_tools.add_orc_object_data(cube)
    userdata.set_value(cube, object_tools.FIELD_VELOCITY_X, float(velocity[0]))
    userdata.set_value(cube, object_tools.FIELD_VELOCITY_Y, float(velocity[1]))
    userdata.set_value(cube, object_tools.FIELD_VELOCITY_Z, float(velocity[2]))
    # Predictable demo: classify by velocity vs. the camera axis, not geometry.
    userdata.set_value(cube, object_tools.FIELD_USE_CAMERA_DIRECTION, False)
    return cube


def _ensure_camera(doc):
    """Return a relativistic camera, creating and framing one if needed."""
    camera = camera_tools.find_relativistic_camera(doc)
    if camera is None:
        camera = camera_tools.create_camera(doc)  # own undo step
        if camera is not None:
            camera.SetRelPos(c4d.Vector(0.0, 0.0, -CAMERA_DISTANCE))
    # Look through it so the render/editor uses this camera.
    try:
        base_draw = doc.GetActiveBaseDraw()
        if base_draw is not None and camera is not None:
            base_draw.SetSceneCamera(camera)
    except Exception:  # noqa: BLE001
        pass
    return camera


def create_test_scene(doc):
    """Create a fresh demo scene. Returns ``(group_object, suffix)`` or ``None``.

    The controller and camera are singletons (reused if present); the test object
    set is uniquely named so repeated runs never overwrite earlier sets.
    """
    if doc is None:
        return None

    # Singletons (each manages its own undo step if it has to create).
    scene_controller.find_or_create(doc)
    _ensure_camera(doc)

    suffix = _next_slot(doc)

    try:
        group = c4d.BaseObject(c4d.Onull)
        group.SetName(GROUP_BASE + suffix)
        for base, position, velocity in TEST_OBJECTS:
            _make_cube(base + suffix, position, velocity).InsertUnder(group)
        light = c4d.BaseObject(c4d.Olight)
        light.SetName(LIGHT_BASE + suffix)
        light.SetRelPos(c4d.Vector(0.0, 400.0, -600.0))
        light.InsertUnder(group)
    except Exception:  # noqa: BLE001
        log.exception("Failed to build the test scene objects.")
        return None

    doc.StartUndo()
    doc.InsertObject(group)
    doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, group)
    doc.EndUndo()
    doc.SetActiveObject(group)
    c4d.EventAdd()
    log.info("Created test scene '%s'.", group.GetName())
    return group, suffix
