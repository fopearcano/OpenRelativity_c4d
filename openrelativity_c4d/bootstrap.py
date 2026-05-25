"""Plugin bootstrap: the single entry point called by ``openrelativity_c4d.pyp``.

Keeps Cinema-4D-specific imports lazy so that importing this module (or the
package) outside Cinema 4D does not raise. The actual ``c4d`` import and plugin
registration only happen inside :func:`register`, guarded by try/except.
"""

from . import constants
from .logging_utils import get_logger

log = get_logger("bootstrap")


def register():
    """Register all Cinema 4D plugin elements. Returns ``True`` on success.

    Called by the ``.pyp`` at load time (inside Cinema 4D). Safe to call
    elsewhere: if ``c4d`` is unavailable it logs and returns ``False`` instead of
    raising, so a non-C4D environment degrades gracefully.
    """
    log.info(
        "Loading %s v%s (%s)",
        constants.PLUGIN_NAME,
        constants.PLUGIN_VERSION,
        constants.DEVELOPMENT_PHASE,
    )

    # --- Are we actually inside Cinema 4D? ---------------------------------
    try:
        import c4d  # noqa: F401  (presence probe; resolves to Cinema 4D's module)
    except ImportError:
        log.error(
            "The 'c4d' module is unavailable - not running inside Cinema 4D. "
            "Plugin registration skipped."
        )
        return False

    # --- Register elements -------------------------------------------------
    try:
        from .c4d import plugin_register
    except Exception:  # noqa: BLE001
        log.exception("Could not import the Cinema 4D integration layer.")
        return False

    try:
        ok = plugin_register.register_all()
    except Exception:  # noqa: BLE001
        log.exception("Unhandled error during plugin registration.")
        return False

    if ok:
        log.info("%s loaded successfully.", constants.PLUGIN_NAME)
    else:
        log.warning("%s loaded with errors (see log above).", constants.PLUGIN_NAME)
    return ok
