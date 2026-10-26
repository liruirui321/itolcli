import csv
import io
import math
import os
import re
import tempfile
import zipfile
from pathlib import Path


class ItolError(ValueError):
    pass


def write_file(path, data, force=False):
    """Publish a complete file; never silently replace an existing result."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=path.parent, prefix=".itol-")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
        if force:
            os.replace(temp, path)
        else:
            os.link(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def cell(value):
    if not isinstance(value, str) or not value.strip() or any(c in value for c in "\t\r\n"):
        raise ItolError("Fields must be nonempty and contain no tabs or newlines")
    return value


def number(value, missing=False):
    if missing and value == "X":
        return value
    try:
        valid = math.isfinite(float(value))
    except ValueError:
        valid = False
    if not valid:
        raise ItolError("Expected a finite number, got: " + repr(value))
    return value


def color(value):
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        raise ItolError("Colors must use #RRGGBB: " + repr(value))
    return value


def annotate(path, kind, label, base_color="#0072B2", options=None):
    """TSV/CSV with explicit columns, serialized as iTOL TAB annotation."""
    cell(label)
    color(base_color)
    path = Path(path)
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, delimiter="," if path.suffix.lower() == ".csv" else "\t")
        rows = list(reader)
    if len(rows) < 2:
        raise ItolError("Input needs a header and at least one data row")
    headers = rows[0]
    if len(set(headers)) != len(headers) or not headers or headers[0] != "id":
        raise ItolError("First column must be id; column names must be unique")
    for h in headers:
        cell(h)
    expected = {"colorstrip": ["id", "color", "label"], "simplebar": ["id", "value"], "labels": ["id", "label"], "treecolors": ["id", "type", "color", "style", "size"], "ranges": ["id", "color", "label"]}
    if kind in expected and headers != expected[kind]:
        raise ItolError("Expected columns: " + ", ".join(expected[kind]))
    if kind == "heatmap" and len(headers) < 2:
        raise ItolError("Heatmap requires at least one numeric column")
    seen = set()
    data = []
    legend = {}
    for line, row in enumerate(rows[1:], 2):
        if len(row) != len(headers):
            raise ItolError("Wrong column count at row " + str(line))
        for value in row:
            cell(value)
        node = row[0]
        identity = (node, row[1]) if kind == "treecolors" else node
        if node.startswith("#") or node != node.strip() or identity in seen:
            raise ItolError("Duplicate/ambiguous node ID at row " + str(line))
        seen.add(identity)
        if kind == "colorstrip":
            color(row[1])
            if row[2] in legend and legend[row[2]].lower() != row[1].lower():
                raise ItolError("One legend label has conflicting colors: " + row[2])
            legend[row[2]] = row[1]
        elif kind in ("simplebar", "heatmap"):
            for value in row[1:]:
                number(value, missing=kind == "heatmap")
        elif kind == "treecolors":
            color(row[2])
            styles = {"branch": ("normal", "dashed"), "clade": ("normal", "dashed"), "label": ("normal", "bold", "italic", "bold-italic")}
            if row[1] not in styles or row[3] not in styles[row[1]]:
                raise ItolError("Invalid TREE_COLORS type/style")
            number(row[4])
            if float(row[4]) <= 0:
                raise ItolError("Style size factor must be positive")
        elif kind == "ranges":
            color(row[1])
            row = [row[0], "range", row[1], row[2]]
        data.append("\t".join(row))
    if kind == "labels":
        lines = ["LABELS", "SEPARATOR TAB"]
    elif kind in ("treecolors", "ranges"):
        lines = ["TREE_COLORS", "SEPARATOR TAB"]
    else:
        lines = ["DATASET_" + kind.upper(), "SEPARATOR TAB", "DATASET_LABEL\t" + label, "COLOR\t" + base_color]
    if legend:
        lines += ["LEGEND_TITLE\t" + label, "LEGEND_SHAPES\t" + "\t".join("1" for _ in legend), "LEGEND_COLORS\t" + "\t".join(legend.values()), "LEGEND_LABELS\t" + "\t".join(legend)]
    if kind == "heatmap":
        lines += ["FIELD_LABELS\t" + "\t".join(headers[1:]), "COLOR_MIN\t#FFFFFF", "COLOR_MAX\t" + base_color, "AUTO_LEGEND\t1"]
    if options:
        if kind in ("labels", "treecolors", "ranges"):
            raise ItolError("Header options apply only to dataset annotations")
        if not isinstance(options, dict):
            raise ItolError("Annotation options must be a JSON object")
        reserved = {"DATA", "SEPARATOR", "DATASET_LABEL", "COLOR", "FIELD_LABELS", "LEGEND_TITLE", "LEGEND_SHAPES", "LEGEND_COLORS", "LEGEND_LABELS"}
        for key, value in options.items():
            if not re.fullmatch(r"[A-Z][A-Z0-9_]*", key) or key in reserved or key.startswith("DATASET_"):
                raise ItolError("Reserved or invalid annotation option: " + key)
            values = value if isinstance(value, list) else [value]
            if not values or any(isinstance(v, (dict, list, bool)) or v is None for v in values):
                raise ItolError("Annotation option must be a scalar or nonempty scalar list")
            fields = [cell(str(v)) for v in values]
            lines = [line for line in lines if not line.startswith(key + "\t")]
            lines.append(key + "\t" + "\t".join(fields))
    return ("\n".join(lines + ["DATA"] + data) + "\n").encode("utf-8")


def bundle(tree, datasets):
    """Order annotation files explicitly and normalize the required tree suffix."""
    tree = Path(tree)
    if tree.suffix.lower() == ".qza":
        raise ItolError("QZA batch packaging is not supported; export a plain text tree first")
    inputs = [tree] + [Path(p) for p in datasets]
    if len({p.resolve() for p in inputs}) != len(inputs):
        raise ItolError("Tree and datasets must be distinct files")
    names = ["tree.jplace" if tree.suffix.lower() == ".jplace" else "tree.tree"]
    names += [f"{i:04d}_dataset.txt" for i in range(1, len(inputs))]
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path, name in zip(inputs, names):
            content = path.read_bytes()
            if not content.strip():
                raise ItolError("Empty input: " + str(path))
            content.decode("utf-8-sig")
            info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content)
    return output.getvalue(), names
