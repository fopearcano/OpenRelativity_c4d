"""Registration of Cinema 4D plugin elements.

:func:`register_all` is called from :mod:`openrelativity_c4d.bootstrap` inside
Cinema 4D. In this skeleton it registers only the *About* command; the
commented-out blocks mark where the Scene Controller, tags and deformer will be
registered in later phases.
"""

import c4d  # Cinema 4D's module

from .. import constants, ids
from ..logging_utils import get_logger
from . import commands

log = get_logger("register")


def register_all():
    """Register every plugin element. Returns ``True`` if all succeeded."""
    ok = True

    # --- About command -----------------------------------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.COMMAND_ABOUT,
        str="{0}: About".format(constants.PLUGIN_NAME),
        info=0,
        icon=None,
        help="Show information about {0}.".format(constants.PLUGIN_NAME),
        dat=commands.AboutCommand(),
    )
    if registered:
        log.info("Registered command 'About' (id=%s).", ids.COMMAND_ABOUT)
    else:
        log.error("Failed to register the 'About' command (id=%s).", ids.COMMAND_ABOUT)
        ok = False

    # --- Create Relativity Controller command ------------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.COMMAND_CREATE_CONTROLLER,
        str="{0}: Create Relativity Controller".format(constants.PLUGIN_NAME),
        info=0,
        icon=None,
        help="Create the ORC_Relativity_Controller Null with relativity settings.",
        dat=commands.CreateControllerCommand(),
    )
    if registered:
        log.info("Registered 'Create Relativity Controller' (id=%s).",
                 ids.COMMAND_CREATE_CONTROLLER)
    else:
        log.error("Failed to register 'Create Relativity Controller' (id=%s).",
                  ids.COMMAND_CREATE_CONTROLLER)
        ok = False

    # --- Setup Relativistic Camera command ---------------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.COMMAND_SETUP_CAMERA,
        str="{0}: Setup Relativistic Camera".format(constants.PLUGIN_NAME),
        info=0,
        icon=None,
        help="Configure the selected camera (or create one) as a relativistic observer.",
        dat=commands.SetupCameraCommand(),
    )
    if registered:
        log.info("Registered 'Setup Relativistic Camera' (id=%s).",
                 ids.COMMAND_SETUP_CAMERA)
    else:
        log.error("Failed to register 'Setup Relativistic Camera' (id=%s).",
                  ids.COMMAND_SETUP_CAMERA)
        ok = False

    # --- Setup Selected Relativistic Objects command -----------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.COMMAND_SETUP_OBJECTS,
        str="{0}: Setup Selected Relativistic Objects".format(constants.PLUGIN_NAME),
        info=0,
        icon=None,
        help="Add relativistic User Data to the selected objects.",
        dat=commands.SetupObjectsCommand(),
    )
    if registered:
        log.info("Registered 'Setup Selected Relativistic Objects' (id=%s).",
                 ids.COMMAND_SETUP_OBJECTS)
    else:
        log.error("Failed to register 'Setup Selected Relativistic Objects' (id=%s).",
                  ids.COMMAND_SETUP_OBJECTS)
        ok = False

    # --- Select Relativistic Objects command -------------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.COMMAND_SELECT_OBJECTS,
        str="{0}: Select Relativistic Objects".format(constants.PLUGIN_NAME),
        info=0,
        icon=None,
        help="Select every object that has relativistic User Data.",
        dat=commands.SelectObjectsCommand(),
    )
    if registered:
        log.info("Registered 'Select Relativistic Objects' (id=%s).",
                 ids.COMMAND_SELECT_OBJECTS)
    else:
        log.error("Failed to register 'Select Relativistic Objects' (id=%s).",
                  ids.COMMAND_SELECT_OBJECTS)
        ok = False

    # --- Apply Doppler Material Preview command ----------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.COMMAND_APPLY_DOPPLER,
        str="{0}: Apply Doppler Material Preview".format(constants.PLUGIN_NAME),
        info=0,
        icon=None,
        help="Apply the approximate Doppler colour preview to relativistic objects.",
        dat=commands.ApplyDopplerPreviewCommand(),
    )
    if registered:
        log.info("Registered 'Apply Doppler Material Preview' (id=%s).",
                 ids.COMMAND_APPLY_DOPPLER)
    else:
        log.error("Failed to register 'Apply Doppler Material Preview' (id=%s).",
                  ids.COMMAND_APPLY_DOPPLER)
        ok = False

    # --- Apply Searchlight Preview command ---------------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.COMMAND_APPLY_SEARCHLIGHT,
        str="{0}: Apply Searchlight Preview".format(constants.PLUGIN_NAME),
        info=0,
        icon=None,
        help="Apply the approximate searchlight (beaming) brightness preview.",
        dat=commands.ApplySearchlightPreviewCommand(),
    )
    if registered:
        log.info("Registered 'Apply Searchlight Preview' (id=%s).",
                 ids.COMMAND_APPLY_SEARCHLIGHT)
    else:
        log.error("Failed to register 'Apply Searchlight Preview' (id=%s).",
                  ids.COMMAND_APPLY_SEARCHLIGHT)
        ok = False

    # --- Apply Relativity Material Preview (combined) command --------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.COMMAND_APPLY_RELATIVITY_PREVIEW,
        str="{0}: Apply Relativity Material Preview".format(constants.PLUGIN_NAME),
        info=0,
        icon=None,
        help="Apply both the Doppler tint and the searchlight brightness.",
        dat=commands.ApplyRelativityMaterialPreviewCommand(),
    )
    if registered:
        log.info("Registered 'Apply Relativity Material Preview' (id=%s).",
                 ids.COMMAND_APPLY_RELATIVITY_PREVIEW)
    else:
        log.error("Failed to register 'Apply Relativity Material Preview' (id=%s).",
                  ids.COMMAND_APPLY_RELATIVITY_PREVIEW)
        ok = False

    # --- Clear Material Preview command ------------------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.COMMAND_CLEAR_PREVIEW,
        str="{0}: Clear Material Preview".format(constants.PLUGIN_NAME),
        info=0,
        icon=None,
        help="Remove all ORC-generated preview materials and tags.",
        dat=commands.ClearMaterialPreviewCommand(),
    )
    if registered:
        log.info("Registered 'Clear Material Preview' (id=%s).",
                 ids.COMMAND_CLEAR_PREVIEW)
    else:
        log.error("Failed to register 'Clear Material Preview' (id=%s).",
                  ids.COMMAND_CLEAR_PREVIEW)
        ok = False

    # --- Create Lorentz Preview Copies command -----------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.COMMAND_CREATE_LORENTZ,
        str="{0}: Create Lorentz Preview Copies".format(constants.PLUGIN_NAME),
        info=0,
        icon=None,
        help="Create non-destructive contracted duplicates for Lorentz preview.",
        dat=commands.CreateLorentzPreviewCommand(),
    )
    if registered:
        log.info("Registered 'Create Lorentz Preview Copies' (id=%s).",
                 ids.COMMAND_CREATE_LORENTZ)
    else:
        log.error("Failed to register 'Create Lorentz Preview Copies' (id=%s).",
                  ids.COMMAND_CREATE_LORENTZ)
        ok = False

    # --- Remove Lorentz Preview Copies command -----------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.COMMAND_REMOVE_LORENTZ,
        str="{0}: Remove Lorentz Preview Copies".format(constants.PLUGIN_NAME),
        info=0,
        icon=None,
        help="Remove the Lorentz preview copies and restore the originals.",
        dat=commands.RemoveLorentzPreviewCommand(),
    )
    if registered:
        log.info("Registered 'Remove Lorentz Preview Copies' (id=%s).",
                 ids.COMMAND_REMOVE_LORENTZ)
    else:
        log.error("Failed to register 'Remove Lorentz Preview Copies' (id=%s).",
                  ids.COMMAND_REMOVE_LORENTZ)
        ok = False

    # --- Create Test Scene command -----------------------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.COMMAND_CREATE_TEST_SCENE,
        str="{0}: Create Test Scene".format(constants.PLUGIN_NAME),
        info=0,
        icon=None,
        help="Build a demo scene: controller, camera, test objects and a light.",
        dat=commands.CreateTestSceneCommand(),
    )
    if registered:
        log.info("Registered 'Create Test Scene' (id=%s).",
                 ids.COMMAND_CREATE_TEST_SCENE)
    else:
        log.error("Failed to register 'Create Test Scene' (id=%s).",
                  ids.COMMAND_CREATE_TEST_SCENE)
        ok = False

    # --- Apply All Previews command ----------------------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.COMMAND_APPLY_ALL,
        str="{0}: Apply All Previews".format(constants.PLUGIN_NAME),
        info=0,
        icon=None,
        help="Apply the material preview and create Lorentz preview copies.",
        dat=commands.ApplyAllPreviewsCommand(),
    )
    if registered:
        log.info("Registered 'Apply All Previews' (id=%s).", ids.COMMAND_APPLY_ALL)
    else:
        log.error("Failed to register 'Apply All Previews' (id=%s).",
                  ids.COMMAND_APPLY_ALL)
        ok = False

    # --- Octane Status command ---------------------------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.COMMAND_OCTANE_STATUS,
        str="{0}: Octane Status".format(constants.PLUGIN_NAME),
        info=0,
        icon=None,
        help="Report Octane availability and status (no Octane changes).",
        dat=commands.OctaneStatusCommand(),
    )
    if registered:
        log.info("Registered 'Octane Status' (id=%s).", ids.COMMAND_OCTANE_STATUS)
    else:
        log.error("Failed to register 'Octane Status' (id=%s).",
                  ids.COMMAND_OCTANE_STATUS)
        ok = False

    # --- Apply Octane-Compatible Material Preview command ------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.COMMAND_APPLY_OCTANE_MATERIAL,
        str="{0}: Apply Octane-Compatible Material Preview".format(constants.PLUGIN_NAME),
        info=0,
        icon=None,
        help="Apply the preview via Octane if supported, else a Standard fallback.",
        dat=commands.ApplyOctaneCompatibleMaterialPreviewCommand(),
    )
    if registered:
        log.info("Registered 'Apply Octane-Compatible Material Preview' (id=%s).",
                 ids.COMMAND_APPLY_OCTANE_MATERIAL)
    else:
        log.error("Failed to register 'Apply Octane-Compatible Material Preview' "
                  "(id=%s).", ids.COMMAND_APPLY_OCTANE_MATERIAL)
        ok = False

    # --- Show AOV Plan command ---------------------------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.COMMAND_SHOW_AOV_PLAN,
        str="{0}: Show AOV Plan".format(constants.PLUGIN_NAME),
        info=0,
        icon=None,
        help="Show the desired Relativity AOVs and Octane AOV support status.",
        dat=commands.ShowAOVPlanCommand(),
    )
    if registered:
        log.info("Registered 'Show AOV Plan' (id=%s).", ids.COMMAND_SHOW_AOV_PLAN)
    else:
        log.error("Failed to register 'Show AOV Plan' (id=%s).",
                  ids.COMMAND_SHOW_AOV_PLAN)
        ok = False

    # --- Export Experimental OSL Camera command ----------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.COMMAND_EXPORT_OSL_CAMERA,
        str="{0}: Export Experimental OSL Camera".format(constants.PLUGIN_NAME),
        info=0,
        icon=None,
        help="Write the experimental (placeholder) OSL camera shader to a file.",
        dat=commands.ExportOSLCameraCommand(),
    )
    if registered:
        log.info("Registered 'Export Experimental OSL Camera' (id=%s).",
                 ids.COMMAND_EXPORT_OSL_CAMERA)
    else:
        log.error("Failed to register 'Export Experimental OSL Camera' (id=%s).",
                  ids.COMMAND_EXPORT_OSL_CAMERA)
        ok = False

    # --- Export Relativity Metadata JSON command ---------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.COMMAND_EXPORT_METADATA,
        str="{0}: Export Relativity Metadata JSON".format(constants.PLUGIN_NAME),
        info=0,
        icon=None,
        help="Export controller/camera/object relativity metadata to JSON.",
        dat=commands.ExportMetadataCommand(),
    )
    if registered:
        log.info("Registered 'Export Relativity Metadata JSON' (id=%s).",
                 ids.COMMAND_EXPORT_METADATA)
    else:
        log.error("Failed to register 'Export Relativity Metadata JSON' (id=%s).",
                  ids.COMMAND_EXPORT_METADATA)
        ok = False

    return ok
