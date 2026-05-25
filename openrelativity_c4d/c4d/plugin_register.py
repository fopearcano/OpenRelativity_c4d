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

    # --- Later phases (not implemented yet) --------------------------------
    # from . import scene_controller, camera_tools, object_tools
    # ok &= scene_controller.register()
    # ok &= camera_tools.register()
    # ok &= object_tools.register()

    return ok
