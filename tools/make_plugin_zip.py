#!/usr/bin/env python3
"""Build a distributable zip for manual installation into Cinema 4D.

The archive contains a single top-level folder (``OpenRelativity_c4d/``) holding
the plugin entry point, the package, the docs and examples - drop that folder
into Cinema 4D's user *plugins* directory and restart. Build artifacts and VCS
noise (.git, __pycache__, *.pyc, temp/editor files) are excluded.

Usage (from anywhere):
    python tools/make_plugin_zip.py [output.zip]

With no argument the zip is written to ``build/OpenRelativity_c4d_v<version>.zip``.
Pure standard library; no Cinema 4D and no third-party dependencies.
"""

import os
import sys
import zipfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Top-level folder name inside the archive (what the user drops into plugins/).
ARCHIVE_ROOT = "OpenRelativity_c4d"

#: Top-level repo paths to include (files or directories).
INCLUDE = [
    "openrelativity_c4d.pyp",
    "openrelativity_c4d",
    "docs",
    "examples",
    "README.md",
    "MITLicense.md",
]

EXCLUDE_DIRS = {
    ".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".idea", ".vscode", "build", "dist", ".venv", "venv", "env",
}
EXCLUDE_SUFFIXES = (".pyc", ".pyo", ".swp", ".tmp", ".orig", ".bak")
EXCLUDE_NAMES = {".DS_Store", "Thumbs.db"}


def _plugin_version():
    if REPO_ROOT not in sys.path:
        sys.path.insert(0, REPO_ROOT)
    try:
        from openrelativity_c4d import constants  # pure import, no c4d

        return constants.PLUGIN_VERSION
    except Exception:  # noqa: BLE001
        return "dev"


def _is_excluded(rel_path):
    parts = rel_path.replace("\\", "/").split("/")
    if any(part in EXCLUDE_DIRS for part in parts):
        return True
    name = parts[-1]
    if name in EXCLUDE_NAMES:
        return True
    return name.endswith(EXCLUDE_SUFFIXES)


def _iter_files():
    """Yield (absolute_path, repo_relative_path) for everything to archive."""
    for entry in INCLUDE:
        abs_entry = os.path.join(REPO_ROOT, entry)
        if os.path.isfile(abs_entry):
            if not _is_excluded(entry):
                yield abs_entry, entry
        elif os.path.isdir(abs_entry):
            for root, dirs, files in os.walk(abs_entry):
                # prune excluded directories in-place for efficiency
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                for name in files:
                    abs_path = os.path.join(root, name)
                    rel_path = os.path.relpath(abs_path, REPO_ROOT)
                    if not _is_excluded(rel_path):
                        yield abs_path, rel_path
        else:
            print("  (skipped, not found: {0})".format(entry))


def build_zip(output_path):
    output_dir = os.path.dirname(os.path.abspath(output_path))
    if output_dir and not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    count = 0
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for abs_path, rel_path in _iter_files():
            arcname = "{0}/{1}".format(ARCHIVE_ROOT, rel_path.replace("\\", "/"))
            archive.write(abs_path, arcname)
            count += 1
    return count


def main():
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
    else:
        version = _plugin_version()
        output_path = os.path.join(
            REPO_ROOT, "build",
            "OpenRelativity_c4d_v{0}.zip".format(version))

    print("Building plugin zip ...")
    count = build_zip(output_path)
    size_kb = os.path.getsize(output_path) / 1024.0
    print("Wrote {0} files ({1:.1f} KB) to:".format(count, size_kb))
    print("  {0}".format(output_path))
    print("Unzip into your Cinema 4D user 'plugins' folder; it contains a single")
    print("'{0}/' folder. Restart Cinema 4D. See docs/INSTALLATION.md.".format(
        ARCHIVE_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
