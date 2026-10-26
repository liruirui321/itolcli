# Validation evidence

Recorded 2026-10-26 for itolcli 0.2.0.

## Local checks

- Python 3.12.13, Biopython 1.88: 31 automated tests passed, no skips.
- Python 3.9.6 without optional dependencies: native/core tests passed; 10 optional parser/PyiTOL checks skipped as expected.
- Built and installed the wheel. Ran `itol --version`, `itol backends` and `itol knowledge index` from outside the checkout, verifying that packaged knowledge is available after installation.
- Native examples produced color strips, bars, heatmaps, labels, branch styles and ranges; tree/style IDs matched the four-tip demonstration tree.
- Converted the demonstration tree to PhyloXML; automated tests cover Newick/Nexus/PhyloXML conversion, Nexus TRANSLATE, multi-tree selection, quoted labels, NHX names, malformed input and ambiguous IDs.
- Deterministic ZIP packing, non-overwrite behavior, upload/export dry runs and redaction were tested. Network contracts are mocked, not live service success.
- Skill passed the skill-creator frontmatter/naming/scaffold validator.

## Actual optional-backend smoke test

Installed PyPI `pyitol==1.0.3` in the same environment. Ran version/help through the `itol pyitol` bridge, then generated a gradient dataset:

```sh
itol pyitol template create gradient \
  --taxonomy examples/abundance.tsv --tree examples/demo.tree \
  --column value --label Abundance --output output/gradient.txt
itol tree validate examples/demo.tree -d output/gradient.txt
```

Generation succeeded and all four rows matched the original tree. This version's gradient command requires **all three** of `--taxonomy`, `--tree` and `--column`; omitting the tree returns failure. Avoid `--quiet` when diagnosing upstream failures because it can suppress useful error text.

This is a real local subprocess integration test, not a mocked backend invocation. It does not validate every PyiTOL template or its online account operations.

## Remote checks and remaining boundary

The initial repository commit passed GitHub Actions on Python 3.9/3.12/3.13. Later commits' exact results are visible in the [Actions history](https://github.com/liruirui321/itolcli/actions); CI installs the tree extra for parser coverage.

Successful authenticated upload, remote annotation rendering and upload-to-export round trip remain unverified because no iTOL account/API key has been supplied for this task. No claim of publication-ready visual quality or complete browser feature parity is made. These account-dependent checks remain the next acceptance milestone.
