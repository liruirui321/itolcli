# itolcli

A small, unofficial command-line workflow for [iTOL (Interactive Tree Of Life)](https://itol.embl.de/): generate annotations, package inputs, upload a tree, and export figures with reproducible settings.

Python 3.9+ for the native CLI; Python 3.10+ for the optional PyiTOL backend. This project is not affiliated with iTOL or EMBL. It prepares annotations and calls iTOL's renderer; it does not infer phylogenies or render trees locally.

## Install

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
itol --help
```

Clone this repository first with `git clone https://github.com/liruirui321/itolcli.git` and enter `itolcli`. The distribution name `itol-workflow-cli` has not been published to PyPI; install from the checkout, not by an unqualified PyPI package name.

Without installation, run `python3 -m itol_cli` from this repository in place of `itol`.

Install `".[trees]"` for Biopython-backed tree parsing, or `".[all]"` on Python 3.10+ for parsing and PyiTOL advanced templates. The base package has no runtime dependencies. `itol backends` reports installed versions. Optional PyiTOL is pinned to 1.0.3; the current upstream main branch can differ.

## Tree files, configuration and Agent skills

```sh
itol tree inspect input.treefile
itol tree convert input.treefile --to nexus -o output/tree.nex
itol tree validate input.treefile -d output/groups.txt
itol annotate colorstrip examples/groups.tsv --label Groups \
  --tree examples/demo.tree --config examples/strip.json -o output/groups.txt
itol preset circular -o output/export.json
itol knowledge formats
itol knowledge styling
itol pyitol template --help
```

Local parsing supports Newick (including IQ-TREE `.treefile`), Nexus and PhyloXML. The extension `TriFile` is not implemented as a distinct format. Multiple trees can be inspected/converted; `--index 0` selects the first for conversion. Conversion can lose format-specific metadata, so keep originals.

`--tree` validates generated annotation IDs against one parsed tree. Direct IDs and two-tip ancestor expressions are supported; regex matching is explicitly unsupported locally. `--config` customizes dataset headers; `--options` customizes exports. These are separate JSON objects.

The [portable skill](skills/itol-workflow/SKILL.md) teaches an existing Agent how to use the CLI and its knowledge. To use it with Codex, copy the `skills/itol-workflow` folder into your Codex skills directory after installing the CLI. This is an instruction package, not a new autonomous Agent server. Knowledge ships inside the Python package and is accessible offline through `itol knowledge`.

The [related tools research](docs/RELATED_TOOLS.md) explains why we reuse Biopython and expose PyiTOL instead of recreating all their functionality. `itol pyitol ...` preserves upstream console output and exit codes, unlike native commands' JSON output. See [third-party provenance](THIRD_PARTY.md).

## Offline example

```sh
itol annotate colorstrip examples/groups.tsv --label Groups -o output/groups.txt
itol annotate simplebar examples/abundance.tsv --label Abundance -o output/abundance.txt
itol annotate heatmap examples/expression.tsv --label Expression -o output/expression.txt
itol annotate labels examples/labels.tsv -o output/labels.txt
itol pack examples/demo.tree \
  -d output/groups.txt -d output/abundance.txt \
  -d output/expression.txt -d output/labels.txt \
  -o output/demo.zip
```

The example tree is synthetic demonstration data, not an inferred biological result. Generated files can also be used manually: upload `examples/demo.tree` through the iTOL website, then drop the annotation `.txt` files onto the tree. The ZIP is intended for the batch upload API.

Existing outputs are protected; use `--force` to replace them.

## Input tables

UTF-8 CSV (`.csv`, comma-separated) or TSV (all other extensions). Include a header; column names and order are exact. Generated annotations use tab separators.

| Kind | Columns | Validation |
| --- | --- | --- |
| `colorstrip` | `id`, `color`, `label` | `#RRGGBB` colors; one color per legend label |
| `simplebar` | `id`, `value` | Finite numeric values |
| `heatmap` | `id`, one or more named numeric columns | Finite numbers or `X` for missing values |
| `labels` | `id`, `label` | Replacement display labels |
| `treecolors` | `id`, `type`, `color`, `style`, `size` | Branch/clade/label style and positive size factor |
| `ranges` | `id`, `color`, `label` | Colored clade/label background range |

Duplicate IDs (or duplicate ID/type pairs for `treecolors`), empty cells, wrong column counts and embedded tabs/newlines are rejected. IDs must match your tree: provide `--tree` to check them during generation, or run `tree validate` separately. Without either, tree membership is not checked.

## Upload

The [official batch uploader](https://itol.embl.de/help.cgi#batch) requires an active Standard subscription, an API key and an existing project name (case-sensitive). Keep credentials in the `ITOL_API_KEY` environment variable; do not put them in source files or commit them.

```sh
# Validate and inspect the package without credentials or network access:
itol upload examples/demo.tree -d output/groups.txt --project MyProject --dry-run

# After setting ITOL_API_KEY securely in your environment:
itol upload examples/demo.tree \
  -d output/groups.txt -d output/abundance.txt -d output/expression.txt \
  --project MyProject --name Demo > upload-result.json
```

The JSON response contains `tree_id`, `url` and any server warnings. Tree contents are preserved; packaging normalizes the tree filename to `tree.tree` (or `tree.jplace`) and numbers annotation filenames in the supplied order. QZA packaging is unsupported. Tree syntax and arbitrary prewritten annotation syntax are left to iTOL to validate.

Upload requests are **not automatically retried**. After a timeout, check the project before retrying to avoid duplicate trees.

## Export

Use an existing tree ID or an `https://itol.embl.de/tree/ID` URL. The official batch downloader does not require a subscription; the tree still needs to be available to that interface.

```sh
itol export TREE_ID --format svg --preset paper -o output/tree.svg
itol export TREE_ID --format pdf --preset circular -o output/tree.pdf
itol export TREE_ID --format svg --options examples/paper.json \
  --set current_font_size=18 -o output/custom.svg
itol export TREE_ID --preset circular -o output/check.svg --dry-run
itol url TREE_ID
```

Formats: SVG, PDF, PNG, EPS, Newick, Nexus and PhyloXML. Settings apply in order: preset → JSON options → `--set`. `paper` and `circular` are starter styles, not a guarantee of publication quality. Unspecified settings use iTOL defaults or saved tree settings. Set `datasets_visible=0,1,2` to select annotation tracks explicitly.

Advanced keys pass through to the [documented export options](https://itol.embl.de/help.cgi#batch); the CLI does not validate every upstream option. Reserved keys `tree`, `format` and `APIkey` cannot be overridden. Export responses are checked for error pages and file format signatures before writing; this is not full binary-file integrity validation. A third `unrooted` preset is available.

Network commands accept `--timeout` (seconds, default 120). Allow at least a few seconds between CLI invocations in your own loops, as requested by iTOL. The client also spaces repeated requests within one client instance by three seconds.

## Status and tests

Version 0.2.0 adds tree parsing, six native annotation generators, dataset configuration, knowledge, a portable Agent skill and optional PyiTOL integration. Tests cover generated annotations, malformed inputs, tree conversion/IDs, deterministic ZIP packaging, upload/export contracts, credential redaction and overwrite protection. HTTP behavior is mocked in the automated suite. **A successful authenticated upload and upload-to-export round trip have not yet been verified with an iTOL account.** See [validation evidence](docs/VALIDATION.md) for tested versions and commands.

```sh
python3 -m unittest discover -s tests -v
```

Install `.[trees]` to run the parser tests; they are skipped if Biopython is absent. CI includes parser tests on all configured Python versions.

See [the research and project brief](docs/PROJECT.md) for scope and the next acceptance milestone.

## 中文说明

原生能力包括六类注释、美化配置、树格式解析与转换、ID 校验、打包及官方接口上传导出。另有可选 PyiTOL 后端、离线知识库和 Agent Skill。自动上传需要 iTOL 标准订阅及 API key，真实账户上传与导出闭环尚未验收。详见[立项说明](docs/PROJECT.md)和[同类工具调研](docs/RELATED_TOOLS.md)。

## License

MIT. iTOL itself remains a separate service subject to its own terms and subscription requirements.
