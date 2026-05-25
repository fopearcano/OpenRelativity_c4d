"""Plugin-level metadata and constants.

Pure Python: no ``c4d`` import, safe to read from tests. Physics constants live
in :mod:`openrelativity_c4d.core.relativity_math`, not here.
"""

# --- Identity ---------------------------------------------------------------
PLUGIN_NAME = "OpenRelativity C4D"
PLUGIN_VERSION = "0.1.0"
PLUGIN_AUTHOR = "OpenRelativity_c4d contributors"
PROJECT_URL = "https://github.com/fopearcano/OpenRelativity_c4d"

# --- Targeting --------------------------------------------------------------
# Minimum supported Cinema 4D release. The plugin uses only APIs available in
# Cinema 4D 2023+ and its bundled Python 3 runtime.
TARGET_C4D_VERSION = "2023+"

# --- Development status -----------------------------------------------------
DEVELOPMENT_PHASE = "Phase 1 - plugin skeleton"
STATUS_SUMMARY = (
    "Prototype skeleton. The 'About' command and the pure-Python physics core "
    "are functional. Relativistic Scene Controller, Camera/Object tags, "
    "deformers, and Octane integration are placeholders for later phases."
)

# Single-line tagline used in menus / about box.
TAGLINE = "Relativistic visualization tools for Cinema 4D"
