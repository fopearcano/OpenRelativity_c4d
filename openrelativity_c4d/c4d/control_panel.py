"""Central Control Panel dialog - a compact, tabbed launcher for every command.

A non-modal :class:`c4d.gui.GeDialog` organised into workflow tabs (Setup,
Preview, Octane, Export, Diagnostics/Help) with a persistent status read-out.
Buttons trigger the already-registered command plugins via ``c4d.CallCommand`` -
there is **no duplicated command logic and no behavior change**; the panel is just
a launcher. Tabs keep it short enough for laptop screens (only one section's
buttons are visible at a time).

Each command shows an optional small icon (via :mod:`.icon_loader`); if an icon is
missing or Cinema 4D's bitmap-button GUI is unavailable, the button degrades to a
plain text button - the click target is always a real text button, so commands
remain reachable regardless of icons.

``import c4d`` here is Cinema 4D's module (this is a GUI-only module, loaded inside
Cinema 4D via the plugin registration).
"""

import os

import c4d

from .. import constants, ids
from ..logging_utils import get_logger
from . import icon_loader, ui_status

log = get_logger("control_panel")


class ControlPanelDialog(c4d.gui.GeDialog):
    """Compact, tabbed launcher panel with a live status read-out."""

    # --- gadget IDs (all dialog widget IDs are defined here, centrally) -----
    _ID_TABS = 1000
    _ID_TAB_SETUP = 1001
    _ID_TAB_PREVIEW = 1002
    _ID_TAB_OCTANE = 1003
    _ID_TAB_EXPORT = 1004
    _ID_TAB_DIAG = 1005

    _ID_STATUS_GROUP = 1010
    _ID_STATUS_CONTROLLER = 1011
    _ID_STATUS_CAMERA = 1012
    _ID_STATUS_OBJECTS = 1013
    _ID_STATUS_OCTANE = 1014
    _ID_STATUS_LAST = 1015
    _ID_STATUS_GENERATED = 1016

    _ID_REFRESH = 1020
    _ID_CLOSE = 1021
    _ID_UI_DIAGNOSTICS = 1022
    _ID_OPEN_DOCS = 1023

    #: Dynamically-assigned command/icon gadget IDs start here (one block).
    _GADGET_BASE = 2000

    def __init__(self):
        super(ControlPanelDialog, self).__init__()
        self._cmd_by_gadget = {}   # gadget id -> (command id, label)
        self._icon_guis = {}       # gadget id -> BitmapButton (kept alive)
        self._next_id = self._GADGET_BASE
        self._last_action = "(none yet)"

    # --- small layout helpers ----------------------------------------------
    def _new_gadget_id(self):
        gid = self._next_id
        self._next_id += 1
        return gid

    def _add_icon(self, gadget_id, icon_name, clickable):
        """Add a small icon bitmap-button for ``icon_name``; return ``True`` if added.

        Fully guarded: returns ``False`` (adds nothing) if the icon is missing or
        the bitmap-button custom GUI is unavailable, so callers fall back to a
        text-only button. ``clickable`` makes the icon itself a button (a bonus
        click target for command rows); decorative icons pass ``False``.
        """
        if not icon_name:
            return False
        try:
            bitmap = icon_loader.safe_icon(icon_name)
        except Exception:  # noqa: BLE001
            bitmap = None
        if bitmap is None:
            return False
        cgui = getattr(c4d, "CUSTOMGUI_BITMAPBUTTON", None)
        if cgui is None:
            return False
        try:
            settings = c4d.BaseContainer()
            if hasattr(c4d, "BITMAPBUTTON_BUTTON"):
                settings.SetBool(c4d.BITMAPBUTTON_BUTTON, bool(clickable))
            if hasattr(c4d, "BITMAPBUTTON_TOGGLE"):
                settings.SetBool(c4d.BITMAPBUTTON_TOGGLE, False)
            gui = self.AddCustomGui(gadget_id, cgui, "",
                                    c4d.BFH_LEFT | c4d.BFV_CENTER, 22, 22, settings)
            if gui is None:
                return False
            try:
                gui.SetImage(bitmap, False)
            except Exception:  # noqa: BLE001 - gadget exists; just no image
                pass
            self._icon_guis[gadget_id] = gui
            return True
        except Exception:  # noqa: BLE001
            log.debug("Icon button '%s' failed; using text only.", icon_name,
                      exc_info=True)
            return False

    def _add_command(self, label, command_id, icon_name):
        """Add an ``[icon] [text button]`` row that runs ``command_id``.

        The text button is always present (reliable click target); the icon is a
        bonus, also mapped to the command when shown. A placeholder keeps the
        2-column grid aligned when no icon is available.
        """
        icon_gid = self._new_gadget_id()
        if self._add_icon(icon_gid, icon_name, clickable=True):
            self._cmd_by_gadget[icon_gid] = (command_id, label)
        else:
            self.AddStaticText(0, c4d.BFH_LEFT, name="")
        btn_gid = self._new_gadget_id()
        self.AddButton(btn_gid, c4d.BFH_SCALEFIT, name=label)
        self._cmd_by_gadget[btn_gid] = (command_id, label)

    def _add_local(self, label, gadget_id, icon_name):
        """Add an ``[icon] [text button]`` row for a panel-local action.

        The fixed ``gadget_id`` is handled directly in :meth:`Command` (not via
        ``CallCommand``); the icon is decorative.
        """
        icon_gid = self._new_gadget_id()
        if not self._add_icon(icon_gid, icon_name, clickable=False):
            self.AddStaticText(0, c4d.BFH_LEFT, name="")
        self.AddButton(gadget_id, c4d.BFH_SCALEFIT, name=label)

    def _begin_tab(self, tab_id, title):
        self.GroupBegin(tab_id, c4d.BFH_SCALEFIT | c4d.BFV_TOP, 2, 0, title)
        self.GroupBorderSpace(8, 6, 8, 6)

    # --- status area (always visible, top) ---------------------------------
    def build_status_area(self):
        self.GroupBegin(self._ID_STATUS_GROUP, c4d.BFH_SCALEFIT, 4, 0, "Status")
        self.GroupBorder(c4d.BORDER_GROUP_IN)
        self.GroupBorderSpace(6, 4, 6, 4)
        self.AddStaticText(0, c4d.BFH_LEFT, name="Controller:")
        self.AddStaticText(self._ID_STATUS_CONTROLLER, c4d.BFH_SCALEFIT, name="...")
        self.AddStaticText(0, c4d.BFH_LEFT, name="Camera:")
        self.AddStaticText(self._ID_STATUS_CAMERA, c4d.BFH_SCALEFIT, name="...")
        self.AddStaticText(0, c4d.BFH_LEFT, name="Objects:")
        self.AddStaticText(self._ID_STATUS_OBJECTS, c4d.BFH_SCALEFIT, name="...")
        self.AddStaticText(0, c4d.BFH_LEFT, name="Octane:")
        self.AddStaticText(self._ID_STATUS_OCTANE, c4d.BFH_SCALEFIT, name="...")
        self.GroupEnd()

        self.GroupBegin(0, c4d.BFH_SCALEFIT, 2, 0, "")
        self.GroupBorderSpace(6, 0, 6, 2)
        self.AddStaticText(0, c4d.BFH_LEFT, name="Generated:")
        self.AddStaticText(self._ID_STATUS_GENERATED, c4d.BFH_SCALEFIT, name="...")
        self.AddStaticText(0, c4d.BFH_LEFT, name="Last:")
        self.AddStaticText(self._ID_STATUS_LAST, c4d.BFH_SCALEFIT, name="(none yet)")
        self.GroupEnd()

    # --- tabs ---------------------------------------------------------------
    def build_setup_tab(self):
        self._begin_tab(self._ID_TAB_SETUP, "Setup")
        self._add_command("Create Controller",
                          ids.ID_ORC_CREATE_CONTROLLER_COMMAND, "icon_setup_controller")
        self._add_command("Setup Camera",
                          ids.ID_ORC_SETUP_CAMERA_COMMAND, "icon_setup_camera")
        self._add_command("Setup Selected Objects",
                          ids.ID_ORC_SETUP_OBJECTS_COMMAND, "icon_setup_objects")
        self._add_command("Select Objects",
                          ids.ID_ORC_SELECT_OBJECTS_COMMAND, "icon_setup_objects")
        self._add_command("Create Test Scene",
                          ids.ID_ORC_CREATE_TEST_SCENE_COMMAND, "icon_create_test_scene")
        self.GroupEnd()

    def build_preview_tab(self):
        self._begin_tab(self._ID_TAB_PREVIEW, "Preview")
        self._add_command("Apply Doppler",
                          ids.ID_ORC_APPLY_DOPPLER_PREVIEW_COMMAND, "icon_doppler_preview")
        self._add_command("Apply Searchlight",
                          ids.ID_ORC_APPLY_SEARCHLIGHT_PREVIEW_COMMAND, "icon_searchlight_preview")
        self._add_command("Apply All Materials",
                          ids.ID_ORC_APPLY_RELATIVITY_PREVIEW_COMMAND, "icon_all_previews")
        self._add_command("Apply All (+ Lorentz)",
                          ids.ID_ORC_APPLY_ALL_PREVIEWS_COMMAND, "icon_all_previews")
        self._add_command("Clear Generated Materials",
                          ids.ID_ORC_CLEAR_PREVIEW_COMMAND, "icon_lorentz_remove")
        self._add_command("Create Lorentz Copies",
                          ids.ID_ORC_CREATE_LORENTZ_PREVIEWS_COMMAND, "icon_lorentz_create")
        self._add_command("Remove Lorentz Copies",
                          ids.ID_ORC_REMOVE_LORENTZ_PREVIEWS_COMMAND, "icon_lorentz_remove")
        self.GroupEnd()

    def build_octane_tab(self):
        self._begin_tab(self._ID_TAB_OCTANE, "Octane")
        self._add_command("Status",
                          ids.ID_ORC_OCTANE_STATUS_COMMAND, "icon_octane_status")
        self._add_command("Apply Compatible Preview",
                          ids.ID_ORC_APPLY_OCTANE_MATERIAL_COMMAND, "icon_octane_status")
        self._add_command("Show AOV Plan",
                          ids.ID_ORC_SHOW_AOV_PLAN_COMMAND, "icon_aov_plan")
        self._add_command("Export OSL Camera",
                          ids.ID_ORC_EXPORT_OSL_CAMERA_COMMAND, "icon_export_osl")
        self.GroupEnd()

    def build_export_tab(self):
        self._begin_tab(self._ID_TAB_EXPORT, "Export")
        self._add_command("Metadata JSON",
                          ids.ID_ORC_EXPORT_METADATA_COMMAND, "icon_export_metadata")
        self.AddStaticText(0, c4d.BFH_LEFT, name="")
        self.AddStaticText(0, c4d.BFH_SCALEFIT,
                           name="Writes a JSON sidecar (docs/METADATA_SCHEMA.md).")
        self.GroupEnd()

    def build_diagnostics_tab(self):
        self._begin_tab(self._ID_TAB_DIAG, "Help")
        self._add_command("About", ids.ID_ORC_ABOUT_COMMAND, "icon_about")
        self._add_command("Octane Diagnostics",
                          ids.ID_ORC_OCTANE_DIAGNOSTICS_COMMAND, "icon_diagnostics")
        self._add_local("UI Diagnostics", self._ID_UI_DIAGNOSTICS, "icon_diagnostics")
        self._add_local("Open Docs Folder", self._ID_OPEN_DOCS, "icon_control_panel")
        self.GroupEnd()

    def build_footer(self):
        self.GroupBegin(0, c4d.BFH_SCALEFIT, 2, 0, "")
        self.AddButton(self._ID_REFRESH, c4d.BFH_SCALEFIT, name="Refresh Status")
        self.AddButton(self._ID_CLOSE, c4d.BFH_SCALEFIT, name="Close")
        self.GroupEnd()

    # --- GeDialog overrides -------------------------------------------------
    def CreateLayout(self):
        self.SetTitle("OpenRelativity C4D - Control Panel")
        self._cmd_by_gadget = {}
        self._icon_guis = {}
        self._next_id = self._GADGET_BASE
        self.GroupBorderSpace(6, 6, 6, 6)

        self.build_status_area()

        self.TabGroupBegin(self._ID_TABS, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT,
                           getattr(c4d, "TAB_TABS", 0))
        self.build_setup_tab()
        self.build_preview_tab()
        self.build_octane_tab()
        self.build_export_tab()
        self.build_diagnostics_tab()
        self.GroupEnd()  # tab group

        self.build_footer()
        return True

    def InitValues(self):
        self.refresh_status()
        return True

    def refresh_status(self):
        status = ui_status.collect_status(self._active_doc(), self._last_action)
        try:
            self.SetString(self._ID_STATUS_CONTROLLER, status.controller_label())
            self.SetString(self._ID_STATUS_CAMERA, status.camera_label())
            self.SetString(self._ID_STATUS_OBJECTS, status.objects_label())
            self.SetString(self._ID_STATUS_OCTANE, status.octane_label())
            self.SetString(self._ID_STATUS_GENERATED, status.generated_label())
            self.SetString(self._ID_STATUS_LAST, status.last_label())
        except Exception:  # noqa: BLE001 - a status refresh must never crash the dialog
            log.debug("Status refresh failed.", exc_info=True)

    def Command(self, cid, msg):
        if cid == self._ID_REFRESH:
            self.refresh_status()
            return True
        if cid == self._ID_CLOSE:
            self.Close()
            return True
        if cid == self._ID_UI_DIAGNOSTICS:
            self._show_ui_diagnostics()
            return True
        if cid == self._ID_OPEN_DOCS:
            self._open_docs_folder()
            return True
        entry = self._cmd_by_gadget.get(cid)
        if entry is not None:
            command_id, label = entry
            try:
                c4d.CallCommand(command_id)  # runs the real command (unchanged behavior)
                self._last_action = "Ran: {0}".format(label)
            except Exception:  # noqa: BLE001 - keep the dialog alive on a failing command
                log.exception("Control Panel command '%s' (id=%s) failed.",
                              label, command_id)
                self._last_action = "Error: '{0}' failed (see console)".format(label)
            self.refresh_status()
        return True

    # --- panel-local helpers ------------------------------------------------
    @staticmethod
    def _active_doc():
        try:
            return c4d.documents.GetActiveDocument()
        except Exception:  # noqa: BLE001
            return None

    def _show_ui_diagnostics(self):
        """Read-only: show scene status and the icon load summary in a dialog."""
        status = ui_status.collect_status(self._active_doc(), self._last_action)
        c4d.gui.MessageDialog(
            "OpenRelativity C4D - UI diagnostics\n\n"
            + status.format_summary()
            + "\n\n"
            + icon_loader.format_load_summary())
        self._last_action = "UI diagnostics"
        self.refresh_status()

    def _open_docs_folder(self):
        """Best-effort: open the repo ``docs/`` folder; fall back to showing its path."""
        root = icon_loader.get_plugin_root()
        candidates = [os.path.join(os.path.dirname(root), "docs"),
                      os.path.join(root, "docs")]
        path = next((p for p in candidates if os.path.isdir(p)), None)
        if path is None:
            c4d.gui.MessageDialog(
                "Docs folder not found next to the plugin.\nProject page:\n"
                + constants.PROJECT_URL)
            self._last_action = "Open docs (not found)"
            self.refresh_status()
            return
        opened = False
        try:
            execute = getattr(c4d.storage, "GeExecuteFile", None)
            if execute is not None:
                opened = bool(execute(path))
        except Exception:  # noqa: BLE001
            opened = False
        if not opened:
            c4d.gui.MessageDialog("Docs are here:\n{0}".format(path))
        self._last_action = "Opened docs folder" if opened else "Showed docs path"
        self.refresh_status()


class ControlPanelCommand(c4d.plugins.CommandData):
    """Open the (async, dockable) Control Panel."""

    dialog = None  # class attribute keeps the async dialog alive

    def Execute(self, doc):
        if self.dialog is None:
            self.dialog = ControlPanelDialog()
        return self.dialog.Open(
            dlgtype=c4d.DLG_TYPE_ASYNC,
            pluginid=ids.ID_ORC_CONTROL_PANEL_DIALOG,
            defaultw=340,
            defaulth=0,
        )

    def RestoreLayout(self, sec_ref):
        if self.dialog is None:
            self.dialog = ControlPanelDialog()
        return self.dialog.Restore(pluginid=ids.ID_ORC_CONTROL_PANEL_DIALOG, secret=sec_ref)

    def GetState(self, doc):
        return c4d.CMD_ENABLED
