#!/usr/bin/env python3
"""Audit the plugin's Cinema 4D IDs without Cinema 4D.

Cinema 4D plugin IDs must be globally unique; a duplicated or sample ID can stop
another plugin from loading. This tool keeps the prototype honest by checking:

  1. lists the central ORC ID constants (from ``openrelativity_c4d/ids.py``);
  2. verifies every ``ID_ORC_*`` value is unique;
  3. fails if any ORC ID is a well-known sample ID or sits in Maxon's
     ``1000001-1000010`` test range;
  4. fails if any ``Register*Plugin`` call uses a raw numeric ``id=`` instead of a
     central ``ids.ID_ORC_*`` constant;
  5. warns if known sample IDs appear as integer literals in the source.

Usage (from anywhere):  python tools/audit_plugin_ids.py
Exits non-zero if any check fails (suitable for CI / pre-commit).
"""

import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THIS_FILE = os.path.abspath(__file__)
IDS_FILE = os.path.join(REPO_ROOT, "openrelativity_c4d", "ids.py")

# Directories whose .py files register plugins / could hold stray IDs.
SCAN_DIRS = ["openrelativity_c4d"]

# Well-known sample / tutorial IDs that must never be used for real (the explicit
# don't-use list plus Maxon's 1000001-1000010 local-test range).
_EXPLICIT_SAMPLE_IDS = {1000001, 1029999, 1039699, 1059500, 5678901, 1234567}
KNOWN_SAMPLE_IDS = _EXPLICIT_SAMPLE_IDS | set(range(1000001, 1000011))

_REGISTER_CALL = re.compile(r"Register\w*Plugin\s*\(")
_ID_RAW = re.compile(r"\bid\s*=\s*(\d+)")
_ID_CONST = re.compile(r"\bid\s*=\s*ids\.(\w+)")
_INT_TOKEN = re.compile(r"\b\d{6,}\b")  # 6+ digit integer literals


def _rel(path):
    return os.path.relpath(path, REPO_ROOT)


def _py_files():
    files = []
    for rel_dir in SCAN_DIRS:
        for root, _dirs, names in os.walk(os.path.join(REPO_ROOT, rel_dir)):
            if "__pycache__" in root:
                continue
            for name in names:
                if name.endswith(".py"):
                    files.append(os.path.join(root, name))
    return files


def _call_arg_span(text, open_paren_index):
    """Return the substring inside the parentheses starting at ``open_paren_index``
    (which must point at the ``(``), handling nested parens. Best-effort."""
    depth = 0
    for i in range(open_paren_index, len(text)):
        ch = text[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return text[open_paren_index + 1:i]
    return text[open_paren_index + 1:]


def _load_ids():
    if REPO_ROOT not in sys.path:
        sys.path.insert(0, REPO_ROOT)
    from openrelativity_c4d import ids  # pure module, no c4d
    return ids


def check_list_and_uniqueness():
    ids = _load_ids()
    id_map = ids.all_ids()
    messages = ["ORC_ID_BASE = {0}".format(ids.ORC_ID_BASE)]
    for name in sorted(id_map, key=lambda n: id_map[n]):
        messages.append("  {0} = {1}".format(name, id_map[name]))

    values = list(id_map.values())
    seen = {}
    duplicates = {}
    for name, value in id_map.items():
        if value in seen:
            duplicates.setdefault(value, [seen[value]]).append(name)
        else:
            seen[value] = name
    if duplicates:
        for value, names in duplicates.items():
            messages.append("DUPLICATE id {0}: {1}".format(value, ", ".join(names)))
        return False, messages
    messages.append("all {0} ORC IDs are unique".format(len(values)))
    return True, messages


def check_no_sample_ids():
    ids = _load_ids()
    id_map = ids.all_ids()
    bad = {name: value for name, value in id_map.items() if value in KNOWN_SAMPLE_IDS}
    if ids.ORC_ID_BASE in KNOWN_SAMPLE_IDS:
        bad["ORC_ID_BASE"] = ids.ORC_ID_BASE
    if bad:
        return False, ["sample/test ID in use: {0} = {1}".format(n, v)
                       for n, v in bad.items()]
    return True, ["no ORC ID collides with a known sample/test ID"]


def check_registrations_use_constants():
    raw_hits = []
    const_uses = []
    call_count = 0
    for path in _py_files():
        with open(path) as handle:
            text = handle.read()
        for match in _REGISTER_CALL.finditer(text):
            open_paren = text.index("(", match.start())
            args = _call_arg_span(text, open_paren)
            # A real registration call always passes an `id=`. Spans without one
            # are prose mentions (docstrings/comments referencing the API), so
            # skip them rather than flag a non-existent raw ID.
            if re.search(r"\bid\s*=", args) is None:
                continue
            call_count += 1
            raw = _ID_RAW.search(args)
            const = _ID_CONST.search(args)
            line = text.count("\n", 0, match.start()) + 1
            if raw is not None:
                raw_hits.append("{0}:{1} raw id={2}".format(_rel(path), line, raw.group(1)))
            elif const is not None:
                const_uses.append("{0}:{1} id=ids.{2}".format(
                    _rel(path), line, const.group(1)))
            else:
                raw_hits.append("{0}:{1} id= is neither a number nor ids.* "
                                "(could not verify)".format(_rel(path), line))
    messages = ["{0} Register*Plugin call(s); {1} use ids.* constants".format(
        call_count, len(const_uses))]
    if raw_hits:
        messages.extend(raw_hits)
        return False, messages
    return True, messages


def check_no_sample_literals():
    """Warning-only: known sample IDs appearing as integer literals in code."""
    hits = []
    # Skip this tool (it names the sample IDs by design) and ids.py (its docstring
    # documents the 1000001-1000010 range it avoids; its actual ID *values* are
    # validated by check_no_sample_ids via import).
    skip = {THIS_FILE, os.path.abspath(IDS_FILE)}
    for path in _py_files():
        if os.path.abspath(path) in skip:
            continue
        with open(path) as handle:
            for lineno, raw_line in enumerate(handle, 1):
                code = raw_line.split("#", 1)[0]  # ignore trailing comments
                if code.lstrip().startswith(("'", '"', "\"\"\"", "'''")):
                    continue
                for token in _INT_TOKEN.findall(code):
                    if int(token) in KNOWN_SAMPLE_IDS:
                        hits.append("{0}:{1} sample literal {2}".format(
                            _rel(path), lineno, token))
    if hits:
        return True, ["WARNING - " + h for h in hits] + [
            "(warning only) sample IDs appear as literals; confirm they are not "
            "used as plugin IDs"]
    return True, ["no known sample IDs appear as integer literals in code"]


CHECKS = [
    ("central ORC IDs (list + uniqueness)", check_list_and_uniqueness),
    ("no sample/test IDs in ORC IDs", check_no_sample_ids),
    ("registrations use ids.* constants", check_registrations_use_constants),
    ("no stray sample-ID literals (warn)", check_no_sample_literals),
]


def main():
    print("OpenRelativity_c4d plugin-ID audit")
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
