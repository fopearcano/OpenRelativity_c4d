#!/usr/bin/env python3
"""Verify the OpenRelativity_c4d repository without Cinema 4D.

Checks performed (each reported PASS/FAIL):
  1. expected plugin/source files exist;
  2. the plugin entry point exists and looks wired to bootstrap;
  3. the pure-Python core and tests make NO Cinema 4D (`c4d`) imports;
  4. the pure-Python test suite passes (and pulls in no `c4d`);
  5. the expected documentation files exist.

Usage (from anywhere):  python tools/verify_repo.py
Exits non-zero if any check fails (suitable for CI / pre-commit).
"""

import io
import os
import re
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ENTRYPOINT = "openrelativity_c4d.pyp"

EXPECTED_FILES = [
    ENTRYPOINT,
    "openrelativity_c4d/__init__.py",
    "openrelativity_c4d/bootstrap.py",
    "openrelativity_c4d/constants.py",
    "openrelativity_c4d/ids.py",
    "openrelativity_c4d/logging_utils.py",
    "openrelativity_c4d/core/__init__.py",
    "openrelativity_c4d/core/relativity_math.py",
    "openrelativity_c4d/core/doppler.py",
    "openrelativity_c4d/core/searchlight.py",
    "openrelativity_c4d/core/transforms.py",
    "openrelativity_c4d/core/history.py",
    "openrelativity_c4d/c4d/__init__.py",
    "openrelativity_c4d/c4d/field_specs.py",
    "openrelativity_c4d/c4d/plugin_register.py",
    "openrelativity_c4d/c4d/commands.py",
    "openrelativity_c4d/c4d/control_panel.py",
    "openrelativity_c4d/c4d/icon_loader.py",
    "openrelativity_c4d/c4d/ui_status.py",
    "openrelativity_c4d/c4d/ui_assets.py",
    "openrelativity_c4d/c4d/ui_diagnostics.py",
    "openrelativity_c4d/c4d/scene_controller.py",
    "openrelativity_c4d/c4d/camera_tools.py",
    "openrelativity_c4d/c4d/object_tools.py",
    "openrelativity_c4d/c4d/preview_material.py",
    "openrelativity_c4d/c4d/lorentz_preview.py",
    "openrelativity_c4d/c4d/test_scene.py",
    "openrelativity_c4d/c4d/userdata.py",
    "openrelativity_c4d/octane/detection.py",
    "openrelativity_c4d/octane/diagnostics.py",
    "openrelativity_c4d/octane/adapter.py",
    "openrelativity_c4d/octane/material_adapter.py",
    "openrelativity_c4d/octane/aov_adapter.py",
    "openrelativity_c4d/octane/osl_camera.py",
    "openrelativity_c4d/export/__init__.py",
    "openrelativity_c4d/export/metadata_export.py",
    "openrelativity_c4d/tests/__init__.py",
    "openrelativity_c4d/tests/test_core_math.py",
    "tools/run_core_tests.py",
]

EXPECTED_DOCS = [
    "README.md",
    "CHANGELOG.md",
    "TODO.md",
    "docs/PROJECT_CHARTER.md",
    "docs/ARCHITECTURE.md",
    "docs/ROADMAP.md",
    "docs/ORIGINAL_OPENRELATIVITY_REFERENCE.md",
    "docs/USER_GUIDE.md",
    "docs/QUICKSTART.md",
    "docs/DOPPLER_PREVIEW.md",
    "docs/SEARCHLIGHT_PREVIEW.md",
    "docs/LORENTZ_PREVIEW.md",
    "docs/OCTANE_INTEGRATION.md",
    "docs/AOV_PIPELINE.md",
    "docs/OSL_CAMERA_EXPERIMENTS.md",
    "docs/METADATA_SCHEMA.md",
    "docs/INSTALLATION.md",
    "docs/DEVELOPER_NOTES.md",
    "docs/TEST_PLAN_C4D.md",
    "docs/TEST_PLAN_OCTANE.md",
    "docs/KNOWN_LIMITATIONS.md",
    "docs/LICENSE_DECISION_NEEDED.md",
    "docs/V0_1_RELEASE_NOTES.md",
    "docs/C4D_PLUGIN_TYPE_MIGRATION.md",
    "docs/TIME_DELAY_LIGHT_CONE_DESIGN.md",
    "docs/UI_UX_AUDIT.md",
    "docs/UI_DESIGN_SYSTEM.md",
    "docs/ICONS.md",
    "docs/COMMAND_REFERENCE.md",
    "docs/TROUBLESHOOTING.md",
]

