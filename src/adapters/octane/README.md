# `adapters/octane` — optional Octane integration (isolated)

The **only** place allowed to import an Octane module, and only via a soft
`try/except`. If Octane is absent, every operation is a safe no-op and the rest
of the plugin is unaffected — the core plugin **must import and run without
Octane installed**.

Planned interface (see [`../../../docs/ARCHITECTURE.md`](../../../docs/ARCHITECTURE.md) §6):

- `is_available()` — whether an Octane integration was detected.
- `apply_doppler(material, color, intensity)` — mirror the per-object Doppler /
  searchlight result onto Octane material nodes (e.g. diffuse/emission color and
  power).

Phase 1 ships **stubs** (detection + no-op). Real node mapping arrives in
Phase 3 (see [`../../../docs/ROADMAP.md`](../../../docs/ROADMAP.md)).

> **No code yet (Phase 0).** This stub documents intent only.
