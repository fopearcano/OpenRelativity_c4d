"""Safe, centralized loading of the plugin's command icons.

One place that turns an icon *name* (e.g. ``"icon_setup_camera"``) into a
``c4d.bitmaps.BaseBitmap`` for ``RegisterCommandPlugin(icon=...)`` - and that
**never crashes** the plugin if an icon is missing or unreadable: every failure
path returns ``None`` (which registration treats as "no icon"), logging at most a
debug/warning line.

Design:

* Paths are resolved **relative to the plugin package root** via ``__file__`` -
  no hardcoded absolute paths.
* There is **no top-level** ``import c4d``: the path helpers
  (:func:`get_plugin_root`, :func:`get_icon_path`) are pure ``os`` and unit-test
  in plain Python; ``c4d`` is imported lazily only inside :func:`load_icon_bitmap`.
  So importing this module is safe outside Cinema 4D and pulls in no Octane.
* Results are cached, and which icons loaded vs. went missing is tracked for a
  startup diagnostic (:func:`get_load_summary` / :func:`format_load_summary`).

Icons live in ``openrelativity_c4d/resources/icons/png/<name>.png`` (see
docs/ICONS.md). PNG is what Cinema 4D's ``BaseBitmap`` loads; the SVG sources are
not loaded at runtime.
"""

import os

from ..logging_utils import get_logger

log = get_logger("icon_loader")

#: Sub-path (under the plugin root) holding the PNG icons.
_ICON_SUBDIR = ("resources", "icons", "png")

#: name -> BaseBitmap|None (cache; None means "tried and unavailable").
_cache = {}
#: names that yielded a bitmap / that did not, for the startup diagnostic.
_loaded = set()
_missing = set()


def get_plugin_root():
    """Return the absolute path of the ``openrelativity_c4d`` package directory.

    Derived from this file's location (``openrelativity_c4d/c4d/icon_loader.py``),
    so it is never a hardcoded absolute path and follows the repo wherever it lives.
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_icon_path(icon_name):
    """Return the absolute path to ``icon_name``'s PNG, or ``None`` if absent.

    Accepts a bare name (``"icon_setup_camera"``), a name without the ``icon_``
    prefix, or one with a trailing ``.png``. Only a basename is used (no path
    traversal). Pure: touches the filesystem but never imports ``c4d``.
    """
    name = os.path.basename(str(icon_name)).strip()
    if name.lower().endswith(".png"):
        name = name[:-4]
    if not name:
        return None

    candidates = [name]
    if not name.startswith("icon_"):
        candidates.append("icon_" + name)

    base = os.path.join(get_plugin_root(), *_ICON_SUBDIR)
    for candidate in candidates:
        path = os.path.join(base, candidate + ".png")
        if os.path.isfile(path):
            return path
    return None


def load_icon_bitmap(icon_name):
    """Load ``icon_name`` into a ``c4d.bitmaps.BaseBitmap``, or return ``None``.

    Returns ``None`` (never raises) when the file is missing, Cinema 4D is
    unavailable, or the bitmap fails to initialize. Logs the reason at debug level
    so a missing icon never floods the console or stops plugin loading.
    """
    path = get_icon_path(icon_name)
    if path is None:
        log.debug("Icon '%s' not found under %s.", icon_name, os.path.join(*_ICON_SUBDIR))
        return None

    try:
        import c4d  # Cinema 4D's module (lazy: keeps this file import-safe)
    except Exception:  # noqa: BLE001
        log.debug("Cinema 4D unavailable; cannot load icon '%s'.", icon_name)
        return None

    try:
        bitmap = c4d.bitmaps.BaseBitmap()
        result = bitmap.InitWith(path)
        # InitWith returns (IMAGERESULT, isMovie) in the Python API; tolerate both.
        code = result[0] if isinstance(result, (tuple, list)) else result
        if code != getattr(c4d, "IMAGERESULT_OK", 0):
            log.debug("Icon '%s' failed to load (result=%s).", icon_name, code)
            return None
        return bitmap
    except Exception:  # noqa: BLE001
        log.debug("Icon '%s' raised while loading; ignoring.", icon_name, exc_info=True)
        return None


def safe_icon(icon_name):
    """Return a cached ``BaseBitmap`` for ``icon_name`` or ``None`` - never raises.

    The entry point used by command registration: pass the result straight to
    ``RegisterCommandPlugin(icon=...)``. ``None`` simply means the command
    registers without an icon (today's behavior), so a missing/broken icon never
    affects whether the command works.
    """
    key = str(icon_name)
    if key in _cache:
        return _cache[key]

    bitmap = None
    try:
        bitmap = load_icon_bitmap(key)
    except Exception:  # noqa: BLE001 - defensive; load_icon_bitmap already guards
        log.warning("Unexpected error loading icon '%s'; registering without it.",
                    key, exc_info=True)
        bitmap = None

    _cache[key] = bitmap
    (_loaded if bitmap is not None else _missing).add(key)
    return bitmap


def get_load_summary():
    """Return ``(loaded_names, missing_names)`` as sorted lists.

    Reflects the icons requested via :func:`safe_icon` so far (i.e. after command
    registration). "Missing" covers not-found files, an unavailable Cinema 4D, and
    load failures alike.
    """
    return sorted(_loaded), sorted(_missing)


def format_load_summary():
    """Render the load summary as a short human-readable string."""
    loaded, missing = get_load_summary()
    lines = ["Command icons: {0} loaded, {1} missing.".format(len(loaded), len(missing))]
    if loaded:
        lines.append("  loaded:  " + ", ".join(loaded))
    if missing:
        lines.append("  missing: " + ", ".join(missing))
    return "\n".join(lines)


def reset_cache():
    """Clear the cache and load tracking (used by tests)."""
    _cache.clear()
    _loaded.clear()
    _missing.clear()
