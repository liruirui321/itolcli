# Reproducible tree styling

Choose visual encodings according to the data: categorical groups → color strips; a single measurement → bars; multiple comparable measurements → heatmap. Branch styles and clade background ranges are different annotation operations. Avoid making one color mean different groups in different layers.

Native generators:

| Kind | Exact table columns | Use |
| --- | --- | --- |
| colorstrip | id, color, label | Group strip and legend |
| simplebar | id, value | One numeric track |
| heatmap | id, named numeric columns | Matrix; X means missing |
| labels | id, label | Display labels, keeping original IDs |
| treecolors | id, type, color, style, size | branch/clade normal or dashed; label normal/bold/italic/bold-italic |
| ranges | id, color, label | TREE_COLORS colored range |

Tables are CSV or TSV; all generators emit TAB annotations. Colors use #RRGGBB. `size` is a positive scale factor. Multiple style rows may target one node if `type` differs.

Dataset header configuration is separate from export configuration:

```sh
itol annotate colorstrip groups.tsv --label Groups --tree input.treefile \
  --config strip.json -o output/groups.txt
itol preset paper -o output/export.json
itol export TREE_ID --options output/export.json \
  --set datasets_visible=0,1 --format svg -o output/tree.svg
```

`strip.json` may contain `{"STRIP_WIDTH": 25, "MARGIN": 5, "COLOR_BRANCHES": 1}`. These are dataset settings. Native configuration checks keys/shape and prevents overwriting structural headers, but does not know every iTOL option's valid range. Verify advanced settings against the relevant official template.

Export presets `paper`, `circular`, `unrooted` are starting points. Preset values are overridden by the JSON export file, then by `--set KEY=VALUE`. Explicitly set `datasets_visible` when needed; indexes refer to actual dataset tracks, not every annotation file (LABELS/TREE_COLORS are not dataset tracks). Save the source tree, input tables, annotation files and export config together to reproduce a figure.

Show branch lengths when biologically meaningful; changing `ignore_branch_length` changes visual interpretation. A bootstrap threshold depends on how support was computed, so do not invent a universal threshold. SVG/PDF suit further editing; inspect the exported figure for clipped labels and unreadable legends. The CLI does not automatically judge visual quality.

Sources: official [color strips](https://itol.embl.de/help/dataset_color_strip_template.txt), [bars](https://itol.embl.de/help/dataset_simplebar_template.txt), [heatmaps](https://itol.embl.de/help/dataset_heatmap_template.txt), [labels](https://itol.embl.de/help/labels_template.txt), [tree colors](https://itol.embl.de/help/colors_styles_template.txt).
