"""Plugin commands (registered under the *Extensions* menu).

* *About* - status dialog (versions, Octane, controller/camera/objects, preview).
* *Create Relativity Controller* - the ``ORC_Relativity_Controller`` Null.
* *Setup Relativistic Camera* - the observer camera.
* *Setup Selected Relativistic Objects* / *Select Relativistic Objects*.
* *Apply Doppler Material Preview* / *Apply Searchlight Preview* /
  *Apply Relativity Material Preview* / *Clear Material Preview* - the
  approximate, non-destructive material previews (see preview_material).
* *Create / Remove Lorentz Preview Copies* - non-destructive contracted
  duplicates (see lorentz_preview).
* *Create Test Scene* / *Apply All Previews* - one-click demo + combined apply
  (see test_scene).
* *Octane Status* / *Apply Octane-Compatible Material Preview* / *Show AOV Plan* /
  *Export Experimental OSL Camera* - Octane detection, material preview (with
  Standard fallback), the AOV plan, and the experimental OSL camera export (see
  the octane package).
* *Export Relativity Metadata JSON* - scene metadata for renderer/post (see the
  export package).
"""

import c4d  # Cinema 4D's module (absolute import; not the sibling sub-package)

from .. import constants, ids
from ..export import metadata_export
from ..logging_utils import get_logger
from ..octane import adapter as octane_adapter
from ..octane import aov_adapter as octane_aov
from ..octane import detection as octane_detection
from ..octane import osl_camera as octane_osl
from . import (
    camera_tools,
    lorentz_preview,
    object_tools,
    preview_material,
    scene_controller,
    test_scene,
)

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
        return ("detected" if octane_detection.detect_octane_available()
                else "not detected")
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


def _preview_status():
    """Return the count of active relativity preview materials."""
    try:
        doc = c4d.documents.GetActiveDocument()
        return "{0} preview material(s)".format(
            preview_material.count_preview_materials(doc))
    except Exception:  # noqa: BLE001
        return "unknown"


def _lorentz_status():
    """Return the count of Lorentz preview copies."""
    try:
        doc = c4d.documents.GetActiveDocument()
        return "{0} preview copy(ies)".format(
            lorentz_preview.count_preview_copies(doc))
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
        "Preview:        {0}".format(_preview_status()),
        "Lorentz:        {0}".format(_lorentz_status()),
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


def _apply_preview_message(count, status, what):
    """Show the standard apply-result dialog."""
    if status == "disabled":
        c4d.gui.MessageDialog(
            "The Relativity Controller is disabled (Enabled = off).\n"
            "Nothing was applied."
        )
    elif status == "no_objects":
        c4d.gui.MessageDialog(
            "No relativistic objects found.\n"
            "Run 'Setup Selected Relativistic Objects' first."
        )
    else:
        c4d.gui.MessageDialog(
            "Applied the {0} to {1} object(s).\n"
            "This is an artistic approximation (see docs/), not spectral or "
            "radiometric rendering.".format(what, count)
        )


class ApplyDopplerPreviewCommand(c4d.plugins.CommandData):
    """Apply the approximate Doppler colour preview only."""

    def Execute(self, doc):
        if doc is None:
            return False
        count, status = preview_material.apply_preview(
            doc, do_doppler=True, do_searchlight=False)
        _apply_preview_message(count, status, "Doppler material preview")
        return True

    def GetState(self, doc):
        return c4d.CMD_ENABLED


class ApplySearchlightPreviewCommand(c4d.plugins.CommandData):
    """Apply the approximate searchlight (beaming) brightness preview only."""

    def Execute(self, doc):
        if doc is None:
            return False
        count, status = preview_material.apply_preview(
            doc, do_doppler=False, do_searchlight=True)
        _apply_preview_message(count, status, "searchlight brightness preview")
        return True

    def GetState(self, doc):
        return c4d.CMD_ENABLED


class ApplyRelativityMaterialPreviewCommand(c4d.plugins.CommandData):
    """Apply both the Doppler tint and the searchlight brightness together."""

    def Execute(self, doc):
        if doc is None:
            return False
        count, status = preview_material.apply_preview(
            doc, do_doppler=True, do_searchlight=True)
        _apply_preview_message(count, status, "relativity material preview (Doppler + searchlight)")
        return True

    def GetState(self, doc):
        return c4d.CMD_ENABLED


