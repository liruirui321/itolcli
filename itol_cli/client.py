import re
import math
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import xml.etree.ElementTree as ET

from .core import ItolError
from . import __version__

BASE_URL = "https://itol.embl.de"
FORMATS = ("svg", "pdf", "png", "eps", "newick", "nexus", "phyloxml")


def tree_id(value):
    if value.startswith("https://itol.embl.de/tree/"):
        value = value.removeprefix("https://itol.embl.de/tree/").rstrip("/")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", value):
        raise ItolError("Expected an iTOL tree ID or https://itol.embl.de/tree/ID URL")
    return value


def parse_upload(data):
    lines = data.decode("utf-8", errors="replace").strip().splitlines()
    if not lines or not re.fullmatch(r"SUCCESS:\s+\S+", lines[-1]):
        raise ItolError("iTOL upload failed: " + " ".join(lines)[:400])
    result = tree_id(lines[-1].split()[-1])
    return {"tree_id": result, "url": BASE_URL + "/tree/" + result, "warnings": lines[:-1]}


def check_export(data, content_type, fmt):
    head = data.lstrip()
    if not head or "text/html" in content_type.lower() or head.lower().startswith((b"<!doctype html", b"<html", b"err")):
        raise ItolError("iTOL returned an error instead of an export: " + head[:250].decode("utf-8", errors="replace"))
    valid = False
    if fmt in ("svg", "phyloxml"):
        try:
            root = ET.fromstring(data)
            valid = root.tag.split("}")[-1].lower() == fmt
        except ET.ParseError:
            pass
    elif fmt == "pdf":
        valid = head.startswith(b"%PDF-")
    elif fmt == "png":
        valid = data.startswith(b"\x89PNG\r\n\x1a\n")
    elif fmt == "eps":
        valid = head.startswith(b"%!PS-Adobe")
    elif fmt == "nexus":
        valid = head.upper().startswith(b"#NEXUS")
    elif fmt == "newick":
        valid = head.endswith(b";") and b"(" in head and b")" in head
    if not valid:
        raise ItolError("Response does not match requested format: " + fmt)


class Client:
    def __init__(self, timeout=120):
        if not math.isfinite(timeout) or timeout <= 0:
            raise ItolError("Timeout must be positive")
        self.timeout = timeout
        self.last_request = None

    def request(self, endpoint, data, content_type):
        if self.last_request is not None:
            time.sleep(max(0, 3 - (time.monotonic() - self.last_request)))
        request = urllib.request.Request(BASE_URL + endpoint, data=data, headers={"Content-Type": content_type, "User-Agent": "itol-workflow-cli/" + __version__})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return response.read(), response.headers.get("Content-Type", "")
        except urllib.error.HTTPError as error:
            raise ItolError(f"iTOL HTTP error {error.code}; request was not retried") from None
        except (urllib.error.URLError, socket.timeout, TimeoutError) as error:
            raise ItolError("iTOL connection failed; request was not retried. If uploading, check your project before retrying") from error
        finally:
            self.last_request = time.monotonic()

    def upload(self, archive, api_key, project, name=None, description=None):
        if not api_key or not project.strip():
            raise ItolError("Upload requires ITOL_API_KEY and --project (active Standard subscription)")
        boundary = uuid.uuid4().hex
        fields = {"APIkey": api_key, "projectName": project}
        if name:
            fields["treeName"] = name
        if description:
            fields["treeDescription"] = description
        parts = []
        for key, value in fields.items():
            parts.append((f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n').encode())
        parts.append((f'--{boundary}\r\nContent-Disposition: form-data; name="zipFile"; filename="upload.zip"\r\nContent-Type: application/zip\r\n\r\n').encode() + archive + b"\r\n")
        parts.append(f"--{boundary}--\r\n".encode())
        data, _ = self.request("/batch_uploader.cgi", b"".join(parts), "multipart/form-data; boundary=" + boundary)
        try:
            result = parse_upload(data)
            result["warnings"] = [warning.replace(api_key, "[REDACTED]") for warning in result["warnings"]]
            return result
        except ItolError as error:
            raise ItolError(str(error).replace(api_key, "[REDACTED]")) from None

    def export(self, identifier, fmt, options):
        if fmt not in FORMATS:
            raise ItolError("Unsupported export format: " + fmt)
        if {"tree", "format", "APIkey"} & options.keys():
            raise ItolError("Export options cannot override tree, format or APIkey")
        params = {**options, "tree": tree_id(identifier), "format": fmt}
        data, content_type = self.request("/batch_downloader.cgi", urllib.parse.urlencode(params).encode(), "application/x-www-form-urlencoded")
        check_export(data, content_type, fmt)
        return data
