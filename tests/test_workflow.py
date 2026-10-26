import contextlib
import io
import json
import tempfile
import unittest
import urllib.error
import zipfile
from pathlib import Path
from unittest.mock import patch

from itol_cli.cli import main
from itol_cli.client import Client, check_export, parse_upload, tree_id
from itol_cli.core import ItolError, annotate, bundle, write_file

ROOT = Path(__file__).resolve().parents[1]


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)

    def input(self, text):
        path = self.path / "data.tsv"
        path.write_text(text)
        return path

    def test_annotations(self):
        for kind, file, expected in [("colorstrip", "groups.tsv", "LEGEND_COLORS\t#009E73\t#D55E00"), ("simplebar", "abundance.tsv", "Human\t15"), ("heatmap", "expression.tsv", "Rice\t2.5\tX"), ("labels", "labels.tsv", "LABELS\nSEPARATOR TAB\nDATA")]:
            with self.subTest(kind=kind):
                self.assertIn(expected, annotate(ROOT / "examples" / file, kind, "Test").decode())

    def test_bad_data(self):
        for body in ["id\tvalue\na\tNaN\n", "id\tvalue\na\tinf\n", "id\tvalue\na\t1\na\t2\n", "id\tvalue\na\t\n", "id\tvalue\na\t1\textra\n", "id\tvalue\n#a\t1\n"]:
            with self.subTest(body=body), self.assertRaises(ItolError):
                annotate(self.input(body), "simplebar", "test")

    def test_csv_quotes_unicode(self):
        path = self.path / "data.csv"
        path.write_text('id,label\nA,"水稻, rice"\n', encoding="utf-8-sig")
        self.assertIn("A\t水稻, rice", annotate(path, "labels", "Labels").decode())

    def test_conflicting_legend(self):
        with self.assertRaises(ItolError):
            annotate(self.input("id\tcolor\tlabel\na\t#000000\tX\nb\t#FFFFFF\tX\n"), "colorstrip", "test")

    def test_pack_deterministic_and_ordered(self):
        tree = ROOT / "examples/demo.tree"
        dataset = self.input("LABELS\nSEPARATOR TAB\nDATA\na\tA\n")
        data, names = bundle(tree, [dataset])
        self.assertEqual(data, bundle(tree, [dataset])[0])
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            self.assertEqual(names, ["tree.tree", "0001_dataset.txt"])
            self.assertEqual(archive.read("tree.tree"), tree.read_bytes())
        with self.assertRaises(ItolError):
            bundle(tree, [tree])

    def test_no_overwrite(self):
        path = self.path / "result.svg"
        write_file(path, b"old")
        with self.assertRaises(FileExistsError):
            write_file(path, b"new")
        self.assertEqual(path.read_bytes(), b"old")
        write_file(path, b"new", force=True)
        self.assertEqual(path.read_bytes(), b"new")

    def test_upload_responses(self):
        self.assertEqual(parse_upload(b"warning\nSUCCESS: 12345\n")["warnings"], ["warning"])
        for data in [b"ERR 1 invalid key", b"", b"<html>oops</html>", b"SUCCESS: 123\nERR 2"]:
            with self.assertRaises(ItolError):
                parse_upload(data)

    def test_export_response_validation(self):
        for fmt, data in [("svg", b'<svg xmlns="http://www.w3.org/2000/svg"/>'), ("png", b"\x89PNG\r\n\x1a\nrest"), ("pdf", b"%PDF-1.4"), ("newick", b"(A,B);"), ("nexus", b"#NEXUS\n"), ("eps", b"%!PS-Adobe-3.0 EPSF-3.0"), ("phyloxml", b"<phyloxml/>")]:
            with self.subTest(fmt=fmt):
                check_export(data, "application/octet-stream", fmt)
                with self.assertRaises(ItolError):
                    check_export(b"<html>Error</html>", "text/html", fmt)
        with self.assertRaises(ItolError):
            check_export(b"SUCCESS", "text/plain", "pdf")

    def test_upload_multipart(self):
        with patch.object(Client, "request", return_value=(b"SUCCESS: 123", "text/plain")) as request:
            self.assertEqual(Client().upload(b"ZIPBYTES", "SECRET", "project")["tree_id"], "123")
            endpoint, body, mime = request.call_args.args
            self.assertEqual(endpoint, "/batch_uploader.cgi")
            for value in [b'name="APIkey"', b'name="projectName"', b'name="zipFile"', b"ZIPBYTES"]:
                self.assertIn(value, body)
            self.assertIn("multipart/form-data; boundary=", mime)

    def test_export_form(self):
        with patch.object(Client, "request", return_value=(b"<svg/>", "image/svg+xml")) as request:
            Client().export("123", "svg", {"display_mode": "2"})
            self.assertIn(b"display_mode=2", request.call_args.args[1])
            self.assertIn(b"tree=123", request.call_args.args[1])

    def test_network_errors_not_retried(self):
        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("unavailable")) as request:
            with self.assertRaises(ItolError):
                Client().export("123", "svg", {})
            self.assertEqual(request.call_count, 1)

    def test_cli_dry_run_no_network(self):
        with patch("urllib.request.urlopen") as network, contextlib.redirect_stdout(io.StringIO()) as out:
            status = main(["upload", str(ROOT / "examples/demo.tree"), "--project", "demo", "--dry-run"])
            self.assertEqual(status, 0)
            self.assertTrue(json.loads(out.getvalue())["dry_run"])
            network.assert_not_called()

    def test_cli_malformed_json(self):
        file = self.input("invalid json")
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["export", "123", "-o", str(self.path / "x.svg"), "--options", str(file)]), 1)

    def test_secret_redaction(self):
        with patch.object(Client, "request", return_value=(b"ERR SECRET", "text/plain")):
            with self.assertRaises(ItolError) as error:
                Client().upload(b"zip", "SECRET", "demo")
            self.assertNotIn("SECRET", str(error.exception))
        with patch.object(Client, "request", return_value=(b"Warning: SECRET\nSUCCESS: 123", "text/plain")):
            self.assertNotIn("SECRET", json.dumps(Client().upload(b"zip", "SECRET", "demo")))

    def test_id_validation(self):
        self.assertEqual(tree_id("https://itol.embl.de/tree/123"), "123")
        with self.assertRaises(ItolError):
            tree_id("https://other.example/tree/123")


if __name__ == "__main__":
    unittest.main()
