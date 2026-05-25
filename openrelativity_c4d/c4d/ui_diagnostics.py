"""UI Diagnostics - a copyable report for debugging UI / icon / registration.

Registered as *OpenRelativity C4D / Diagnostics / UI Diagnostics*. It opens a
small, fixed-size, **read-only multi-line** dialog (selectable / copyable, and it
scrolls - so the report is never a giant dialog), and also writes the same report
to the console once. The report is fully guarded: any unavailable piece shows as
``unknown`` / ``?`` rather than raising, and Octane is never required.

``import c4d`` here is Cinema 4D's module (GUI-only; loaded inside Cinema 4D).
"""

import c4d

from .. import constants, ids
from ..logging_utils import get_logger
from . import icon_loader, ui_assets, ui_status

log = get_logger("ui_diagnostics")


def _c4d_version():
    try:
        return str(c4d.GetC4DVersion())
    except Exception:  # noqa: BLE001
        return "unknown"


def _command_loaded(command_id):
    """Tri-state: ``True`` registered, ``False`` not found, ``None`` undeterminable."""
    ptype = getattr(c4d, "PLUGINTYPE_COMMANDDATA", None)
    if command_id is None or ptype is None:
        return None
    try:
        return c4d.plugins.FindPlugin(command_id, ptype) is not None
    except Exception:  # noqa: BLE001
        return None


def _mark(state):
    return {True: "OK", False: "--"}.get(state, "??")


def build_report(doc):
    """Return the diagnostics report as a multi-line string. Never raises."""
    try:
        return _build_report(doc)
    except Exception:  # noqa: BLE001
        log.exception("Failed to build the UI diagnostics report.")
        return "Failed to build the UI diagnostics report (see the console)."


def _build_report(doc):
    lines = [
        "OpenRelativity C4D - UI Diagnostics",
        "=" * 46,
        "Plugin version: {0}".format(constants.PLUGIN_VERSION),
        "Plugin root:    {0}".format(icon_loader.get_plugin_root()),
        "C4D version:    {0}".format(_c4d_version()),
        "",
    ]

    # --- commands (real registration check via FindPlugin) -----------------
    specs = ui_assets.COMMANDS
    loaded = sum(1 for s in specs if _command_loaded(ui_assets.command_id(s)) is True)
    lines.append("Commands defined: {0}   loaded (verified): {1}".format(
        len(specs), loaded))
    for spec in specs:
        cid = ui_assets.command_id(spec)
        lines.append("  [{0}] {1!s:>10}  {2}".format(
            _mark(_command_loaded(cid)),
            cid if cid is not None else "?",
            ui_assets.menu_label(spec)))
    lines.append("")

    # --- icons (file found + load result) ----------------------------------
    lines.append("Icons (resources/icons/png):")
    for name in ui_assets.expected_icon_names():
        path = icon_loader.get_icon_path(name)
        found = path is not None
        bitmap = icon_loader.safe_icon(name) if found else None
        if bitmap is not None:
            state, note = "OK", "loaded"
        elif found:
            state, note = "??", "found, not loaded"
        else:
            state, note = "--", "MISSING"
        lines.append("  [{0}] {1}  ({2})".format(state, name, note))
    lines.append("")

    # --- scene status ------------------------------------------------------
    lines.append("Scene status:")
    status = ui_status.collect_status(doc)
    lines.append("  " + status.format_summary().replace("\n", "\n  "))
    return "\n".join(lines)


class UIDiagnosticsDialog(c4d.gui.GeDialog):
    """A small, fixed-size, read-only, scrollable + copyable report dialog."""

    _ID_TEXT = 2000
    _ID_CLOSE = 2001

    def __init__(self, report):
        super(UIDiagnosticsDialog, self).__init__()
        self._report = report

    def CreateLayout(self):
        self.SetTitle("OpenRelativity C4D - UI Diagnostics")
        self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 1, 0, "")
        self.GroupBorderSpace(8, 8, 8, 8)
        style = c4d.DR_MULTILINE_READONLY | c4d.DR_MULTILINE_MONOSPACED
        if hasattr(c4d, "DR_MULTILINE_NO_SYNTAXHIGHLIGHT"):
            style |= c4d.DR_MULTILINE_NO_SYNTAXHIGHLIGHT
        self.AddMultiLineEditText(self._ID_TEXT, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT,
                                  480, 360, style)
        self.AddButton(self._ID_CLOSE, c4d.BFH_CENTER, name="Close")
        self.GroupEnd()
        return True

    def InitValues(self):
        self.SetString(self._ID_TEXT, self._report)
        return True

    def Command(self, cid, msg):
        if cid == self._ID_CLOSE:
            self.Close()
        return True


class UIDiagnosticsCommand(c4d.plugins.CommandData):
    """Open the UI Diagnostics report (copyable dialog + console)."""

    def Execute(self, doc):
        report = build_report(doc)
        log.info("UI Diagnostics report:\n%s", report)  # once, user-initiated
        dialog = UIDiagnosticsDialog(report)
        dialog.Open(
            dlgtype=c4d.DLG_TYPE_MODAL,
            pluginid=ids.ID_ORC_UI_DIAGNOSTICS_DIALOG,
            defaultw=520,
            defaulth=440,
        )
        return True

    def GetState(self, doc):
        return c4d.CMD_ENABLED
