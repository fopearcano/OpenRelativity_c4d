"""Plugin commands.

* *Extensions > OpenRelativity C4D: About* - a modal dialog with the plugin
  version, target/running Cinema 4D version, Octane detection, whether a
  Relativity Controller exists in the scene, and the development status.
* *Extensions > OpenRelativity C4D: Create Relativity Controller* - creates (or
  re-selects) the ``ORC_Relativity_Controller`` Null with its User Data.
"""

import c4d  # Cinema 4D's module (absolute import; not the sibling sub-package)

from .. import constants, ids
from ..logging_utils import get_logger
from . import camera_tools, object_tools, scene_controller

log = get_logger("commands")


def _c4d_build():
    """Return the running Cinema 4D build as a string (best effort)."""
    try:
        return str(c4d.GetC4DVersion())
    except Exception:  # noqa: BLE001
        return "unknown"


def _octane_status():
    """Return a short human-readable Octane availability string."""
    try:
        from ..octane import detection

        return "detected" if detection.is_octane_available() else "not detected"
    except Exception:  # noqa: BLE001
        return "unknown"


def _controller_status():
    """Return whether a Relativity Controller exists in the active document."""
    try:
        doc = c4d.documents.GetActiveDocument()
        return "present" if scene_controller.find_controller(doc) else "not in scene"
    except Exception:  # noqa: BLE001
        return "unknown"


def _camera_status():
    """Return the name of the active relativistic camera, or 'none'."""
    try:
        doc = c4d.documents.GetActiveDocument()
        cam = camera_tools.find_relativistic_camera(doc)
        return cam.GetName() if cam is not None else "none"
    except Exception:  # noqa: BLE001
        return "unknown"


def _object_status():
    """Return the count of relativistic objects in the active document."""
    try:
        doc = c4d.documents.GetActiveDocument()
        return "{0} relativistic".format(len(object_tools.collect_orc_objects(doc)))
    except Exception:  # noqa: BLE001
        return "unknown"


def about_info_lines():
    """Build the list of text lines shown in the About dialog."""
    return [
        constants.TAGLINE,
        "",
        "Version:        {0}".format(constants.PLUGIN_VERSION),
        "Target C4D:     Cinema 4D {0}".format(constants.TARGET_C4D_VERSION),
        "Running build:  {0}".format(_c4d_build()),
        "Octane:         {0}".format(_octane_status()),
        "Controller:     {0}".format(_controller_status()),
        "Camera:         {0}".format(_camera_status()),
        "Objects:        {0}".format(_object_status()),
        "Phase:          {0}".format(constants.DEVELOPMENT_PHASE),
        "",
        "Status:",
        constants.STATUS_SUMMARY,
        "",
        constants.PROJECT_URL,
    ]


class AboutDialog(c4d.gui.GeDialog):
    """Minimal modal dialog summarising the plugin state."""

    _TEXT_ID_BASE = 2000

    def CreateLayout(self):
        self.SetTitle("About {0}".format(constants.PLUGIN_NAME))

        self.GroupBegin(
            id=1000,
            flags=c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT,
            cols=1,
            rows=0,
        )
        self.GroupBorderSpace(12, 12, 12, 12)
        for offset, line in enumerate(about_info_lines()):
            self.AddStaticText(
                self._TEXT_ID_BASE + offset,
                c4d.BFH_LEFT,
                name=line,
            )
        self.GroupEnd()

        # Standard OK button row.
        self.AddDlgGroup(c4d.DLG_OK)
        return True

    def Command(self, cid, msg):
        if cid == c4d.DLG_OK:
            self.Close()
        return True


class AboutCommand(c4d.plugins.CommandData):
    """``CommandData`` that opens :class:`AboutDialog`."""

    def Execute(self, doc):
        log.info("Opening About dialog.")
        dlg = AboutDialog()
        dlg.Open(
            dlgtype=c4d.DLG_TYPE_MODAL,
            pluginid=ids.DIALOG_ABOUT,
            defaultw=460,
            defaulth=260,
        )
        return True

    def GetState(self, doc):
        return c4d.CMD_ENABLED


