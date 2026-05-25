"""Logging helpers for OpenRelativity C4D.

Pure Python (standard-library :mod:`logging` only) so it is import-safe inside
Cinema 4D, in unit tests, and in plain scripts. Inside Cinema 4D, records sent to
``stderr`` appear in the Python console / Extensions > Console.

Usage::

    from openrelativity_c4d.logging_utils import get_logger
    log = get_logger(__name__)
    log.info("hello")
"""

import logging

#: Root logger name for the whole plugin. Child loggers hang off this.
ROOT_LOGGER_NAME = "openrelativity_c4d"

_DEFAULT_FORMAT = "[OpenRelativity C4D] %(levelname)s %(name)s: %(message)s"

# Default level; can be raised/lowered at runtime via set_level().
_DEFAULT_LEVEL = logging.INFO


def _configure_root():
    """Attach a single stream handler to the root plugin logger (idempotent)."""
    root = logging.getLogger(ROOT_LOGGER_NAME)
    if not root.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT))
        root.addHandler(handler)
        root.setLevel(_DEFAULT_LEVEL)
        # Don't double-log through the global root logger.
        root.propagate = False
    return root


def get_logger(name=None):
    """Return a configured logger.

    ``name`` may be a module ``__name__`` or a short label; it is namespaced
    under :data:`ROOT_LOGGER_NAME` so all plugin logs share one handler/level.
    """
    _configure_root()
    if not name or name == ROOT_LOGGER_NAME:
        return logging.getLogger(ROOT_LOGGER_NAME)

    # Normalise a dotted module name to a compact child name.
    short = name.split(".")[-1]
    return logging.getLogger("{0}.{1}".format(ROOT_LOGGER_NAME, short))


def set_level(level):
    """Set the plugin-wide log level (e.g. ``logging.DEBUG``)."""
    _configure_root().setLevel(level)
