"""Control Panel status model + on-demand collection (safe, no polling).

Snapshots the relativity scene state for the Control Panel's status read-out.
It is **import-safe**: there is no top-level ``import c4d`` and the Cinema-4D-bound
sibling modules are imported lazily inside :func:`collect_status`, so the pure
:class:`UIStatus` model and its label helpers unit-test in plain Python and
importing this module pulls in no ``c4d`` and no Octane.

Collection happens **on demand only** (panel open / after an action / manual
refresh) - there is no timer or polling. Every query is guarded: a failure yields
an ``Unknown`` field and a single debug log line, never an exception.
"""

from ..logging_utils import get_logger

log = get_logger("ui_status")

# Octane tri-state tokens.
OCTANE_DETECTED = "detected"
OCTANE_MISSING = "missing"
OCTANE_UNKNOWN = "unknown"


def _ok_missing(value):
    if value is None:
        return "Unknown"
    return "OK" if value else "Missing"


def _count(value):
    return "?" if value is None else str(value)


class UIStatus(object):
    """A snapshot of the relativity scene state, with concise label helpers.

    Fields are tri-state where it matters: ``controller`` / ``camera`` are
    ``True`` / ``False`` / ``None`` (unknown); counts are ``int`` / ``None``;
    ``octane`` is one of the ``OCTANE_*`` tokens.
    """

    __slots__ = ("controller", "camera", "object_count", "preview_materials",
                 "lorentz_copies", "octane", "last_action")

    def __init__(self, controller=None, camera=None, object_count=None,
                 preview_materials=None, lorentz_copies=None,
                 octane=OCTANE_UNKNOWN, last_action=""):
        self.controller = controller
        self.camera = camera
        self.object_count = object_count
        self.preview_materials = preview_materials
        self.lorentz_copies = lorentz_copies
        self.octane = octane
        self.last_action = last_action

    def controller_label(self):
        return _ok_missing(self.controller)

    def camera_label(self):
        return _ok_missing(self.camera)

    def objects_label(self):
        return _count(self.object_count)

    def generated_label(self):
        return "{0} mat / {1} Lorentz".format(
            _count(self.preview_materials), _count(self.lorentz_copies))

    def octane_label(self):
        return {OCTANE_DETECTED: "Detected",
                OCTANE_MISSING: "Missing"}.get(self.octane, "Unknown")

    def last_label(self):
        return self.last_action or "(none yet)"

    def format_summary(self):
        """Multi-line summary used by the panel's UI Diagnostics dialog."""
        return "\n".join([
            "Controller: {0}".format(self.controller_label()),
            "Camera:     {0}".format(self.camera_label()),
            "Objects:    {0}".format(self.objects_label()),
            "Generated:  {0}".format(self.generated_label()),
            "Octane:     {0}".format(self.octane_label()),
            "Last:       {0}".format(self.last_label()),
        ])


def _safe(call, label):
    """Run ``call()`` guarded; return its result, or ``None`` (logged at debug)."""
    try:
        return call()
    except Exception:  # noqa: BLE001
        log.debug("Status query '%s' failed.", label, exc_info=True)
        return None


def _octane_token():
    """Octane tri-state via the existing adapter; never raises, never needs Octane."""
    try:
        from ..octane import adapter
        return OCTANE_DETECTED if adapter.is_available() else OCTANE_MISSING
    except Exception:  # noqa: BLE001
        log.debug("Octane availability check failed.", exc_info=True)
        return OCTANE_UNKNOWN


def collect_status(doc, last_action=""):
    """Return a :class:`UIStatus` snapshot for ``doc``. Never raises.

    With ``doc is None`` returns an all-unknown status and imports nothing
    Cinema-4D-bound. Otherwise each field is queried independently and guarded, so
    one failing query cannot blank the others or crash the caller. Lazy imports
    keep this module import-safe / testable without Cinema 4D.
    """
    if doc is None:
        return UIStatus(last_action=last_action)

    def controller():
        from . import scene_controller
        return scene_controller.find_controller(doc) is not None

    def camera():
        from . import camera_tools
        return camera_tools.find_relativistic_camera(doc) is not None

    def objects():
        from . import object_tools
        return len(object_tools.collect_orc_objects(doc))

    def materials():
        from . import preview_material
        return preview_material.count_preview_materials(doc)

    def lorentz():
        from . import lorentz_preview
        return lorentz_preview.count_preview_copies(doc)

    return UIStatus(
        controller=_safe(controller, "controller"),
        camera=_safe(camera, "camera"),
        object_count=_safe(objects, "objects"),
        preview_materials=_safe(materials, "preview_materials"),
        lorentz_copies=_safe(lorentz, "lorentz_copies"),
        octane=_octane_token(),
        last_action=last_action,
    )
