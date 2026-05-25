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

    # --- Clear Doppler Material Preview command ----------------------------
    registered = c4d.plugins.RegisterCommandPlugin(
        id=ids.COMMAND_CLEAR_DOPPLER,
        str="{0}: Clear Doppler Material Preview".format(constants.PLUGIN_NAME),
        info=0,
        icon=None,
        help="Remove the ORC-generated Doppler preview materials and tags.",
        dat=commands.ClearDopplerPreviewCommand(),
    )
    if registered:
        log.info("Registered 'Clear Doppler Material Preview' (id=%s).",
                 ids.COMMAND_CLEAR_DOPPLER)
    else:
        log.error("Failed to register 'Clear Doppler Material Preview' (id=%s).",
                  ids.COMMAND_CLEAR_DOPPLER)
        ok = False

    return ok
