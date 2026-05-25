#!/usr/bin/env python3
"""Audit the plugin's UI assets without Cinema 4D.

Verifies that the UI stays internally consistent:

  1. every icon the command registry expects has a PNG file;
  2. the registry matches the command IDs in ``ids.py`` (no drift), every command
     resolves to an ID, and every command has an icon;
  3. icon names referenced in the registration / Control Panel source actually
     exist as files (typo guard) and are known to the registry (drift warning);
  4. the UI documentation files exist.

Usage (from anywhere):  python tools/audit_ui_assets.py
Exits non-zero if any check fails (suitable for CI / pre-commit).
"""

import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_PNG_DIR = os.path.join(REPO_ROOT, "openrelativity_c4d", "resources", "icons", "png")

REQUIRED_UI_DOCS = [
    "docs/UI_UX_AUDIT.md",
    "docs/UI_DESIGN_SYSTEM.md",
    "docs/ICONS.md",
    "docs/COMMAND_REFERENCE.md",
    "docs/USER_GUIDE.md",
    "docs/TROUBLESHOOTING.md",
]

#: Source files whose icon-name string literals must stay valid/consistent.
SOURCE_FILES = [
    "openrelativity_c4d/c4d/plugin_register.py",
    "openrelativity_c4d/c4d/control_panel.py",
]

_ICON_LITERAL = re.compile(r'"(icon_[a-z0-9_]+)"')


def _icon_file(name):
    return os.path.join(ICON_PNG_DIR, name + ".png")


def _load_ui_assets():
    if REPO_ROOT not in sys.path:
        sys.path.insert(0, REPO_ROOT)
    from openrelativity_c4d.c4d import ui_assets  # pure; no c4d
    return ui_assets


def check_icons_exist():
    ua = _load_ui_assets()
    names = ua.expected_icon_names()
    missing = [n for n in names if not os.path.isfile(_icon_file(n))]
    if missing:
        return False, ["missing PNG for icon: " + n for n in missing]
    return True, ["all {0} expected icons have a PNG".format(len(names))]


def check_command_mapping():
    ua = _load_ui_assets()
    from openrelativity_c4d import ids

    messages = []
    ok = True

    ids_cmd = {n for n in ids.all_ids() if n.endswith("_COMMAND")}
    reg_cmd = ua.command_id_constants()
    only_ids = sorted(ids_cmd - reg_cmd)
    only_reg = sorted(reg_cmd - ids_cmd)
    if only_ids:
        ok = False
        messages.append("commands in ids.py but not in the registry: "
                        + ", ".join(only_ids))
    if only_reg:
        ok = False
        messages.append("commands in the registry but not in ids.py: "
                        + ", ".join(only_reg))

    for spec in ua.COMMANDS:
        if ua.command_id(spec) is None:
            ok = False
            messages.append("unresolved command ID: " + spec.const)
        if not spec.icon:
            ok = False
            messages.append("command has no icon: " + spec.const)

    if ok:
        messages.append("registry matches ids.py ({0} commands); all resolve + "
                        "have icons".format(len(ua.COMMANDS)))
    return ok, messages


def check_source_icons():
    ua = _load_ui_assets()
    expected = set(ua.expected_icon_names())
    unknown = []   # referenced in source but no PNG file -> fail
    drift = []     # referenced + file exists but not in the registry -> warn
    referenced = set()
    for rel in SOURCE_FILES:
        path = os.path.join(REPO_ROOT, rel)
        if not os.path.isfile(path):
            continue
        with open(path) as handle:
            text = handle.read()
        for name in _ICON_LITERAL.findall(text):
            referenced.add(name)
            if not os.path.isfile(_icon_file(name)):
                unknown.append("{0}: {1} (no PNG)".format(rel, name))
            elif name not in expected:
                drift.append("{0}: {1} (not in ui_assets registry)".format(rel, name))
    if unknown:
        return False, ["source icon not found: " + u for u in unknown] + [
            "WARNING - " + d for d in drift]
    messages = ["{0} icon name(s) referenced in source, all have PNGs".format(
        len(referenced))]
    messages += ["WARNING - " + d for d in drift]
    return True, messages


def check_ui_docs():
    missing = [d for d in REQUIRED_UI_DOCS
               if not os.path.isfile(os.path.join(REPO_ROOT, d))]
    if missing:
        return False, ["missing UI doc: " + d for d in missing]
    return True, ["all {0} UI docs present".format(len(REQUIRED_UI_DOCS))]


CHECKS = [
    ("expected icons exist", check_icons_exist),
    ("command<->icon registry consistent", check_command_mapping),
    ("source icon references valid", check_source_icons),
    ("UI docs present", check_ui_docs),
]


def main():
    print("OpenRelativity_c4d UI-asset audit")
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
