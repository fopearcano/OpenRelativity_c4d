"""OpenRelativity C4D - Cinema 4D plugin entry point.

Cinema 4D loads every ``*.pyp`` file in its plugins folders and executes it with
``__name__ == "__main__"``. This file deliberately stays tiny: it makes the
sibling ``openrelativity_c4d`` package importable and then delegates all real
work to :func:`openrelativity_c4d.bootstrap.register`.

Design notes
------------
* All registration logic lives in the package (``openrelativity_c4d/``) so it can
  be tested and reused. This ``.pyp`` is just the hook Cinema 4D calls.
* Importing is wrapped in try/except so a failure here cannot take down Cinema
  4D's plugin-loading pass for other plugins.
* The pure-Python physics core (``openrelativity_c4d.core``) never imports
  ``c4d``; this file is the only Cinema-4D-specific thing that must exist on disk
  next to the package.
"""

import os
import sys
import traceback

# ----------------------------------------------------------------------------
# Make the plugin's own folder importable so ``import openrelativity_c4d`` works
# regardless of how Cinema 4D set up sys.path for this .pyp.
# ----------------------------------------------------------------------------
try:
    _PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # __file__ should always be defined for a .pyp, but stay defensive.
    _PLUGIN_DIR = os.path.abspath(os.getcwd())

if _PLUGIN_DIR and _PLUGIN_DIR not in sys.path:
    sys.path.insert(0, _PLUGIN_DIR)


if __name__ == "__main__":
    # Cinema 4D executes this block when it loads the plugin.
    try:
        import openrelativity_c4d.bootstrap as bootstrap

        bootstrap.register()
    except Exception:  # noqa: BLE001 - never let a plugin error break C4D startup
        print("[OpenRelativity C4D] Fatal error while loading plugin:")
        traceback.print_exc()
