"""Central Control Panel dialog - one window with buttons for every command.

A compact, non-modal :class:`c4d.gui.GeDialog`. Buttons trigger the already-
registered command plugins via ``c4d.CallCommand`` (so there is no duplicated
logic), and a status read-out shows controller/camera/object/Octane state. Kept
narrow and grouped so it stays short enough for laptop screens.

``import c4d`` here is Cinema 4D's module (this is a GUI-only module, loaded
inside Cinema 4D via the plugin registration).
"""

import c4d

from .. import ids
from ..logging_utils import get_logger
from ..octane import detection as octane_detection
from . import camera_tools, object_tools, scene_controller

log = get_logger("control_panel")


def _status_values():
    """Return ``(controller, camera, object_count, octane)`` status strings."""
    controller = camera = objects = octane = "unknown"
    try:
        doc = c4d.documents.GetActiveDocument()
        controller = "found" if scene_controller.find_controller(doc) else "MISSING"
        cam = camera_tools.find_relativistic_camera(doc)
        camera = cam.GetName() if cam is not None else "MISSING"
        objects = str(len(object_tools.collect_orc_objects(doc)))
    except Exception:  # noqa: BLE001
        pass
    try:
        octane = ("detected" if octane_detection.detect_octane_available()
                  else "not detected")
    except Exception:  # noqa: BLE001
        octane = "unknown"
    return controller, camera, objects, octane


class ControlPanelDialog(c4d.gui.GeDialog):
    """Compact launcher panel with a live status read-out."""

    _ID_STATUS_CONTROLLER = 1001
    _ID_STATUS_CAMERA = 1002
    _ID_STATUS_OBJECTS = 1003
    _ID_STATUS_OCTANE = 1004
    _ID_REFRESH = 1005
    _ID_CLOSE = 1006
    _BUTTON_BASE = 3000

    # (section title, [(button label, command id), ...]) - grouped to stay short.
    _SECTIONS = (
        ("Scene setup", (
            ("Create / Select Controller", ids.COMMAND_CREATE_CONTROLLER),
            ("Setup Relativistic Camera", ids.COMMAND_SETUP_CAMERA),
            ("Setup Selected Objects", ids.COMMAND_SETUP_OBJECTS),
            ("Create Test Scene", ids.COMMAND_CREATE_TEST_SCENE),
        )),
        ("Material preview", (
            ("Apply Doppler Preview", ids.COMMAND_APPLY_DOPPLER),
            ("Apply Searchlight Preview", ids.COMMAND_APPLY_SEARCHLIGHT),
            ("Apply All Material Previews", ids.COMMAND_APPLY_RELATIVITY_PREVIEW),
        )),
        ("Lorentz geometry", (
            ("Create Lorentz Copies", ids.COMMAND_CREATE_LORENTZ),
            ("Remove Lorentz Copies", ids.COMMAND_REMOVE_LORENTZ),
        )),
        ("Octane / export", (
            ("Octane Status", ids.COMMAND_OCTANE_STATUS),
            ("Show AOV Plan", ids.COMMAND_SHOW_AOV_PLAN),
            ("Export Metadata JSON", ids.COMMAND_EXPORT_METADATA),
        )),
        ("Info", (
            ("About", ids.COMMAND_ABOUT),
        )),
    )

    def _add_status_row(self, label, value_id):
        self.AddStaticText(0, c4d.BFH_LEFT, name=label)
        self.AddStaticText(value_id, c4d.BFH_SCALEFIT, name="...")

    def CreateLayout(self):
        self.SetTitle("OpenRelativity C4D - Control Panel")
        self.GroupBorderSpace(6, 6, 6, 6)

        # --- status ---
        self.GroupBegin(0, c4d.BFH_SCALEFIT, 2, 0, "Status")
        self.GroupBorder(c4d.BORDER_GROUP_IN)
        self.GroupBorderSpace(6, 4, 6, 4)
        self._add_status_row("Controller:", self._ID_STATUS_CONTROLLER)
        self._add_status_row("Camera:", self._ID_STATUS_CAMERA)
        self._add_status_row("ORC objects:", self._ID_STATUS_OBJECTS)
        self._add_status_row("Octane:", self._ID_STATUS_OCTANE)
        self.GroupEnd()

        # --- command buttons, grouped, 2 columns each ---
        self._cmd_by_gadget = {}
        gadget_id = self._BUTTON_BASE
        for title, buttons in self._SECTIONS:
            self.GroupBegin(0, c4d.BFH_SCALEFIT, 2, 0, title)
            self.GroupBorder(c4d.BORDER_GROUP_IN)
            self.GroupBorderSpace(6, 4, 6, 4)
            for label, command_id in buttons:
                self.AddButton(gadget_id, c4d.BFH_SCALEFIT, name=label)
                self._cmd_by_gadget[gadget_id] = command_id
                gadget_id += 1
            self.GroupEnd()

        # --- footer ---
        self.GroupBegin(0, c4d.BFH_SCALEFIT, 2, 0, "")
        self.AddButton(self._ID_REFRESH, c4d.BFH_SCALEFIT, name="Refresh")
        self.AddButton(self._ID_CLOSE, c4d.BFH_SCALEFIT, name="Close")
        self.GroupEnd()
        return True

    def InitValues(self):
        self._refresh()
        return True

    def _refresh(self):
        controller, camera, objects, octane = _status_values()
        self.SetString(self._ID_STATUS_CONTROLLER, controller)
        self.SetString(self._ID_STATUS_CAMERA, camera)
        self.SetString(self._ID_STATUS_OBJECTS, objects)
        self.SetString(self._ID_STATUS_OCTANE, octane)

    def Command(self, cid, msg):
        if cid == self._ID_REFRESH:
            self._refresh()
            return True
        if cid == self._ID_CLOSE:
            self.Close()
            return True
        command_id = getattr(self, "_cmd_by_gadget", {}).get(cid)
        if command_id is not None:
            c4d.CallCommand(command_id)
            self._refresh()  # state may have changed
        return True


class ControlPanelCommand(c4d.plugins.CommandData):
    """Open the (async, dockable) Control Panel."""

    dialog = None  # class attribute keeps the async dialog alive

    def Execute(self, doc):
        if self.dialog is None:
            self.dialog = ControlPanelDialog()
        return self.dialog.Open(
            dlgtype=c4d.DLG_TYPE_ASYNC,
            pluginid=ids.DIALOG_CONTROL_PANEL,
            defaultw=300,
            defaulth=0,
        )

    def RestoreLayout(self, sec_ref):
        if self.dialog is None:
            self.dialog = ControlPanelDialog()
        return self.dialog.Restore(pluginid=ids.DIALOG_CONTROL_PANEL, secret=sec_ref)

    def GetState(self, doc):
        return c4d.CMD_ENABLED
