# iTOL workflow knowledge

Maintained with itolcli 0.2.0. Sources checked 2026-10-26. These are operational notes, not a mirror of the entire iTOL manual.

Run `itol knowledge TOPIC` for JSON containing the corresponding Markdown:

- `formats`: treefile/Newick, Nexus, PhyloXML; parsing and conversion boundaries.
- `styling`: choosing annotation layers, style options and repeatable export settings.
- `api`: official upload/export contracts, subscription requirements and failure recovery.
- `agent`: a practical workflow and honest capability boundaries for assistants.
- `ecosystem`: comparable projects and optional PyiTOL integration.

Native commands return JSON on stdout, diagnostics on stderr, and nonzero exit codes on failure. `itol pyitol ...` intentionally preserves PyiTOL's own output and exit codes. Do not parse it as our JSON protocol.

Start with `itol --help`, `itol backends` and `itol tree inspect INPUT`.
