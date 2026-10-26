import contextlib
import io
import json
import sys
import unittest
from unittest.mock import patch

from itol_cli.backends import run_pyitol
from itol_cli.cli import main
from itol_cli.core import ItolError


class BackendTests(unittest.TestCase):
    def test_knowledge_available(self):
        for topic in ("index", "formats", "styling", "api", "agent", "ecosystem"):
            with self.subTest(topic=topic), contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(main(["knowledge", topic]), 0)
                result = json.loads(out.getvalue())
                self.assertEqual(result["topic"], topic)
                self.assertTrue(result["content"])

    @unittest.skipIf(sys.version_info < (3, 10), "PyiTOL requires Python 3.10+")
    def test_dispatch_no_shell_and_exit_code(self):
        with patch("importlib.util.find_spec", return_value=object()), patch("subprocess.run") as run:
            run.return_value.returncode = 3
            result = run_pyitol(["validate", "--tree", "a tree;echo nope.nwk"])
            self.assertEqual(result, 3)
            self.assertEqual(run.call_args.args[0], [sys.executable, "-m", "pyitol", "validate", "--tree", "a tree;echo nope.nwk"])
            self.assertNotIn("shell", run.call_args.kwargs)

    def test_missing_backend(self):
        with patch("importlib.util.find_spec", return_value=None), self.assertRaises(ItolError):
            run_pyitol(["--help"])

    def test_help_passthrough(self):
        with patch("itol_cli.cli.run_pyitol", return_value=0) as run:
            self.assertEqual(main(["pyitol", "template", "--help"]), 0)
            run.assert_called_once_with(["template", "--help"])
