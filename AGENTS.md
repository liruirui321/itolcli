# Working on itolcli

This is an unofficial iTOL workflow client. Keep native annotation generation and packaging usable without optional dependencies. Import Biopython/PyiTOL only on the paths that need them.

For scientific workflows, read `skills/itol-workflow/SKILL.md`; obtain format/style/API guidance through `itol knowledge TOPIC` or `itol_cli/knowledge/`. Source provenance and optional upstream integrations are documented in `THIRD_PARTY.md` and `docs/RELATED_TOOLS.md`.

Native commands return JSON on stdout and diagnostics on stderr. `itol pyitol ...` is an explicitly documented passthrough that retains upstream output and exit codes. Preserve this distinction.

Test changes with `python -m unittest discover -s tests -v` in an environment installed with `.[trees]`. Use `.[all]` on Python 3.10+ when testing the optional backend. Run offline examples and installed-package smoke checks when changing resources or CLI behavior. Do not represent mocked HTTP tests as real iTOL account acceptance.

Keep original trees intact during annotation. A visualization request does not justify modifying topology, support or scientific labels silently. Keep service credentials out of repository files and generated reports.
