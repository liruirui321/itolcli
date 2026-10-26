# itolcli

A small, unofficial command-line workflow for [iTOL (Interactive Tree Of Life)](https://itol.embl.de/): generate annotations, package inputs, upload a tree, and export figures with reproducible settings.

Python 3.9+; no runtime dependencies. This project is not affiliated with iTOL or EMBL. It prepares annotations and calls iTOL's renderer; it does not infer phylogenies or render trees locally.

## Install

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
itol --help
```

Without installation, run `python3 -m itol_cli` from this repository in place of `itol`.

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

Duplicate IDs, empty cells, wrong column counts and embedded tabs/newlines are rejected. IDs must match your tree; **this version does not parse trees or verify node membership**. Branch annotations using iTOL's ancestor ID syntax may be supplied as IDs.

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

Advanced keys pass through to the [documented export options](https://itol.embl.de/help.cgi#batch); the CLI does not validate every upstream option. Reserved keys `tree`, `format` and `APIkey` cannot be overridden. Export responses are checked for error pages and file format signatures before writing; this is not full binary-file integrity validation.

Network commands accept `--timeout` (seconds, default 120). Allow at least a few seconds between CLI invocations in your own loops, as requested by iTOL. The client also spaces repeated requests within one client instance by three seconds.

## Status and tests

Version 0.1.0 is an initial implementation. Offline examples and 15 automated tests pass locally. Tests cover generated annotations, malformed inputs, deterministic ZIP packaging, upload response parsing, multipart fields, export request fields, error responses, credential redaction and overwrite protection. HTTP behavior is mocked in the automated suite. **A successful authenticated upload and upload-to-export round trip have not yet been verified with an iTOL account.**

```sh
python3 -m unittest discover -s tests -v
```

See [the research and project brief](docs/PROJECT.md) for scope and the next acceptance milestone.

## 中文说明

首版提供四类注释生成、离线打包、官方接口上传，以及可复用配置的图片导出。自动上传需要 iTOL 标准订阅及 API key；没有订阅时仍可离线生成注释，再到网页手动使用。当前尚未完成真实账户的上传与导出闭环验收，也不检查注释 ID 是否存在于树中。详见[调研与立项说明](docs/PROJECT.md)。

## License

MIT. iTOL itself remains a separate service subject to its own terms and subscription requirements.
