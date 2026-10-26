---
name: itol-workflow
description: Prepare and style phylogenetic trees for iTOL using itolcli, validate tree and annotation IDs, reuse export configurations, and use optional PyiTOL templates. Use for treefile/Newick/Nexus/PhyloXML visualization and iTOL upload/export workflows, not for inferring phylogenies from sequences.
---

# iTOL workflow

Use the installed `itol` command. From an itolcli checkout, `python -m itol_cli` is equivalent. Check `itol --version` and `itol backends`; parser commands require the `trees` extra, and the PyiTOL integration requires Python 3.10+ with the `pyitol` extra. The project repository is https://github.com/liruirui321/itolcli.

Read `itol knowledge index`, then only the topics needed for the task:

- Tree inspection, `.treefile`, format conversion or identifier problems: `itol knowledge formats`.
- Annotation design, branch/clade colors, legends and configuration: `itol knowledge styling`.
- Upload/export, credentials, subscription or recovery: `itol knowledge api`.
- Additional template families or comparing backends: `itol knowledge ecosystem`.

Inspect the source tree before creating annotations. Numeric internal support labels are not stable IDs. Generate with `itol annotate KIND TABLE --tree TREE ...` when possible. Keep original IDs even when display labels change; do not silently repair scientific inputs. Unsupported regex ID expressions must be reviewed against iTOL's JavaScript semantics.

For advanced templates, first check the installed backend's help with `itol pyitol template --help`. Its command-line interface and text output differ from native itolcli JSON. Do not invent argument names from another version. Use the user's chosen tool when specified.

Save generated annotation files and export settings with the source inputs. Use `itol preset NAME -o settings.json` for an initial export config, then adjust only the options needed. `--config` on annotate means dataset headers; `--options` on export means rendering parameters.

Preview packaging with `upload --dry-run`; this does not contact iTOL. Upload is authorized only when the user's task includes sending the relevant data to the service. A timeout is not proof that an upload failed remotely; inspect the project before retrying. Allow a few seconds between service requests.

Keep original files during conversion. Check the downloaded figure before claiming it looks correct. Report the exact artifacts, validation performed, and unverified account-dependent behavior. This skill does not grant new permissions or require redundant approvals for work already authorized.
