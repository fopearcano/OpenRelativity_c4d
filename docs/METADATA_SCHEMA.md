# Relativity Metadata Schema (JSON)

A simple, dependency-free JSON export of the scene's relativistic state, for
renderer/post workflows, a future RelativityRender bridge, debugging, and
reproducibility.

> The numeric values (`beta`, `doppler_factor`, `searchlight_multiplier`,
> `cos_theta`) are the same **artistic approximations** the previews use - not
> spectral/radiometric quantities. Each export embeds these caveats in
> `approximation_notes`.

## Exporting

**Extensions > “OpenRelativity C4D: Export Relativity Metadata JSON”** opens a
save dialog (defaulting to the project folder and `ORC_metadata_f<frame>.json`)
and writes the file. Programmatic: `openrelativity_c4d/export/metadata_export.py`
→ `collect_metadata(doc)` (dict), `to_json(metadata)` (string),
`export_metadata_json(doc, path)` (writes; returns `{ok, path, error,
object_count}`).

It exports the **current frame** - run it per frame (or script it across a frame
range) for animation.

## Top-level structure

| Key | Type | Meaning |
|---|---|---|
| `schema` | string | Always `"openrelativity_c4d.metadata"`. |
| `schema_version` | int | Schema version (currently `1`); bumped on breaking changes. |
| `plugin` / `plugin_version` | string | Producer identity. |
| `document` | object | Document name/path, fps, frame, time (see below). |
| `controller` | object | Relativity Controller state, or `{"present": false}`. |
| `camera` | object | Active relativistic camera state, or `{"present": false}`. |
| `objects` | array | One entry per relativistic object. |
| `approximation_notes` | array[string] | Standing caveats about the values. |

### `document`
| Key | Type | Meaning |
|---|---|---|
| `name` | string\|null | Document name. |
| `path` | string\|null | Document folder. |
| `fps` | int\|null | Frames per second. |
| `frame` | int\|null | Current frame. |
| `time_seconds` | float\|null | Current time in seconds. |

### `controller` (when `present`)
| Key | Type | Meaning |
|---|---|---|
| `present` | bool | `true` if a controller exists. |
| `name` | string | Object name. |
| `guid` | int\|null | `BaseList2D.GetGUID()` (stable per object in the doc). |
| `position` | [x,y,z]\|null | World position. |
| `settings` | object | Controller User Data, keyed by **display name** (e.g. `"Artificial Speed of Light"`, `"Global Beta Override"`, `"Doppler Strength"`, ...). |

### `camera` (when `present`)
| Key | Type | Meaning |
|---|---|---|
| `present` | bool | `true` if a relativistic camera exists. |
| `name` / `guid` / `position` | | As above. |
| `settings` | object | Camera User Data (`"ORC Enabled"`, `"Observer Beta"`, `"Observer Velocity"` as `[x,y,z]`, ...). |
| `observer_beta` | float\|null | Resolved observer beta (`camera_tools.compute_observer_beta`). |

### `objects[]`
| Key | Type | Meaning |
|---|---|---|
| `name` | string | Object name. |
| `guid` | int\|null | Object GUID. |
| `position` | [x,y,z]\|null | World position. |
| `velocity` | [vx,vy,vz] | Object velocity (scene units/second). |
| `settings` | object | Object User Data (display-name keys). |
| `beta` | float\|null | Effective `v/c` (object/global). |
| `cos_theta` | float\|null | Cosine to the observer (`+1` approaching, `-1` receding). |
| `doppler_factor` | float\|null | Doppler factor (`<1` blue, `>1` red). |
| `searchlight_multiplier` | float\|null | Beaming intensity multiplier. |

Computed factors are `null` if they could not be evaluated for an object.

## Example (empty scene skeleton)

```json
{
  "schema": "openrelativity_c4d.metadata",
  "schema_version": 1,
  "plugin": "OpenRelativity C4D",
  "plugin_version": "0.1.0",
  "document": {"name": null, "path": null, "fps": null, "frame": null, "time_seconds": null},
  "controller": {"present": false},
  "camera": {"present": false},
  "objects": [],
  "approximation_notes": ["..."]
}
```

A populated object entry looks like:

```json
{
  "name": "ORC_Test_Approaching",
  "guid": 1234567,
  "position": [-300.0, 160.0, 0.0],
  "velocity": [0.0, 0.0, -600.0],
  "settings": {"ORC Object Enabled": true, "Object Beta": 0.0, "Velocity Z": -600.0, "...": "..."},
  "beta": 0.6,
  "cos_theta": 1.0,
  "doppler_factor": 0.5,
  "searchlight_multiplier": 8.0
}
```

## Use cases

- **Octane render + external compositing** - drive comp grades from `beta` /
  `doppler_factor` / `searchlight_multiplier` per object (see
  [`AOV_PIPELINE.md`](AOV_PIPELINE.md)).
- **Future RelativityRender bridge** - a stable, documented hand-off of scene
  state to an external relativistic renderer.
- **Debugging** - inspect exactly what the plugin computed for each object.
- **Reproducibility** - capture the relativistic state alongside a render.

## Compatibility & limitations

- **No external dependencies** (standard-library JSON).
- **Single frame per file** - export per frame for sequences.
- `settings` keys mirror the C4D **User Data display names** (spaces included) for
  fidelity; the normalized physics values are the typed fields above.
- Values are **approximations** (per-object, pivot-based; the camera's velocity is
  not yet folded into a relative beta), consistent with the previews.
- `schema_version` will increase on breaking changes; consumers should check it.
