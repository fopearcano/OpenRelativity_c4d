"""Shared Cinema 4D User Data helpers.

Low-level builders and **name-based** accessors used by the Relativity Controller,
the Relativistic Camera, and future tags. Addressing User Data by its display
**name** (not by hard-coded sub-ids) keeps accessors robust if the layout changes.

``import c4d`` here resolves to Cinema 4D's module (absolute import), not the
``openrelativity_c4d.c4d`` sub-package.
"""

import c4d


# --- builders ----------------------------------------------------------------
def add_group(obj, name, parent=None):
    bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_GROUP)
    bc[c4d.DESC_NAME] = name
    bc[c4d.DESC_SHORT_NAME] = name
    bc[c4d.DESC_TITLEBAR] = True
    if parent is not None:
        bc[c4d.DESC_PARENTGROUP] = parent
    return obj.AddUserData(bc)


def add_bool(obj, name, default, group=None):
    bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_BOOL)
    bc[c4d.DESC_NAME] = name
    bc[c4d.DESC_SHORT_NAME] = name
    bc[c4d.DESC_DEFAULT] = bool(default)
    if group is not None:
        bc[c4d.DESC_PARENTGROUP] = group
    descid = obj.AddUserData(bc)
    obj[descid] = bool(default)
    return descid


def add_real(obj, name, default, group=None,
             min_val=None, max_val=None, step=None, unit=None):
    bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_REAL)
    bc[c4d.DESC_NAME] = name
    bc[c4d.DESC_SHORT_NAME] = name
    bc[c4d.DESC_DEFAULT] = float(default)
    if min_val is not None:
        bc[c4d.DESC_MIN] = float(min_val)
    if max_val is not None:
        bc[c4d.DESC_MAX] = float(max_val)
    if step is not None:
        bc[c4d.DESC_STEP] = float(step)
    if unit is not None:
        bc[c4d.DESC_UNIT] = unit
    if group is not None:
        bc[c4d.DESC_PARENTGROUP] = group
    descid = obj.AddUserData(bc)
    obj[descid] = float(default)
    return descid


def add_vector(obj, name, default=None, group=None):
    if default is None:
        default = c4d.Vector(0.0, 0.0, 0.0)
    bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_VECTOR)
    bc[c4d.DESC_NAME] = name
    bc[c4d.DESC_SHORT_NAME] = name
    bc[c4d.DESC_DEFAULT] = default
    if group is not None:
        bc[c4d.DESC_PARENTGROUP] = group
    descid = obj.AddUserData(bc)
    obj[descid] = default
    return descid


def add_long(obj, name, default=0, group=None):
    bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_LONG)
    bc[c4d.DESC_NAME] = name
    bc[c4d.DESC_SHORT_NAME] = name
    bc[c4d.DESC_DEFAULT] = int(default)
    if group is not None:
        bc[c4d.DESC_PARENTGROUP] = group
    descid = obj.AddUserData(bc)
    obj[descid] = int(default)
    return descid


def add_link(obj, name, group=None):
    """Add a link (object reference) User Data field. Set the value with
    ``obj[descid] = other_object`` and read it back the same way."""
    bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_BASELISTLINK)
    bc[c4d.DESC_NAME] = name
    bc[c4d.DESC_SHORT_NAME] = name
    if group is not None:
        bc[c4d.DESC_PARENTGROUP] = group
    return obj.AddUserData(bc)


def add_cycle(obj, name, items, default, group=None):
    bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_LONG)
    bc[c4d.DESC_NAME] = name
    bc[c4d.DESC_SHORT_NAME] = name
    bc[c4d.DESC_CUSTOMGUI] = c4d.CUSTOMGUI_CYCLE
    cycle = c4d.BaseContainer()
    for index, label in enumerate(items):
        cycle.SetString(index, label)
    bc.SetContainer(c4d.DESC_CYCLE, cycle)
    bc[c4d.DESC_DEFAULT] = int(default)
    if group is not None:
        bc[c4d.DESC_PARENTGROUP] = group
    descid = obj.AddUserData(bc)
    obj[descid] = int(default)
    return descid


# --- accessors ---------------------------------------------------------------
def descid_for_field(obj, field_name):
    """Return the ``DescID`` of a User Data field by display name, or ``None``."""
    if obj is None:
        return None
    for descid, bc in obj.GetUserDataContainer():
        if bc[c4d.DESC_NAME] == field_name:
            return descid
    return None


def has_field(obj, field_name):
    """``True`` if ``obj`` has a User Data field with this name."""
    return descid_for_field(obj, field_name) is not None


def get_value(obj, field_name, default=None):
    """Read a User Data field by name; ``default`` if missing."""
    descid = descid_for_field(obj, field_name)
    if descid is None:
        return default
    return obj[descid]


def set_value(obj, field_name, value):
    """Write a User Data field by name. Returns ``True`` on success."""
    descid = descid_for_field(obj, field_name)
    if descid is None:
        return False
    obj[descid] = value
    return True
