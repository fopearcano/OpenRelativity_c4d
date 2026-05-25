"""Registration of Cinema 4D plugin elements.

:func:`register_all` is called from :mod:`openrelativity_c4d.bootstrap` inside
Cinema 4D and registers every command plugin (About, controller/camera/object
setup, the previews, Octane utilities, metadata export, and the Control Panel).
"""

import c4d  # Cinema 4D's module

from .. import constants, ids
from ..logging_utils import get_logger
from . import commands, control_panel, icon_loader

log = get_logger("register")


def register_all():
    """Register every plugin element. Returns ``True`` if all succeeded."""
    ok = True

    # --- About command -----------------------------------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.ID_ORC_ABOUT_COMMAND,
        str="{0}: About".format(constants.PLUGIN_NAME),
        info=0,
        icon=icon_loader.safe_icon("icon_about"),
        help="Show information about {0}.".format(constants.PLUGIN_NAME),
        dat=commands.AboutCommand(),
    )
    if registered:
        log.info("Registered command 'About' (id=%s).", ids.ID_ORC_ABOUT_COMMAND)
    else:
        log.error("Failed to register the 'About' command (id=%s).", ids.ID_ORC_ABOUT_COMMAND)
        ok = False

    # --- Create Relativity Controller command ------------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.ID_ORC_CREATE_CONTROLLER_COMMAND,
        str="{0}: Create Relativity Controller".format(constants.PLUGIN_NAME),
        info=0,
        icon=icon_loader.safe_icon("icon_setup_controller"),
        help="Create the ORC_Relativity_Controller Null with relativity settings.",
        dat=commands.CreateControllerCommand(),
    )
    if registered:
        log.info("Registered 'Create Relativity Controller' (id=%s).",
                 ids.ID_ORC_CREATE_CONTROLLER_COMMAND)
    else:
        log.error("Failed to register 'Create Relativity Controller' (id=%s).",
                  ids.ID_ORC_CREATE_CONTROLLER_COMMAND)
        ok = False

    # --- Setup Relativistic Camera command ---------------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.ID_ORC_SETUP_CAMERA_COMMAND,
        str="{0}: Setup Relativistic Camera".format(constants.PLUGIN_NAME),
        info=0,
        icon=icon_loader.safe_icon("icon_setup_camera"),
        help="Configure the selected camera (or create one) as a relativistic observer.",
        dat=commands.SetupCameraCommand(),
    )
    if registered:
        log.info("Registered 'Setup Relativistic Camera' (id=%s).",
                 ids.ID_ORC_SETUP_CAMERA_COMMAND)
    else:
        log.error("Failed to register 'Setup Relativistic Camera' (id=%s).",
                  ids.ID_ORC_SETUP_CAMERA_COMMAND)
        ok = False

    # --- Setup Selected Relativistic Objects command -----------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.ID_ORC_SETUP_OBJECTS_COMMAND,
        str="{0}: Setup Selected Relativistic Objects".format(constants.PLUGIN_NAME),
        info=0,
        icon=icon_loader.safe_icon("icon_setup_objects"),
        help="Add relativistic User Data to the selected objects.",
        dat=commands.SetupObjectsCommand(),
    )
    if registered:
        log.info("Registered 'Setup Selected Relativistic Objects' (id=%s).",
                 ids.ID_ORC_SETUP_OBJECTS_COMMAND)
    else:
        log.error("Failed to register 'Setup Selected Relativistic Objects' (id=%s).",
                  ids.ID_ORC_SETUP_OBJECTS_COMMAND)
        ok = False

    # --- Select Relativistic Objects command -------------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.ID_ORC_SELECT_OBJECTS_COMMAND,
        str="{0}: Select Relativistic Objects".format(constants.PLUGIN_NAME),
        info=0,
        icon=icon_loader.safe_icon("icon_setup_objects"),
        help="Select every object that has relativistic User Data.",
        dat=commands.SelectObjectsCommand(),
    )
    if registered:
        log.info("Registered 'Select Relativistic Objects' (id=%s).",
                 ids.ID_ORC_SELECT_OBJECTS_COMMAND)
    else:
        log.error("Failed to register 'Select Relativistic Objects' (id=%s).",
                  ids.ID_ORC_SELECT_OBJECTS_COMMAND)
        ok = False

    # --- Apply Doppler Material Preview command ----------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.ID_ORC_APPLY_DOPPLER_PREVIEW_COMMAND,
        str="{0}: Apply Doppler Material Preview".format(constants.PLUGIN_NAME),
        info=0,
        icon=icon_loader.safe_icon("icon_doppler_preview"),
        help="Apply the approximate Doppler colour preview to relativistic objects.",
        dat=commands.ApplyDopplerPreviewCommand(),
    )
    if registered:
        log.info("Registered 'Apply Doppler Material Preview' (id=%s).",
                 ids.ID_ORC_APPLY_DOPPLER_PREVIEW_COMMAND)
    else:
        log.error("Failed to register 'Apply Doppler Material Preview' (id=%s).",
                  ids.ID_ORC_APPLY_DOPPLER_PREVIEW_COMMAND)
        ok = False

    # --- Apply Searchlight Preview command ---------------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.ID_ORC_APPLY_SEARCHLIGHT_PREVIEW_COMMAND,
        str="{0}: Apply Searchlight Preview".format(constants.PLUGIN_NAME),
        info=0,
        icon=icon_loader.safe_icon("icon_searchlight_preview"),
        help="Apply the approximate searchlight (beaming) brightness preview.",
        dat=commands.ApplySearchlightPreviewCommand(),
    )
    if registered:
        log.info("Registered 'Apply Searchlight Preview' (id=%s).",
                 ids.ID_ORC_APPLY_SEARCHLIGHT_PREVIEW_COMMAND)
    else:
        log.error("Failed to register 'Apply Searchlight Preview' (id=%s).",
                  ids.ID_ORC_APPLY_SEARCHLIGHT_PREVIEW_COMMAND)
        ok = False

    # --- Apply Relativity Material Preview (combined) command --------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.ID_ORC_APPLY_RELATIVITY_PREVIEW_COMMAND,
        str="{0}: Apply Relativity Material Preview".format(constants.PLUGIN_NAME),
        info=0,
        icon=icon_loader.safe_icon("icon_all_previews"),
        help="Apply both the Doppler tint and the searchlight brightness.",
        dat=commands.ApplyRelativityMaterialPreviewCommand(),
    )
    if registered:
        log.info("Registered 'Apply Relativity Material Preview' (id=%s).",
                 ids.ID_ORC_APPLY_RELATIVITY_PREVIEW_COMMAND)
    else:
        log.error("Failed to register 'Apply Relativity Material Preview' (id=%s).",
                  ids.ID_ORC_APPLY_RELATIVITY_PREVIEW_COMMAND)
        ok = False

    # --- Clear Material Preview command ------------------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.ID_ORC_CLEAR_PREVIEW_COMMAND,
        str="{0}: Clear Material Preview".format(constants.PLUGIN_NAME),
        info=0,
        icon=icon_loader.safe_icon("icon_lorentz_remove"),
        help="Remove all ORC-generated preview materials and tags.",
        dat=commands.ClearMaterialPreviewCommand(),
    )
    if registered:
        log.info("Registered 'Clear Material Preview' (id=%s).",
                 ids.ID_ORC_CLEAR_PREVIEW_COMMAND)
    else:
        log.error("Failed to register 'Clear Material Preview' (id=%s).",
                  ids.ID_ORC_CLEAR_PREVIEW_COMMAND)
        ok = False

    # --- Create Lorentz Preview Copies command -----------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.ID_ORC_CREATE_LORENTZ_PREVIEWS_COMMAND,
        str="{0}: Create Lorentz Preview Copies".format(constants.PLUGIN_NAME),
        info=0,
        icon=icon_loader.safe_icon("icon_lorentz_create"),
        help="Create non-destructive contracted duplicates for Lorentz preview.",
        dat=commands.CreateLorentzPreviewCommand(),
    )
    if registered:
        log.info("Registered 'Create Lorentz Preview Copies' (id=%s).",
                 ids.ID_ORC_CREATE_LORENTZ_PREVIEWS_COMMAND)
    else:
        log.error("Failed to register 'Create Lorentz Preview Copies' (id=%s).",
                  ids.ID_ORC_CREATE_LORENTZ_PREVIEWS_COMMAND)
        ok = False

    # --- Remove Lorentz Preview Copies command -----------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.ID_ORC_REMOVE_LORENTZ_PREVIEWS_COMMAND,
        str="{0}: Remove Lorentz Preview Copies".format(constants.PLUGIN_NAME),
        info=0,
        icon=icon_loader.safe_icon("icon_lorentz_remove"),
        help="Remove the Lorentz preview copies and restore the originals.",
        dat=commands.RemoveLorentzPreviewCommand(),
    )
    if registered:
        log.info("Registered 'Remove Lorentz Preview Copies' (id=%s).",
                 ids.ID_ORC_REMOVE_LORENTZ_PREVIEWS_COMMAND)
    else:
        log.error("Failed to register 'Remove Lorentz Preview Copies' (id=%s).",
                  ids.ID_ORC_REMOVE_LORENTZ_PREVIEWS_COMMAND)
        ok = False

    # --- Create Test Scene command -----------------------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.ID_ORC_CREATE_TEST_SCENE_COMMAND,
        str="{0}: Create Test Scene".format(constants.PLUGIN_NAME),
        info=0,
        icon=icon_loader.safe_icon("icon_create_test_scene"),
        help="Build a demo scene: controller, camera, test objects and a light.",
        dat=commands.CreateTestSceneCommand(),
    )
    if registered:
        log.info("Registered 'Create Test Scene' (id=%s).",
                 ids.ID_ORC_CREATE_TEST_SCENE_COMMAND)
    else:
        log.error("Failed to register 'Create Test Scene' (id=%s).",
                  ids.ID_ORC_CREATE_TEST_SCENE_COMMAND)
        ok = False

    # --- Apply All Previews command ----------------------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.ID_ORC_APPLY_ALL_PREVIEWS_COMMAND,
        str="{0}: Apply All Previews".format(constants.PLUGIN_NAME),
        info=0,
        icon=icon_loader.safe_icon("icon_all_previews"),
        help="Apply the material preview and create Lorentz preview copies.",
        dat=commands.ApplyAllPreviewsCommand(),
    )
    if registered:
        log.info("Registered 'Apply All Previews' (id=%s).", ids.ID_ORC_APPLY_ALL_PREVIEWS_COMMAND)
    else:
        log.error("Failed to register 'Apply All Previews' (id=%s).",
                  ids.ID_ORC_APPLY_ALL_PREVIEWS_COMMAND)
        ok = False

    # --- Octane Status command ---------------------------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.ID_ORC_OCTANE_STATUS_COMMAND,
        str="{0}: Octane Status".format(constants.PLUGIN_NAME),
        info=0,
        icon=icon_loader.safe_icon("icon_octane_status"),
        help="Report Octane availability and status (no Octane changes).",
        dat=commands.OctaneStatusCommand(),
    )
    if registered:
        log.info("Registered 'Octane Status' (id=%s).", ids.ID_ORC_OCTANE_STATUS_COMMAND)
    else:
        log.error("Failed to register 'Octane Status' (id=%s).",
                  ids.ID_ORC_OCTANE_STATUS_COMMAND)
        ok = False

    # --- Octane Diagnostics command ----------------------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.ID_ORC_OCTANE_DIAGNOSTICS_COMMAND,
        str="{0}: Octane Diagnostics".format(constants.PLUGIN_NAME),
        info=0,
        icon=icon_loader.safe_icon("icon_diagnostics"),
        help="Report detected Octane IDs/classes/material parameters (read-only).",
        dat=commands.OctaneDiagnosticsCommand(),
    )
    if registered:
        log.info("Registered 'Octane Diagnostics' (id=%s).",
                 ids.ID_ORC_OCTANE_DIAGNOSTICS_COMMAND)
    else:
        log.error("Failed to register 'Octane Diagnostics' (id=%s).",
                  ids.ID_ORC_OCTANE_DIAGNOSTICS_COMMAND)
        ok = False

    # --- Apply Octane-Compatible Material Preview command ------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.ID_ORC_APPLY_OCTANE_MATERIAL_COMMAND,
        str="{0}: Apply Octane-Compatible Material Preview".format(constants.PLUGIN_NAME),
        info=0,
        icon=icon_loader.safe_icon("icon_octane_status"),
        help="Apply the preview via Octane if supported, else a Standard fallback.",
        dat=commands.ApplyOctaneCompatibleMaterialPreviewCommand(),
    )
    if registered:
        log.info("Registered 'Apply Octane-Compatible Material Preview' (id=%s).",
                 ids.ID_ORC_APPLY_OCTANE_MATERIAL_COMMAND)
    else:
        log.error("Failed to register 'Apply Octane-Compatible Material Preview' "
                  "(id=%s).", ids.ID_ORC_APPLY_OCTANE_MATERIAL_COMMAND)
        ok = False

    # --- Show AOV Plan command ---------------------------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.ID_ORC_SHOW_AOV_PLAN_COMMAND,
        str="{0}: Show AOV Plan".format(constants.PLUGIN_NAME),
        info=0,
        icon=icon_loader.safe_icon("icon_aov_plan"),
        help="Show the desired Relativity AOVs and Octane AOV support status.",
        dat=commands.ShowAOVPlanCommand(),
    )
    if registered:
        log.info("Registered 'Show AOV Plan' (id=%s).", ids.ID_ORC_SHOW_AOV_PLAN_COMMAND)
    else:
        log.error("Failed to register 'Show AOV Plan' (id=%s).",
                  ids.ID_ORC_SHOW_AOV_PLAN_COMMAND)
        ok = False

    # --- Export Experimental OSL Camera command ----------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.ID_ORC_EXPORT_OSL_CAMERA_COMMAND,
        str="{0}: Export Experimental OSL Camera".format(constants.PLUGIN_NAME),
        info=0,
        icon=icon_loader.safe_icon("icon_export_osl"),
        help="Write the experimental (placeholder) OSL camera shader to a file.",
        dat=commands.ExportOSLCameraCommand(),
    )
    if registered:
        log.info("Registered 'Export Experimental OSL Camera' (id=%s).",
                 ids.ID_ORC_EXPORT_OSL_CAMERA_COMMAND)
    else:
        log.error("Failed to register 'Export Experimental OSL Camera' (id=%s).",
                  ids.ID_ORC_EXPORT_OSL_CAMERA_COMMAND)
        ok = False

    # --- Export Relativity Metadata JSON command ---------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.ID_ORC_EXPORT_METADATA_COMMAND,
        str="{0}: Export Relativity Metadata JSON".format(constants.PLUGIN_NAME),
        info=0,
        icon=icon_loader.safe_icon("icon_export_metadata"),
        help="Export controller/camera/object relativity metadata to JSON.",
        dat=commands.ExportMetadataCommand(),
    )
    if registered:
        log.info("Registered 'Export Relativity Metadata JSON' (id=%s).",
                 ids.ID_ORC_EXPORT_METADATA_COMMAND)
    else:
        log.error("Failed to register 'Export Relativity Metadata JSON' (id=%s).",
                  ids.ID_ORC_EXPORT_METADATA_COMMAND)
        ok = False

    # --- Control Panel command ---------------------------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.ID_ORC_CONTROL_PANEL_COMMAND,
        str="{0}: Control Panel".format(constants.PLUGIN_NAME),
        info=0,
        icon=icon_loader.safe_icon("icon_control_panel"),
        help="Open the OpenRelativity control panel (buttons for every command).",
        dat=control_panel.ControlPanelCommand(),
    )
    if registered:
        log.info("Registered 'Control Panel' (id=%s).", ids.ID_ORC_CONTROL_PANEL_COMMAND)
    else:
        log.error("Failed to register 'Control Panel' (id=%s).",
                  ids.ID_ORC_CONTROL_PANEL_COMMAND)
        ok = False

    # --- command icon diagnostic (never affects registration success) ------
    loaded, missing = icon_loader.get_load_summary()
    log.info("Command icons: %d loaded, %d missing.", len(loaded), len(missing))
    if loaded:
        log.debug("Loaded command icons: %s", ", ".join(loaded))
    if missing:
        log.warning("Command icons missing/failed (registered without icon): %s",
                    ", ".join(missing))

    return ok