class ClearMaterialPreviewCommand(c4d.plugins.CommandData):
    """Remove all ORC-generated preview materials and tags (Doppler + searchlight)."""

    def Execute(self, doc):
        if doc is None:
            return False

        tags, materials = preview_material.clear_preview(doc)
        if tags == 0 and materials == 0:
            c4d.gui.MessageDialog("No relativity material preview to clear.")
        else:
            c4d.gui.MessageDialog(
                "Cleared the material preview: removed {0} tag(s) and "
                "{1} material(s). Original materials were left untouched.".format(
                    tags, materials
                )
            )
        return True

    def GetState(self, doc):
        return c4d.CMD_ENABLED


class CreateLorentzPreviewCommand(c4d.plugins.CommandData):
    """Create non-destructive, contracted duplicate copies for Lorentz preview."""

    def Execute(self, doc):
        if doc is None:
            return False

        count, status = lorentz_preview.create_preview(doc)
        if status == "disabled":
            c4d.gui.MessageDialog(
                "The Relativity Controller is disabled (Enabled = off).\n"
                "Nothing was created."
            )
        elif status == "no_objects":
            c4d.gui.MessageDialog(
                "No relativistic objects found.\n"
                "Run 'Setup Selected Relativistic Objects' first."
            )
        else:
            c4d.gui.MessageDialog(
                "Created {0} Lorentz preview copy(ies) "
                "('ORC_LorentzPreview_<name>').\n"
                "Axis-aligned length-contraction approximation only - no Terrell "
                "rotation / apparent geometry yet (see docs/LORENTZ_PREVIEW.md). "
                "Originals are unchanged; use 'Remove Lorentz Preview Copies' to "
                "restore.".format(count)
            )
        return True

    def GetState(self, doc):
        return c4d.CMD_ENABLED


class RemoveLorentzPreviewCommand(c4d.plugins.CommandData):
    """Remove Lorentz preview copies and restore the originals' visibility."""

    def Execute(self, doc):
        if doc is None:
            return False

        removed = lorentz_preview.remove_preview(doc)
        if removed == 0:
            c4d.gui.MessageDialog("No Lorentz preview copies to remove.")
        else:
            c4d.gui.MessageDialog(
                "Removed {0} Lorentz preview copy(ies); originals restored.".format(
                    removed
                )
            )
        return True

    def GetState(self, doc):
        return c4d.CMD_ENABLED


class CreateTestSceneCommand(c4d.plugins.CommandData):
    """Build a ready-to-preview demo scene (controller, camera, test objects)."""

    def Execute(self, doc):
        if doc is None:
            return False

        result = test_scene.create_test_scene(doc)
        if result is None:
            c4d.gui.MessageDialog("Failed to create the test scene.")
            return False

        group, _suffix = result
        c4d.gui.MessageDialog(
            "Created test scene '{0}': a Relativity Controller, a relativistic "
            "camera, four test objects (approaching / receding / lateral / "
            "static) and a light.\n\n"
            "Next: run 'Apply All Previews', then render with Standard or "
            "Physical. See docs/QUICKSTART.md.".format(group.GetName())
        )
        return True

    def GetState(self, doc):
        return c4d.CMD_ENABLED


class ApplyAllPreviewsCommand(c4d.plugins.CommandData):
    """Apply the material preview (Doppler + searchlight) and Lorentz copies."""

    def Execute(self, doc):
        if doc is None:
            return False

        # Materials first, so the Lorentz clones inherit the preview material.
        mat_count, mat_status = preview_material.apply_preview(
            doc, do_doppler=True, do_searchlight=True)
        lorentz_count, lorentz_status = lorentz_preview.create_preview(doc)

        if mat_status == "disabled":
            c4d.gui.MessageDialog(
                "The Relativity Controller is disabled (Enabled = off).\n"
                "Nothing was applied."
            )
            return True
        if mat_status == "no_objects" and lorentz_status == "no_objects":
            c4d.gui.MessageDialog(
                "No relativistic objects found.\n"
                "Run 'Create Test Scene' or 'Setup Selected Relativistic "
                "Objects' first."
            )
            return True

        c4d.gui.MessageDialog(
            "Applied the material preview to {0} object(s) and created {1} "
            "Lorentz preview copy(ies).\n\n"
            "These are artistic approximations (not spectral/radiometric). "
            "Render with Standard or Physical.".format(mat_count, lorentz_count)
        )
        return True

    def GetState(self, doc):
        return c4d.CMD_ENABLED


class OctaneStatusCommand(c4d.plugins.CommandData):
    """Report Octane availability/status (detection only; no Octane changes)."""

    def Execute(self, doc):
        report = octane_detection.get_octane_status_report(doc)
        c4d.gui.MessageDialog(
            "OpenRelativity C4D - Octane Status\n\n"
            + octane_detection.format_status_report(report)
        )
        return True

    def GetState(self, doc):
        return c4d.CMD_ENABLED