class CreateControllerCommand(c4d.plugins.CommandData):
    """Create (or re-select) the ``ORC_Relativity_Controller`` Null."""

    def Execute(self, doc):
        if doc is None:
            return False

        existing = scene_controller.find_controller(doc)
        if existing is not None:
            doc.SetActiveObject(existing)
            c4d.EventAdd()
            log.info("Relativity Controller already present; selected it.")
            c4d.gui.MessageDialog(
                "A Relativity Controller already exists.\n"
                "It has been selected - edit its User Data in the Attribute Manager."
            )
            return True

        controller = scene_controller.create_controller(doc)
        if controller is None:
            c4d.gui.MessageDialog("Failed to create the Relativity Controller.")
            return False

        c4d.gui.MessageDialog(
            "Created '{0}'.\n"
            "Select it and open the Attribute Manager (User Data) to adjust the "
            "speed of light, beta, and effect strengths.".format(
                scene_controller.CONTROLLER_NAME
            )
        )
        return True

    def GetState(self, doc):
        return c4d.CMD_ENABLED


class SetupCameraCommand(c4d.plugins.CommandData):
    """Set up the selected camera (or create one) as a relativistic observer."""

    def Execute(self, doc):
        if doc is None:
            return False

        cam, action = camera_tools.setup_relativistic_camera(doc)
        if cam is None or action == "failed":
            c4d.gui.MessageDialog("Failed to set up the relativistic camera.")
            return False

        name = cam.GetName()
        if action == "created":
            message = (
                "Created '{0}' with relativity User Data.\n"
                "Open the Attribute Manager (User Data) to set Observer Beta or "
                "Observer Velocity.".format(name)
            )
        elif action == "configured":
            message = (
                "Added relativity User Data to the selected camera '{0}'.".format(name)
            )
        else:  # "exists"
            message = (
                "Camera '{0}' already has relativity User Data; selected it.".format(name)
            )
        log.info("Setup Relativistic Camera: %s (%s).", name, action)
        c4d.gui.MessageDialog(message)
        return True

    def GetState(self, doc):
        return c4d.CMD_ENABLED


class SetupObjectsCommand(c4d.plugins.CommandData):
    """Add relativistic-object User Data to each eligible selected object.

    Cameras and the Relativity Controller are skipped; objects that already have
    the data are left unchanged.
    """

    def Execute(self, doc):
        if doc is None:
            return False

        selected = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0)
        if not selected:
            c4d.gui.MessageDialog(
                "Select one or more objects first, then run this command."
            )
            return True

        controller = scene_controller.find_controller(doc)
        controller_name = scene_controller.CONTROLLER_NAME

        def excluded(op):
            if op.GetType() == c4d.Ocamera:
                return True
            if op.GetName() == controller_name:
                return True
            if controller is not None and op == controller:
                return True
            return False

        added = 0
        already = 0
        doc.StartUndo()
        for op in selected:
            if excluded(op):
                continue
            if object_tools.is_orc_object(op):
                already += 1
                continue
            doc.AddUndo(c4d.UNDOTYPE_CHANGE, op)
            if object_tools.add_orc_object_data(op):
                added += 1
        doc.EndUndo()
        c4d.EventAdd()

        log.info("Setup objects: %d configured, %d already set up.", added, already)
        if added == 0 and already == 0:
            c4d.gui.MessageDialog(
                "No eligible objects in the selection "
                "(the controller and cameras are skipped)."
            )
        else:
            c4d.gui.MessageDialog(
                "Set up {0} object(s) as relativistic; {1} already had data.".format(
                    added, already
                )
            )
        return True

    def GetState(self, doc):
        return c4d.CMD_ENABLED


class SelectObjectsCommand(c4d.plugins.CommandData):
    """Select every relativistic object in the active document."""

    def Execute(self, doc):
        if doc is None:
            return False

        objects = object_tools.collect_orc_objects(doc)
        if not objects:
            c4d.gui.MessageDialog("No relativistic objects found in the scene.")
            return True

        for index, op in enumerate(objects):
            mode = c4d.SELECTION_NEW if index == 0 else c4d.SELECTION_ADD
            doc.SetActiveObject(op, mode)
        c4d.EventAdd()

        log.info("Selected %d relativistic object(s).", len(objects))
        return True

    def GetState(self, doc):
        return c4d.CMD_ENABLED
