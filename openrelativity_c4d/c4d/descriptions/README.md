# `descriptions` - Cinema 4D resource files

Holds Cinema 4D **description resources** for the tags / objects / scene hook
added in later phases:

- `*.res` - parameter layout definitions,
- `c4d_symbols.h` / per-description `.h` - symbol id headers,
- `strings_xx/` - localized parameter labels.

This format is shared with the Cinema 4D **C++ SDK**, so resources written here
carry over to a future C++ migration unchanged.

> Empty for now (Phase 1). The "About" command needs no description resource.
