import argparse
import csv
import json
import os
import sys
from pathlib import Path

from . import __version__
from .client import Client, FORMATS, tree_id
from .core import ItolError, annotate, bundle, write_file

PRESETS = {
    "paper": {"display_mode": "1", "current_font_name": "Arial", "current_font_size": "14", "line_width": "2", "align_labels": "1", "label_display": "1"},
    "circular": {"display_mode": "2", "arc": "350", "rotation": "0", "current_font_size": "12", "line_width": "2", "label_display": "1"},
}


def parser():
    p = argparse.ArgumentParser(description="Unofficial iTOL workflow CLI: annotations → package → upload → export")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="command", required=True)
    a = sub.add_parser("annotate", help="Generate an iTOL annotation from CSV/TSV")
    a.add_argument("kind", choices=["colorstrip", "simplebar", "heatmap", "labels"])
    a.add_argument("input", type=Path)
    a.add_argument("--label", default="Dataset")
    a.add_argument("--color", default="#0072B2")
    a.add_argument("-o", "--output", required=True, type=Path)
    a.add_argument("--force", action="store_true")
    for command in ("pack", "upload"):
        a = sub.add_parser(command, help="Package local files" if command == "pack" else "Upload using the official batch API (subscription required)")
        a.add_argument("tree", type=Path)
        a.add_argument("-d", "--dataset", action="append", default=[], type=Path)
        if command == "pack":
            a.add_argument("-o", "--output", required=True, type=Path)
            a.add_argument("--force", action="store_true")
        else:
            a.add_argument("--project", required=True)
            a.add_argument("--name")
            a.add_argument("--description")
            a.add_argument("--dry-run", action="store_true")
            a.add_argument("--timeout", type=float, default=120)
    a = sub.add_parser("export", help="Export an existing iTOL tree")
    a.add_argument("tree_id")
    a.add_argument("--format", choices=FORMATS, default="svg")
    a.add_argument("-o", "--output", required=True, type=Path)
    a.add_argument("--preset", choices=PRESETS)
    a.add_argument("--options", type=Path, help="JSON object of official export options")
    a.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    a.add_argument("--dry-run", action="store_true")
    a.add_argument("--force", action="store_true")
    a.add_argument("--timeout", type=float, default=120)
    a = sub.add_parser("url", help="Print a tree URL")
    a.add_argument("tree_id")
    return p


def export_options(args):
    options = dict(PRESETS.get(args.preset, {}))
    if args.options:
        loaded = json.loads(args.options.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict) or not all(isinstance(k, str) and isinstance(v, (str, int, float)) and not isinstance(v, bool) for k, v in loaded.items()):
            raise ItolError("Options must be a JSON object with string/number values")
        options.update({k: str(v) for k, v in loaded.items()})
    for pair in args.set:
        key, sep, value = pair.partition("=")
        if not sep or not key or not value:
            raise ItolError("--set requires KEY=VALUE")
        options[key] = value
    if {"tree", "format", "APIkey"} & options.keys():
        raise ItolError("Options cannot override tree, format or APIkey")
    return options


def run(args):
    if args.command == "url":
        return {"url": "https://itol.embl.de/tree/" + tree_id(args.tree_id)}
    if args.command == "annotate":
        data = annotate(args.input, args.kind, args.label, args.color)
        write_file(args.output, data, args.force)
        return {"output": str(args.output), "bytes": len(data)}
    if args.command in ("pack", "upload"):
        data, names = bundle(args.tree, args.dataset)
        if args.command == "pack":
            write_file(args.output, data, args.force)
            return {"output": str(args.output), "files": names, "bytes": len(data)}
        if args.dry_run:
            return {"dry_run": True, "project": args.project, "files": names, "bytes": len(data), "requires": "Standard subscription and ITOL_API_KEY"}
        result = Client(args.timeout).upload(data, os.environ.get("ITOL_API_KEY", ""), args.project, args.name, args.description)
        return result
    if args.command == "export":
        identifier = tree_id(args.tree_id)
        options = export_options(args)
        if args.dry_run:
            return {"dry_run": True, "tree": identifier, "format": args.format, "options": options}
        if args.output.exists() and not args.force:
            raise ItolError("Output exists; use --force to replace it")
        data = Client(args.timeout).export(identifier, args.format, options)
        write_file(args.output, data, args.force)
        return {"output": str(args.output), "bytes": len(data), "tree_id": identifier}


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        result = run(args)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, OSError, UnicodeError, csv.Error) as error:
        message = str(error)
        secret = os.environ.get("ITOL_API_KEY")
        if secret:
            message = message.replace(secret, "[REDACTED]")
        print("itol: " + message, file=sys.stderr)
        return 1
