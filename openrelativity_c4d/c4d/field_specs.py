"""Declarative field schema for the relativity entities (pure Python).

A single, **c4d-free** description of the User Data carried by the Relativity
Controller, the Relativistic Camera, and Relativistic Objects: field names,
kinds, defaults, ranges, units, and grouping. It mirrors what
``scene_controller`` / ``camera_tools`` / ``object_tools`` build today.

This is the canonical data the **TagData/ObjectData migration** will iterate to
build a description (a programmatic ``GetDDescription`` or a generated ``.res``).
For now it documents and validates the schema and is exercised by the tests and
``tools/verify_repo.py``; the c4d modules still own their own constants
(migration Step 2 wires them to this). See docs/C4D_PLUGIN_TYPE_MIGRATION.md.

No ``import c4d`` - importable and testable anywhere.
"""

from collections import namedtuple

# --- field kinds (map to User Data DTYPE_* and to description params) -------
KIND_BOOL = "bool"
KIND_REAL = "real"
KIND_VECTOR = "vector"
KIND_CYCLE = "cycle"
KINDS = (KIND_BOOL, KIND_REAL, KIND_VECTOR, KIND_CYCLE)

# --- units ------------------------------------------------------------------
UNIT_NONE = None
UNIT_PERCENT = "percent"

#: One parameter. ``group`` is a group title (see Entity.groups); ``cycle`` is a
#: list of labels for KIND_CYCLE (``default`` is then the index).
Field = namedtuple(
    "Field",
    ["name", "kind", "default", "group", "min_val", "max_val", "step", "unit", "cycle"],
)

#: An entity (controller / camera / object) with ordered group titles + fields.
Entity = namedtuple("Entity", ["key", "label", "groups", "fields"])


def _f(name, kind, default=None, group=None, min_val=None, max_val=None,
       step=None, unit=UNIT_NONE, cycle=None):
    return Field(name, kind, default, group, min_val, max_val, step, unit, cycle)


_PERCENT_0_1 = dict(min_val=0.0, max_val=1.0, step=0.01, unit=UNIT_PERCENT)
_PERCENT_BETA = dict(min_val=0.0, max_val=0.999, step=0.001, unit=UNIT_PERCENT)

PREVIEW_MODES = ["Off", "Doppler", "Searchlight", "Doppler + Searchlight"]

CONTROLLER = Entity(
    key="controller",
    label="Relativity Controller",
    groups=("Relativity", "Visual Effects", "Integration"),
    fields=(
        _f("Enabled", KIND_BOOL, True, "Relativity"),
        _f("Artificial Speed of Light", KIND_REAL, 1000.0, "Relativity",
           min_val=0.001, step=1.0),
        _f("Global Beta Override", KIND_REAL, 0.0, "Relativity", **_PERCENT_BETA),
        _f("Doppler Strength", KIND_REAL, 1.0, "Visual Effects", **_PERCENT_0_1),
        _f("Searchlight Strength", KIND_REAL, 1.0, "Visual Effects", **_PERCENT_0_1),
        _f("Lorentz Deformation Strength", KIND_REAL, 1.0, "Visual Effects", **_PERCENT_0_1),
        _f("Preview Mode", KIND_CYCLE, 3, "Visual Effects", cycle=PREVIEW_MODES),
        _f("Hide Originals (Lorentz Preview)", KIND_BOOL, True, "Visual Effects"),
        _f("Octane Adapter Enabled", KIND_BOOL, False, "Integration"),
        _f("Bake Mode Enabled", KIND_BOOL, False, "Integration"),
    ),
)

CAMERA = Entity(
    key="camera",
    label="Relativistic Camera",
    groups=("Relativistic Camera", "Preview", "Integration (Experimental)"),
    fields=(
        _f("ORC Enabled", KIND_BOOL, True, "Relativistic Camera"),
        _f("Observer Beta", KIND_REAL, 0.0, "Relativistic Camera", **_PERCENT_BETA),
        _f("Observer Velocity", KIND_VECTOR, (0.0, 0.0, 0.0), "Relativistic Camera"),
        _f("Use Controller Global Beta", KIND_BOOL, True, "Relativistic Camera"),
        _f("Doppler Preview Enabled", KIND_BOOL, True, "Preview"),
        _f("Searchlight Preview Enabled", KIND_BOOL, True, "Preview"),
        _f("Aberration Preview Enabled", KIND_BOOL, False, "Preview"),
        _f("Octane Camera Sync Enabled", KIND_BOOL, False, "Integration (Experimental)"),
        _f("OSL Camera Experimental Enabled", KIND_BOOL, False, "Integration (Experimental)"),
    ),
)

OBJECT = Entity(
    key="object",
    label="Relativistic Object",
    groups=("Relativistic Object", "Material Preview", "Integration"),
    fields=(
        _f("ORC Object Enabled", KIND_BOOL, True, "Relativistic Object"),
        _f("Object Beta", KIND_REAL, 0.0, "Relativistic Object", **_PERCENT_BETA),
        _f("Velocity X", KIND_REAL, 0.0, "Relativistic Object", step=1.0),
        _f("Velocity Y", KIND_REAL, 0.0, "Relativistic Object", step=1.0),
        _f("Velocity Z", KIND_REAL, 0.0, "Relativistic Object", step=1.0),
        _f("Use Camera Relative Direction", KIND_BOOL, True, "Relativistic Object"),
        _f("Doppler Material Preview", KIND_BOOL, True, "Material Preview"),
        _f("Searchlight Material Preview", KIND_BOOL, True, "Material Preview"),
        _f("Lorentz Deformation Preview", KIND_BOOL, True, "Material Preview"),
        _f("Bake Eligible", KIND_BOOL, False, "Integration"),
        _f("Octane Material Sync Enabled", KIND_BOOL, False, "Integration"),
    ),
)

ENTITIES = {e.key: e for e in (CONTROLLER, CAMERA, OBJECT)}


def field_names(entity_key):
    """Ordered field names for an entity."""
    return [f.name for f in ENTITIES[entity_key].fields]


def defaults(entity_key):
    """``{field_name: default}`` for an entity (includes the vector default)."""
    return {f.name: f.default for f in ENTITIES[entity_key].fields}


def validate():
    """Return a list of schema problems (empty if the schema is consistent)."""
    problems = []
    for key, entity in ENTITIES.items():
        seen = set()
        groups = set(entity.groups)
        for f in entity.fields:
            tag = "{0}.{1!r}".format(key, f.name)
            if f.name in seen:
                problems.append("{0}: duplicate field name".format(tag))
            seen.add(f.name)
            if f.kind not in KINDS:
                problems.append("{0}: unknown kind {1!r}".format(tag, f.kind))
            if f.group is not None and f.group not in groups:
                problems.append("{0}: unknown group {1!r}".format(tag, f.group))
            if (f.kind == KIND_REAL and f.min_val is not None
                    and f.max_val is not None and f.min_val > f.max_val):
                problems.append("{0}: min_val > max_val".format(tag))
            if f.kind == KIND_CYCLE:
                if not f.cycle:
                    problems.append("{0}: cycle has no items".format(tag))
                elif not (0 <= int(f.default) < len(f.cycle)):
                    problems.append("{0}: cycle default out of range".format(tag))
    return problems