class ApplyOctaneCompatibleMaterialPreviewCommand(c4d.plugins.CommandData):
    """Apply the combined preview via Octane if supported, else Standard fallback."""

    def Execute(self, doc):
        if doc is None:
            return False

        tally = {}
        warnings_seen = []

        def writer(d, obj, color, multiplier):
            result = octane_adapter.apply_octane_or_fallback_material(
                d, obj, color, multiplier)
            method = result.get("method", "error")
            tally[method] = tally.get(method, 0) + 1
            for warning in result.get("warnings", []):
                if warning not in warnings_seen:
                    warnings_seen.append(warning)

        count, status = preview_material.apply_preview(
            doc, do_doppler=True, do_searchlight=True, writer=writer)

        if status == "disabled":
            c4d.gui.MessageDialog(
                "The Relativity Controller is disabled (Enabled = off).\n"
                "Nothing was applied."
            )
            return True
        if status == "no_objects":
            c4d.gui.MessageDialog(
                "No relativistic objects found.\n"
                "Run 'Create Test Scene' or 'Setup Selected Relativistic "
                "Objects' first."
            )
            return True

        octane_n = tally.get("octane", 0)
        fallback_n = tally.get("fallback", 0)
        error_n = tally.get("error", 0)
        lines = [
            "Octane-compatible material preview applied to {0} object(s):".format(count),
            "  - via Octane material: {0}".format(octane_n),
            "  - via Standard fallback: {0}".format(fallback_n),
        ]
        if error_n:
            lines.append("  - failed: {0}".format(error_n))
        if warnings_seen:
            lines.append("")
            lines.append("Notes:")
            lines.extend("- " + warning for warning in warnings_seen)
        c4d.gui.MessageDialog("\n".join(lines))
        return True

    def GetState(self, doc):
        return c4d.CMD_ENABLED


class ShowAOVPlanCommand(c4d.plugins.CommandData):
    """Show the desired Relativity AOVs and whether auto-creation is supported."""

    def Execute(self, doc):
        plan = octane_aov.get_relativity_aov_plan()
        render_info = octane_aov.detect_render_settings(doc)
        c4d.gui.MessageDialog(
            "OpenRelativity C4D - AOV Plan\n\n"
            + octane_aov.format_aov_plan(plan, render_info)
        )
        return True

    def GetState(self, doc):
        return c4d.CMD_ENABLED


class ExportMetadataCommand(c4d.plugins.CommandData):
    """Export the scene's relativity metadata to a JSON file."""

    def Execute(self, doc):
        if doc is None:
            return False

        def_path = ""
        try:
            def_path = doc.GetDocumentPath() or ""
        except Exception:  # noqa: BLE001
            def_path = ""

        path = c4d.storage.SaveDialog(
            title="Export Relativity Metadata JSON",
            force_suffix="json",
            def_path=def_path,
            def_file=metadata_export.default_filename(doc),
        )
        if not path:
            return True  # user cancelled

        result = metadata_export.export_metadata_json(doc, path)
        if result["ok"]:
            c4d.gui.MessageDialog(
                "Exported relativity metadata for {0} object(s) to:\n{1}\n\n"
                "Schema: docs/METADATA_SCHEMA.md (values are artistic "
                "approximations).".format(result["object_count"], result["path"]))
        else:
            c4d.gui.MessageDialog(
                "Failed to export metadata:\n{0}".format(result["error"]))
        return True

    def GetState(self, doc):
        return c4d.CMD_ENABLED


class ExportOSLCameraCommand(c4d.plugins.CommandData):
    """Export the experimental OSL camera shader to a user-selected file."""

    def Execute(self, doc):
        path = c4d.storage.SaveDialog(
            title="Export Experimental OSL Camera Shader",
            force_suffix="osl",
            def_file=octane_osl.OSL_FILENAME,
        )
        if not path:
            return True  # user cancelled

        result = octane_osl.export_osl_camera(path)
        if result["ok"]:
            c4d.gui.MessageDialog(
                "Wrote the EXPERIMENTAL OSL camera shader to:\n{0}\n\n"
                "This is a physically-incomplete placeholder and is NOT wired "
                "into Octane. See docs/OSL_CAMERA_EXPERIMENTS.md for how to "
                "experiment with it.".format(result["path"])
            )
        else:
            c4d.gui.MessageDialog(
                "Failed to write the OSL shader:\n{0}".format(result["error"]))
        return True

    def GetState(self, doc):
        return c4d.CMD_ENABLED
