# Related tools and reuse

Research snapshot: 2026-10-26. Capabilities below come from project documentation/source inspection, not a comparative benchmark. GitHub `pushed_at` is repository activity, not a guarantee of compatibility, support or scientific correctness.

| Project | Interface and useful scope | Last push observed | License metadata |
| --- | --- | --- | --- |
| [PyiTOL](https://github.com/ZengZichao/PyiTOL) | Python CLI; many annotation templates, configuration, taxonomy, upload/export | 2026-10-23 | MIT |
| [itolapi](https://github.com/albertyw/itolapi) | Python API and basic shell scripts for upload/export | 2026-10-24 | MIT |
| [table2itol](https://github.com/mgoeker/table2itol) | R script; spreadsheet/CSV to annotations, data-driven visualization selection | 2020-05-15 | GPL-3.0 |
| [Gotree](https://github.com/evolbioinfo/gotree) | Go CLI; tree manipulation, local drawing, `upload itol` / `download itol` | 2026-08-20 | GPL-2.0 |
| [itol.toolkit](https://github.com/TongZhou2017/itol.toolkit) | R package for annotation generation; functions rather than a standalone Python CLI | 2025-11-02 | DESCRIPTION declares MIT + file LICENSE (API metadata was NOASSERTION) |
| [iBiology/iTOL](https://github.com/iBiology/iTOL) | Earlier Python API/CLI with annotation support | 2020-08-28 | MIT |

PyiTOL is the closest functional match to the requested automation, and deserves evaluation before writing additional template generators. itolapi's README still contains an old deprecation announcement, but the observed repository had recent pushes; do not label it abandoned from that notice alone. table2itol is useful in an existing R/table workflow. Gotree is useful for tree manipulation and local rendering beyond iTOL-specific styling.

## Integration in this project

- Biopython is an optional parser dependency behind `.[trees]`, reusing Bio.Phylo for Newick/Nexus/PhyloXML instead of maintaining a separate general tree parser.
- PyiTOL is an optional pinned dependency behind `.[pyitol]` or `.[all]` (Python 3.10+). Native `itol pyitol ...` dispatches to `python -m pyitol` in the same environment without a shell. Upstream output and exit codes are preserved.
- No source from the listed GPL projects has been copied into this MIT repository. Public visibility alone is not a reuse license. Dependencies and provenance are documented in THIRD_PARTY.md.

```sh
python -m pip install ".[all]"
itol backends
itol pyitol --version
itol pyitol template --help
itol pyitol validate --help
```

Verified with 1.0.3: `itol pyitol template create gradient --taxonomy examples/abundance.tsv --tree examples/demo.tree --column value --label Abundance --output output/gradient.txt`. All three inputs (`--taxonomy`, `--tree`, `--column`) are required for that operation. For failures, omit upstream `--quiet` so diagnostic text remains visible.

The tested optional version is pyitol 1.0.3. The GitHub main branch may have features newer than that release; read installed help rather than assuming README examples match every release. An installed backend is not proof that its account-dependent operations have been tested. Native itolcli keeps its own input checks, JSON output, optional-dependency boundaries and knowledge/skill package; it does not claim all PyiTOL features as native implementations.