# Directories that must never import Cinema 4D's `c4d` module.
NO_C4D_DIRS = ["openrelativity_c4d/core", "openrelativity_c4d/tests"]

# Matches a top-level `c4d` import (not `openrelativity_c4d`, which has no
# whitespace before "c4d").
_C4D_IMPORT = re.compile(r"^\s*(?:import\s+c4d(?:\b|\.)|from\s+c4d(?:\b|\.))", re.M)


def _rel(path):
    return os.path.join(REPO_ROOT, path)


def check_expected_files():
    missing = [p for p in EXPECTED_FILES if not os.path.isfile(_rel(p))]
    if missing:
        return False, ["missing: " + m for m in missing]
    return True, ["{0} files present".format(len(EXPECTED_FILES))]


def check_entrypoint():
    path = _rel(ENTRYPOINT)
    if not os.path.isfile(path):
        return False, ["entry point {0} not found".format(ENTRYPOINT)]
    with open(path) as handle:
        text = handle.read()
    if "bootstrap" not in text:
        return False, ["{0} does not reference bootstrap".format(ENTRYPOINT)]
    return True, ["{0} present and calls bootstrap".format(ENTRYPOINT)]


def check_no_c4d_imports():
    violations = []
    for rel_dir in NO_C4D_DIRS:
        abs_dir = _rel(rel_dir)
        for root, _dirs, files in os.walk(abs_dir):
            for name in files:
                if not name.endswith(".py"):
                    continue
                full = os.path.join(root, name)
                with open(full) as handle:
                    if _C4D_IMPORT.search(handle.read()):
                        violations.append(os.path.relpath(full, REPO_ROOT))
    if violations:
        return False, ["imports c4d: " + v for v in violations]
    return True, ["no c4d imports in " + ", ".join(NO_C4D_DIRS)]


def check_pure_tests():
    if REPO_ROOT not in sys.path:
        sys.path.insert(0, REPO_ROOT)
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=os.path.join(REPO_ROOT, "openrelativity_c4d", "tests"),
        top_level_dir=REPO_ROOT,
    )
    result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    messages = ["ran {0} tests, {1} failures, {2} errors".format(
        result.testsRun, len(result.failures), len(result.errors))]
    ok = result.wasSuccessful()
    if "c4d" in sys.modules:
        ok = False
        messages.append("the test run imported c4d (must not happen)")
    for case, _tb in list(result.failures) + list(result.errors):
        messages.append("failed: {0}".format(case))
    return ok, messages


def check_docs():
    missing = [p for p in EXPECTED_DOCS if not os.path.isfile(_rel(p))]
    if missing:
        return False, ["missing: " + m for m in missing]
    return True, ["{0} docs present".format(len(EXPECTED_DOCS))]


def check_field_specs():
    if REPO_ROOT not in sys.path:
        sys.path.insert(0, REPO_ROOT)
    from openrelativity_c4d.c4d import field_specs  # pure; no c4d

    problems = field_specs.validate()
    if "c4d" in sys.modules:
        problems.append("importing field_specs pulled in c4d")
    if problems:
        return False, problems
    return True, ["schema valid for {0} entities".format(len(field_specs.ENTITIES))]


CHECKS = [
    ("expected files", check_expected_files),
    ("plugin entry point", check_entrypoint),
    ("no c4d in core/tests", check_no_c4d_imports),
    ("field schema valid", check_field_specs),
    ("pure-Python tests", check_pure_tests),
    ("documentation", check_docs),
]


def main():
    print("OpenRelativity_c4d repository verification")
    print("=" * 50)
    all_ok = True
    for name, func in CHECKS:
        try:
            ok, messages = func()
        except Exception as exc:  # noqa: BLE001
            ok, messages = False, ["check raised: {0}".format(exc)]
        all_ok = all_ok and ok
        print("[{0}] {1}".format("PASS" if ok else "FAIL", name))
        for message in messages:
            print("       - {0}".format(message))
    print("=" * 50)
    print("RESULT:", "PASS" if all_ok else "FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
