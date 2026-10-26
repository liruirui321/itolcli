"""Tree inspection/conversion using Bio.Phylo, with explicit format boundaries."""
import io
import math
import re
from collections import Counter
from pathlib import Path

from .core import ItolError

TREE_FORMATS = ("newick", "nexus", "phyloxml")


def phylo():
    try:
        from Bio import Phylo
    except ImportError:
        raise ItolError('Tree parsing needs Biopython: run pip install ".[trees]" from the itolcli repository') from None
    return Phylo


def detect_format(text):
    head = text.lstrip()
    if head.upper().startswith("#NEXUS"):
        return "nexus"
    if head.startswith("<"):
        return "phyloxml"
    if head.startswith("{"):
        raise ItolError("Jplace is supported for batch packaging only, not local parsing/conversion")
    return "newick"


def check_newick(text):
    """Guard against silently accepted truncated input or invalid branch lengths."""
    tokens = []
    i = 0
    while i < len(text):
        char = text[i]
        if char == "'":
            i += 1
            while i < len(text):
                if text[i] == "'":
                    i += 1
                    if i < len(text) and text[i] == "'":
                        i += 1
                        continue
                    break
                i += 1
            else:
                raise ItolError("Unclosed quoted Newick name")
            tokens.append("NAME")
        elif char == "[":
            end = text.find("]", i + 1)
            if end < 0:
                raise ItolError("Unclosed Newick comment")
            i = end + 1
        else:
            tokens.append(char)
            i += 1
    plain = "".join(tokens).strip()
    if not plain.endswith(";"):
        raise ItolError("Newick trees must end with a semicolon")
    for match in re.finditer(r":\s*([^,();\s]+)", plain):
        try:
            valid = math.isfinite(float(match.group(1)))
        except ValueError:
            valid = False
        if not valid:
            raise ItolError("Invalid Newick branch length: " + match.group(1))
    if re.search(r":\s*[,();]|:\s*$", plain):
        raise ItolError("Missing Newick branch length")


def load_trees(path, fmt=None):
    path = Path(path)
    if path.suffix.lower() == ".qza":
        raise ItolError("Extract a plain tree from QZA with QIIME 2 first")
    text = path.read_text(encoding="utf-8-sig")
    if not text.strip():
        raise ItolError("Empty tree file")
    fmt = fmt or detect_format(text)
    if fmt not in TREE_FORMATS:
        raise ItolError("Unsupported local tree format: " + fmt)
    if fmt == "newick":
        check_newick(text)
    try:
        trees = list(phylo().parse(io.StringIO(text), fmt))
    except ItolError:
        raise
    except Exception as error:
        raise ItolError("Cannot parse " + fmt + ": " + str(error)) from None
    if not trees:
        raise ItolError("No trees found")
    for tree in trees:
        for node in tree.find_clades():
            if node.branch_length is not None and not math.isfinite(node.branch_length):
                raise ItolError("Non-finite branch length")
    return trees, fmt


def node_identifier(node):
    # iTOL uses NHX name tags as IDs. Bootstrap/confidence values are not IDs.
    comment = getattr(node, "comment", None) or ""
    match = re.search(r"(?:&&NHX:|:)name=([^:\]]+)", comment)
    return match.group(1) if match else node.name


def inspect_tree(path, fmt=None):
    trees, fmt = load_trees(path, fmt)
    result = []
    for tree in trees:
        nodes = list(tree.find_clades())
        tips = tree.get_terminals()
        ids = [node_identifier(node) for node in nodes if node_identifier(node) is not None]
        counts = Counter(ids)
        warnings = []
        duplicates = sorted(k for k, v in counts.items() if v > 1)
        if duplicates:
            warnings.append("Duplicate node IDs make annotation matching ambiguous")
        if any(node.branch_length is not None and node.branch_length < 0 for node in nodes):
            warnings.append("Negative branch lengths are present")
        if any(node.confidence is not None for node in nodes):
            warnings.append("Numeric internal labels are parsed as support, not node IDs")
        result.append({"tips": len(tips), "nodes": len(nodes), "tip_ids": [node_identifier(n) for n in tips], "internal_ids": [node_identifier(n) for n in nodes if n.clades and node_identifier(n) is not None], "duplicate_ids": duplicates, "unnamed_tips": sum(node_identifier(n) is None for n in tips), "warnings": warnings})
    return {"format": fmt, "tree_count": len(trees), "trees": result}


def annotation_ids(content):
    lines = content.decode("utf-8-sig").splitlines()
    separator = None
    active = False
    for line in lines:
        if not line.strip() or line.startswith("#"):
            continue
        if line.startswith("SEPARATOR "):
            separator = {"TAB": "\t", "COMMA": ",", "SPACE": " "}.get(line.split()[-1])
        elif line.strip() == "DATA":
            if separator is None:
                raise ItolError("Annotation needs a supported SEPARATOR before DATA")
            active = True
        elif active:
            yield line.split(separator)[0]
    if not active:
        raise ItolError("Annotation has no DATA section")


def validate_ids(tree_path, content, fmt=None):
    trees, _ = load_trees(tree_path, fmt)
    if len(trees) != 1:
        raise ItolError("ID validation requires one tree; use tree convert --index to select one")
    tree = trees[0]
    nodes = list(tree.find_clades())
    ids = [node_identifier(n) for n in nodes if node_identifier(n) is not None]
    duplicates = [k for k, v in Counter(ids).items() if v > 1]
    if duplicates or any(node_identifier(n) is None for n in tree.get_terminals()):
        raise ItolError("Tree has duplicate node IDs or unnamed tips; inspect the tree first")
    known = set(ids)
    tips = {node_identifier(n) for n in tree.get_terminals()}
    matched = 0
    missing = []
    unsupported = []
    for identifier in annotation_ids(content):
        if identifier in known:
            matched += 1
        elif identifier.startswith("CONTAINS=="):
            unsupported.append(identifier)
        else:
            parts = identifier.split("|") if "|" in identifier else identifier.split("---")
            if len(parts) == 2 and parts[0] != parts[1] and all(p in tips for p in parts):
                matched += 1
            else:
                missing.append(identifier)
    if missing or unsupported:
        raise ItolError("ID validation failed: " + repr({"unknown": missing, "unsupported_regex": unsupported}))
    return {"matched_rows": matched, "tree_tips": len(tips)}


def convert_tree(path, target, source=None, index=None):
    trees, source = load_trees(path, source)
    if index is not None:
        if index < 0 or index >= len(trees):
            raise ItolError("Tree index is out of range (zero-based)")
        trees = [trees[index]]
    output = io.StringIO()
    try:
        kwargs = {"format_branch_length": "%1.15g", "format_confidence": "%1.15g"} if target == "newick" else {}
        phylo().write(trees, output, target, **kwargs)
    except Exception as error:
        raise ItolError("Conversion failed: " + str(error)) from None
    return output.getvalue().encode(), {"source_format": source, "target_format": target, "tree_count": len(trees), "warnings": ["Conversion may change metadata, rooting declarations, comments and formatting; keep the original. Newick/Nexus cannot preserve all PhyloXML styling."]}
