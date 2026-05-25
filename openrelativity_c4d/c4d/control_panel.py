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

    # (section title, [(button label, command id), ...]). Button labels match the
    # registered command names (minus the "OpenRelativity C4D: " prefix) for
    # consistency; grouped into sections to stay compact.
    _SECTIONS = (
        ("Scene setup", (
            ("Create Relativity Controller", ids.ID_ORC_CREATE_CONTROLLER_COMMAND),
            ("Setup Relativistic Camera", ids.ID_ORC_SETUP_CAMERA_COMMAND),
            ("Setup Selected Relativistic Objects", ids.ID_ORC_SETUP_OBJECTS_COMMAND),
            ("Create Test Scene", ids.ID_ORC_CREATE_TEST_SCENE_COMMAND),
        )),
        ("Material preview", (
            ("Apply Doppler Material Preview", ids.ID_ORC_APPLY_DOPPLER_PREVIEW_COMMAND),
            ("Apply Searchlight Preview", ids.ID_ORC_APPLY_SEARCHLIGHT_PREVIEW_COMMAND),
            ("Apply Relativity Material Preview", ids.ID_ORC_APPLY_RELATIVITY_PREVIEW_COMMAND),
            ("Clear Material Preview", ids.ID_ORC_CLEAR_PREVIEW_COMMAND),
        )),
        ("Lorentz geometry", (
            ("Create Lorentz Preview Copies", ids.ID_ORC_CREATE_LORENTZ_PREVIEWS_COMMAND),
            ("Remove Lorentz Preview Copies", ids.ID_ORC_REMOVE_LORENTZ_PREVIEWS_COMMAND),
        )),
        ("Octane / export", (
            ("Octane Status", ids.ID_ORC_OCTANE_STATUS_COMMAND),
            ("Octane Diagnostics", ids.ID_ORC_OCTANE_DIAGNOSTICS_COMMAND),
            ("Show AOV Plan", ids.ID_ORC_SHOW_AOV_PLAN_COMMAND),
            ("Export Relativity Metadata JSON", ids.ID_ORC_EXPORT_METADATA_COMMAND),
        )),
        ("Info", (
            ("About", ids.ID_ORC_ABOUT_COMMAND),
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
            pluginid=ids.ID_ORC_CONTROL_PANEL_DIALOG,
            defaultw=300,
            defaulth=0,
        )

    def RestoreLayout(self, sec_ref):
        if self.dialog is None:
            self.dialog = ControlPanelDialog()
        return self.dialog.Restore(pluginid=ids.ID_ORC_CONTROL_PANEL_DIALOG, secret=sec_ref)

    def GetState(self, doc):
        return c4d.CMD_ENABLED
