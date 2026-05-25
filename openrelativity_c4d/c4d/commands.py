"""The "About" command and its dialog (the only functional UI in this skeleton).

Adds *Extensions > OpenRelativity C4D: About*, which opens a small modal dialog
showing the plugin version, the target Cinema 4D version, the running build, the
current development status, and whether an Octane integration was detected.
"""

import c4d  # Cinema 4D's module (absolute import; not the sibling sub-package)

from .. import constants, ids
from ..logging_utils import get_logger

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


def about_info_lines():
    """Build the list of text lines shown in the About dialog."""
    return [
        constants.TAGLINE,
        "",
        "Version:        {0}".format(constants.PLUGIN_VERSION),
        "Target C4D:     Cinema 4D {0}".format(constants.TARGET_C4D_VERSION),
        "Running build:  {0}".format(_c4d_build()),
        "Octane:         {0}".format(_octane_status()),
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
