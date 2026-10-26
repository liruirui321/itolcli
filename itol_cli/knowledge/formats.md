# Tree formats and identifiers

## Content, not extension

IQ-TREE's `.treefile` is a Newick maximum-likelihood tree, not a separate serialization format. `.contree`, `.nwk`, `.newick` and `.tree` frequently contain Newick as well. `TriFile` is treated here as a likely reference to `.treefile`; an unrelated format needs an actual sample/specification before support can be claimed. Source: [IQ-TREE tutorial](https://www.iqtree.org/doc/Tutorial).

Install `.[trees]` to use the Biopython-backed commands. Inspect content before producing annotations:

```sh
itol tree inspect input.treefile
itol tree inspect input.nex --input-format nexus
itol tree convert input.treefile --to phyloxml -o output/tree.xml
itol tree convert forest.nex --to newick --index 0 -o output/selected.tree
itol tree validate input.treefile -d output/groups.txt
```

Newick contains topology, optional branch lengths, node names and comments. Numeric internal labels are parsed as support values, not IDs. Names with spaces/punctuation may be quoted. IQ-TREE multi-support labels such as `95/100` remain text; do not silently interpret them as a single percentage. NHX `name` tags are recognized as annotation IDs. Annotating multiple nodes with the same ID is ambiguous and rejected by ID validation.

Nexus may contain multiple trees and a TRANSLATE block mapping numeric tokens to taxa. Inspection reports all trees; conversion preserves all unless `--index` selects one (zero-based). ID validation requires one tree. PhyloXML carries richer metadata; converting it to Newick or Nexus can lose annotations. Conversion uses Bio.Phylo writers and is not a byte-for-byte round trip. Keep original files and compare topology, IDs, support, branch lengths and metadata after conversion. Sources: [Bio.Phylo](https://biopython.org/wiki/Phylo), [Biopython tree tutorial](https://biopython.org/docs/1.85/Tutorial/chapter_phylo.html).

Jplace is passed through by batch packaging; local parsing/conversion is not implemented. QZA is not parsed or packaged by this CLI; extract a plain tree with QIIME 2 first. The iTOL website has broader import support than this wrapper.

## Annotation matching

Use original node IDs even after changing display labels. Validation handles direct IDs and two-tip ancestor expressions `A|B` / `A---B`. Regex matching (`CONTAINS==...`) is not evaluated locally: iTOL uses JavaScript regex semantics, so validation fails explicitly rather than guessing.

`tree validate` checks ID membership, not every annotation header or numerical data cell. Use `annotate` for validated table generation. Partial tip coverage is valid; missing annotation rows do not imply missing tree leaves. Source: [iTOL identifiers and annotation help](https://itol.embl.de/help.cgi#annot).
