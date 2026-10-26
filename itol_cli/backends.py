"""Optional upstream CLI integration without vendoring or shell interpolation."""
import importlib.metadata
import importlib.util
import subprocess
import sys

from .core import ItolError


def status():
    result = {}
    for distribution in ("biopython", "pyitol"):
        try:
            result[distribution] = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            result[distribution] = None
    return {"python": sys.version.split()[0], "optional_backends": result}


def run_pyitol(arguments):
    if sys.version_info < (3, 10):
        raise ItolError("PyiTOL integration requires Python 3.10+")
    if importlib.util.find_spec("pyitol") is None:
        raise ItolError('Install the optional backend with pip install ".[pyitol]" from the repository')
    # Upstream stdout/stderr and exit codes are intentionally preserved.
    return subprocess.run([sys.executable, "-m", "pyitol", *arguments], check=False).returncode
