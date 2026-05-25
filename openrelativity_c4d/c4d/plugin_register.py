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

    # --- Later phases (not implemented yet) --------------------------------
    # from . import object_tools
    # ok &= object_tools.register()

    return ok
